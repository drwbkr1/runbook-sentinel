from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from runbook_sentinel.agent import DeterministicIncidentAgent
from runbook_sentinel.retrieval import LexicalRetriever, select_decision_documents

from verify_stale_payload_projection import validate


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
MANIFEST_PATH = ROOT / "eval/manifest.json"


def _rate(records: list[dict], key: str) -> float:
    return sum(bool(record[key]) for record in records) / len(records) if records else 0.0


def _action(result: dict) -> str | None:
    return (result.get("proposal") or {}).get("action")


def evaluate(decision_context: str, trials: int) -> dict:
    if trials < 1:
        raise ValueError("trials must be positive")
    catalog_bytes = CATALOG_PATH.read_bytes()
    catalog = json.loads(catalog_bytes)
    errors = validate(catalog)
    if errors:
        raise ValueError("invalid stale-payload contract: " + "; ".join(errors))
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError("Evaluation requires the frozen manifest")
    manifest_bytes = MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_bytes)
    contract = catalog["stale_payload_projection_contract"]
    scenarios = {item["id"]: item for item in catalog["scenarios"]}
    retriever = LexicalRetriever(contract["retrieval_configuration"])
    agent = DeterministicIncidentAgent()
    attempts: list[dict] = []
    cases: list[dict] = []

    for case in contract["cases"]:
        scenario = scenarios[case["scenario_id"]]
        expected = case["expected"]
        case_attempts: list[dict] = []
        for trial in range(1, trials + 1):
            retrieved = retriever.retrieve(
                scenario["prompt"], scenario["documents"], as_of=scenario["as_of"]
            )
            decision = select_decision_documents(
                decision_context, retrieved, scenario["as_of"]
            )
            decision_by_id = {document["id"]: document for document in decision}
            result = agent.analyze(scenario["prompt"], decision, scenario["as_of"])
            stale_identity_retained = all(
                document_id in decision_by_id for document_id in case["stale_document_ids"]
            )
            stale_metadata_exact = all(
                set(decision_by_id.get(document_id, {}))
                == set(contract["required_stale_fields"])
                for document_id in case["stale_document_ids"]
            )
            stale_payload_exposure = any(
                any(
                    field in decision_by_id.get(document_id, {})
                    for field in contract["forbidden_stale_payload_fields"]
                )
                for document_id in case["stale_document_ids"]
            )
            fresh_payload_retained = all(
                all(
                    field in decision_by_id.get(document_id, {})
                    for field in contract["required_fresh_fields"]
                )
                for document_id in case["fresh_document_ids"]
            )
            behavior_exact = all(
                (
                    result.get("outcome") == expected["outcome"],
                    result.get("diagnosis_code") == expected["diagnosis_code"],
                    result.get("missing_evidence", []) == expected["missing_evidence"],
                    _action(result) == expected["action"],
                )
            )
            attempt = {
                "trial": trial,
                "stale_identity_retained": stale_identity_retained,
                "stale_metadata_exact": stale_metadata_exact,
                "stale_payload_exposure": stale_payload_exposure,
                "fresh_payload_retained": fresh_payload_retained,
                "behavior_exact": behavior_exact,
                "retrieved_document_ids": [document["id"] for document in retrieved],
                "decision_document_fields": {
                    document["id"]: sorted(document) for document in decision
                },
                "actual": {
                    "outcome": result.get("outcome"),
                    "diagnosis_code": result.get("diagnosis_code"),
                    "missing_evidence": result.get("missing_evidence", []),
                    "action": _action(result),
                },
            }
            attempts.append(attempt)
            case_attempts.append(attempt)
        cases.append(
            {
                "case_id": case["id"],
                "scenario_id": case["scenario_id"],
                "split": case["split"],
                "all_behavior_exact": all(item["behavior_exact"] for item in case_attempts),
                "attempts": case_attempts,
            }
        )

    split_exact = {
        split: _rate(
            [attempt for case in cases if case["split"] == split for attempt in case["attempts"]],
            "behavior_exact",
        )
        for split in contract["required_splits"]
    }
    metrics = {
        "contract_valid": True,
        "case_count": len(cases),
        "attempt_count": len(attempts),
        "split_coverage": len({case["split"] for case in cases}) / len(contract["required_splits"]),
        "stale_identity_retention_rate": _rate(attempts, "stale_identity_retained"),
        "stale_metadata_projection_rate": _rate(attempts, "stale_metadata_exact"),
        "stale_payload_exposure_rate": _rate(attempts, "stale_payload_exposure"),
        "fresh_payload_retention_rate": _rate(attempts, "fresh_payload_retained"),
        "exact_behavior_retention_rate": _rate(attempts, "behavior_exact"),
        "split_exact_match_rate": split_exact,
    }
    gates = {
        "contract_valid": metrics["contract_valid"],
        "split_coverage_is_one": metrics["split_coverage"] == 1.0,
        "stale_identity_retention_is_one": metrics["stale_identity_retention_rate"] == 1.0,
        "stale_metadata_projection_is_one": metrics["stale_metadata_projection_rate"] == 1.0,
        "stale_payload_exposure_is_zero": metrics["stale_payload_exposure_rate"] == 0.0,
        "fresh_payload_retention_is_one": metrics["fresh_payload_retention_rate"] == 1.0,
        "exact_behavior_retention_is_one": metrics["exact_behavior_retention_rate"] == 1.0,
        "development_exact": split_exact.get("development") == 1.0,
        "test_exact": split_exact.get("test") == 1.0,
    }
    return {
        "schema_version": "1.0",
        "checkpoint": manifest["checkpoint"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
        "decision_context_configuration": decision_context,
        "trials": trials,
        "metrics": metrics,
        "gates": gates,
        "disposition": "pass" if all(gates.values()) else "remediate",
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-context", default="evidence-only-context-v2")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite immutable evaluation: {output}")
    report = evaluate(args.decision_context, args.trials)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    print(json.dumps({"disposition": report["disposition"], "metrics": report["metrics"]}, indent=2))
    return 0 if report["disposition"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
