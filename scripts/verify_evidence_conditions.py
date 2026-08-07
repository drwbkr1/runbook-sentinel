from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
EXPECTED_CONTRACT_KEYS = {
    "schema_version",
    "allowed_conditions",
    "required_conditions_per_split",
    "required_splits",
    "definitions",
    "invariants",
}
EXPECTED_CONDITIONS = {
    "complete",
    "incomplete",
    "stale",
    "conflicting",
    "instruction_bearing",
}
PRIMARY_CONDITIONS = {"complete", "incomplete", "conflicting"}
PROJECT_EVIDENCE_KINDS = {"telemetry", "status"}
FRESHNESS_SECONDS = 3600


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if catalog.get("schema_version") != "1.8":
        errors.append("catalog schema must be 1.8")

    contract = catalog.get("evidence_condition_contract")
    if not isinstance(contract, dict) or set(contract) != EXPECTED_CONTRACT_KEYS:
        errors.append("evidence-condition contract keys do not match the frozen schema")
        contract = contract if isinstance(contract, dict) else {}
    if set(contract.get("allowed_conditions", [])) != EXPECTED_CONDITIONS:
        errors.append("allowed evidence conditions do not match the frozen taxonomy")
    if set(contract.get("required_conditions_per_split", [])) != EXPECTED_CONDITIONS:
        errors.append("every frozen condition must be required in each split")
    if set(contract.get("required_splits", [])) != {"development", "test"}:
        errors.append("required splits must be development and test")
    if set(contract.get("definitions", {})) != EXPECTED_CONDITIONS:
        errors.append("every allowed condition must have exactly one definition")

    scenarios = catalog.get("scenarios", [])
    scenario_ids = [scenario.get("id") for scenario in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("scenario IDs must be unique")

    counts_by_split: dict[str, Counter[str]] = {
        split: Counter() for split in contract.get("required_splits", [])
    }
    adversarial_by_split: Counter[str] = Counter()
    for scenario in scenarios:
        scenario_id = scenario.get("id", "<missing-id>")
        split = scenario.get("split")
        conditions = scenario.get("evidence_conditions")
        if split not in counts_by_split:
            errors.append(f"{scenario_id}: split is not allowed")
            continue
        if not isinstance(conditions, list) or not conditions:
            errors.append(f"{scenario_id}: evidence_conditions must be a non-empty list")
            continue
        if len(conditions) != len(set(conditions)):
            errors.append(f"{scenario_id}: evidence conditions must be unique")
        unknown = set(conditions) - EXPECTED_CONDITIONS
        if unknown:
            errors.append(f"{scenario_id}: unknown evidence conditions {sorted(unknown)}")
        primary = set(conditions) & PRIMARY_CONDITIONS
        if len(primary) != 1:
            errors.append(f"{scenario_id}: exactly one primary evidence condition is required")
        if "incomplete" in conditions and scenario["expected"]["outcome"] != "request_evidence":
            errors.append(f"{scenario_id}: incomplete evidence must request evidence")
        if "conflicting" in conditions and scenario["expected"]["diagnosis_code"] != "conflicting_evidence":
            errors.append(f"{scenario_id}: conflicting evidence must use the frozen conflict diagnosis")
        if "complete" in conditions and scenario["expected"]["outcome"] not in {"diagnose", "propose_action"}:
            errors.append(f"{scenario_id}: complete evidence must diagnose or propose")

        now = parse_timestamp(scenario["as_of"])
        has_stale_project_evidence = any(
            document.get("kind") in PROJECT_EVIDENCE_KINDS
            and (now - parse_timestamp(document["observed_at"])).total_seconds() > FRESHNESS_SECONDS
            for document in scenario.get("documents", [])
        )
        if has_stale_project_evidence != ("stale" in conditions):
            errors.append(f"{scenario_id}: stale label disagrees with the frozen one-hour boundary")

        has_instruction_marker = bool(
            scenario.get("attack_document_ids") or scenario.get("inband_attack_document_ids")
        )
        if has_instruction_marker != ("instruction_bearing" in conditions):
            errors.append(f"{scenario_id}: instruction-bearing label disagrees with attack-document markers")

        counts_by_split[split].update(conditions)
        if scenario.get("adversarial") is True:
            adversarial_by_split[split] += 1

    missing_pairs = [
        {"split": split, "condition": condition}
        for split in contract.get("required_splits", [])
        for condition in contract.get("required_conditions_per_split", [])
        if counts_by_split[split][condition] == 0
    ]
    if missing_pairs:
        errors.append(f"missing required condition/split pairs: {missing_pairs}")
    missing_adversarial_splits = [
        split for split in contract.get("required_splits", []) if adversarial_by_split[split] == 0
    ]
    if missing_adversarial_splits:
        errors.append(f"missing adversarial coverage in splits: {missing_adversarial_splits}")

    if errors:
        raise SystemExit(json.dumps({"status": "remediate", "errors": errors}, indent=2))
    print(
        json.dumps(
            {
                "status": "pass",
                "catalog_schema": catalog["schema_version"],
                "scenario_count": len(scenarios),
                "condition_case_count_by_split": {
                    split: dict(sorted(counts.items())) for split, counts in counts_by_split.items()
                },
                "adversarial_case_count_by_split": dict(sorted(adversarial_by_split.items())),
                "missing_condition_split_pairs": missing_pairs,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
