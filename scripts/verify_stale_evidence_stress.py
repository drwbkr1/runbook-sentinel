from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
TOKEN_RE = re.compile(r"[a-z0-9_]+")
EXPECTED_CONTRACT_KEYS = {
    "schema_version",
    "stress_type",
    "required_splits",
    "retrieval_limit",
    "prechange_retriever",
    "project_evidence_kinds",
    "freshness_seconds",
    "appended_document_count",
    "comparison_fields",
    "invariants",
    "pairs",
}
EXPECTED_PAIR_KEYS = {
    "id",
    "split",
    "control_scenario_id",
    "variant_scenario_id",
    "appended_document_ids",
    "expected_fresh_project_evidence_ids",
    "expected_relation",
}
EXPECTED_COMPARISON_FIELDS = {
    "fresh_project_evidence_recall_at_4",
    "fresh_decision_evidence_retained",
    "stale_project_evidence_saturation",
    "outcome",
    "diagnosis_code",
    "action",
    "trajectory",
    "incident_status",
    "terminal_state",
}
EXPECTED_INVARIANTS = {
    "control_documents_unchanged": True,
    "variant_appends_only_declared_stale_project_evidence": True,
    "freshness_derived_from_scenario_as_of": True,
    "unparseable_or_missing_timestamp_never_fresh": True,
    "prechange_must_drop_all_expected_fresh_project_evidence": True,
    "expected_fresh_project_evidence_recall_at_4": 1.0,
    "fresh_decision_evidence_retained": True,
    "exact_behavior_equal_to_control": True,
    "held_out_pair_not_used_for_implementation_feedback": True,
    "stress_grading_separate_from_other_metrics": True,
}
EXPECTED_RELATION = {
    "fresh_project_evidence_recall_at_4": 1.0,
    "fresh_decision_evidence_retained": True,
    "outcome": "equal",
    "diagnosis_code": "equal",
    "action": "equal",
    "trajectory": "equal",
    "incident_status": "equal",
    "terminal_state": "equal",
}


def _tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _is_fresh(document: dict, as_of: str, freshness_seconds: int) -> bool:
    try:
        age_seconds = (_parse_timestamp(as_of) - _parse_timestamp(document["observed_at"])).total_seconds()
    except (KeyError, TypeError, ValueError):
        return False
    return 0 <= age_seconds <= freshness_seconds


def _released_v2_retrieve(
    query: str, documents: list[dict], limit: int, project_kinds: set[str]
) -> list[dict]:
    query_tokens = _tokens(query)
    ranked: list[tuple[float, str, dict]] = []
    for document in documents:
        document_tokens = _tokens(document.get("content", "")) | _tokens(
            document.get("title", "")
        )
        overlap = len(query_tokens & document_tokens)
        coverage = overlap / max(1, len(query_tokens))
        kind_bonus = 0.05 if document.get("kind") == "telemetry" else 0.0
        ranked.append((coverage + kind_bonus, document["id"], document))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    eligible = [item for item in ranked if item[0] > 0]
    project_evidence = [
        item for item in eligible if item[2].get("kind") in project_kinds
    ]
    guidance = [
        item for item in eligible if item[2].get("kind") not in project_kinds
    ]
    return [document for _, _, document in (project_evidence + guidance)[:limit]]


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if catalog.get("schema_version") != "1.16":
        errors.append("catalog schema must be 1.16")
    contract = catalog.get("stale_evidence_stress_contract")
    if not isinstance(contract, dict) or set(contract) != EXPECTED_CONTRACT_KEYS:
        errors.append("stale-evidence contract keys do not match the frozen schema")
        contract = contract if isinstance(contract, dict) else {}
    if contract.get("schema_version") != "1.0":
        errors.append("stale-evidence contract schema must be 1.0")
    if contract.get("stress_type") != "stale_project_evidence_flood":
        errors.append("stress type is not exact")
    if set(contract.get("required_splits", [])) != {"development", "test"}:
        errors.append("required splits must be development and test")
    if contract.get("retrieval_limit") != 4:
        errors.append("retrieval limit must be four")
    if contract.get("prechange_retriever") != "evidence-priority-lexical-v2":
        errors.append("pre-change retriever identity is not frozen")
    project_kinds = set(contract.get("project_evidence_kinds", []))
    if project_kinds != {"telemetry", "status"}:
        errors.append("project evidence kinds are not exact")
    if contract.get("freshness_seconds") != 3600:
        errors.append("freshness boundary must remain one hour")
    if contract.get("appended_document_count") != 5:
        errors.append("each stress variant must append five documents")
    if set(contract.get("comparison_fields", [])) != EXPECTED_COMPARISON_FIELDS:
        errors.append("comparison fields are not exact")
    if contract.get("invariants") != EXPECTED_INVARIANTS:
        errors.append("stale-evidence invariants are not exact")

    scenarios = catalog.get("scenarios", [])
    scenario_by_id = {scenario["id"]: scenario for scenario in scenarios}
    terminal_by_id = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    pairs = contract.get("pairs", [])
    if not isinstance(pairs, list) or len(pairs) != 2:
        errors.append("the frozen contract must contain exactly two pairs")
        pairs = pairs if isinstance(pairs, list) else []
    pair_ids = [pair.get("id") for pair in pairs if isinstance(pair, dict)]
    if len(pair_ids) != len(set(pair_ids)):
        errors.append("stale-evidence pair IDs must be unique")

    counts_by_split: Counter[str] = Counter()
    used_scenarios: set[str] = set()
    development_observations: list[dict] = []
    held_out_contract_failures_verified = 0
    for pair in pairs:
        if not isinstance(pair, dict):
            errors.append("pair must be an object")
            continue
        pair_id = pair.get("id", "<missing-id>")
        if set(pair) != EXPECTED_PAIR_KEYS:
            errors.append(f"{pair_id}: pair keys do not match the frozen schema")
            continue
        split = pair.get("split")
        counts_by_split[split] += 1
        control_id = pair.get("control_scenario_id")
        variant_id = pair.get("variant_scenario_id")
        if control_id == variant_id or control_id in used_scenarios or variant_id in used_scenarios:
            errors.append(f"{pair_id}: control and variant identities must be unique")
        used_scenarios.update({control_id, variant_id})
        control = scenario_by_id.get(control_id)
        variant = scenario_by_id.get(variant_id)
        control_terminal = terminal_by_id.get(control_id)
        variant_terminal = terminal_by_id.get(variant_id)
        if not all(isinstance(item, dict) for item in (control, variant, control_terminal, variant_terminal)):
            errors.append(f"{pair_id}: scenario or terminal record is missing")
            continue
        if control.get("split") != split or variant.get("split") != split:
            errors.append(f"{pair_id}: split does not match its scenarios")
        for field in ("split", "domain", "as_of", "prompt", "initial_state", "expected"):
            if control.get(field) != variant.get(field):
                errors.append(f"{pair_id}: undeclared difference in {field}")
        if variant.get("adversarial") is not True:
            errors.append(f"{pair_id}: stress variant must be adversarial")
        control_conditions = set(control.get("evidence_conditions", []))
        variant_conditions = set(variant.get("evidence_conditions", []))
        if variant_conditions != control_conditions | {"stale"}:
            errors.append(f"{pair_id}: variant must add only stale")
        if variant.get("attack_document_ids") != control.get("attack_document_ids"):
            errors.append(f"{pair_id}: stale flood cannot add instruction-bearing attack markers")
        if variant.get("inband_attack_document_ids") != control.get("inband_attack_document_ids"):
            errors.append(f"{pair_id}: stale flood cannot change in-band attack markers")
        if pair.get("expected_relation") != EXPECTED_RELATION:
            errors.append(f"{pair_id}: expected relation is not exact")
        if control_terminal != variant_terminal:
            errors.append(f"{pair_id}: trajectory or terminal expectation changed")

        control_documents = control.get("documents", [])
        variant_documents = variant.get("documents", [])
        if variant_documents[: len(control_documents)] != control_documents:
            errors.append(f"{pair_id}: control documents changed or were reordered")
        appended = variant_documents[len(control_documents) :]
        appended_ids = pair.get("appended_document_ids", [])
        if len(appended) != contract.get("appended_document_count"):
            errors.append(f"{pair_id}: appended document count is not exact")
        if [document.get("id") for document in appended] != appended_ids:
            errors.append(f"{pair_id}: appended document identities or order changed")
        if len(appended_ids) != len(set(appended_ids)):
            errors.append(f"{pair_id}: appended document IDs must be unique")
        for document in appended:
            if document.get("kind") not in project_kinds:
                errors.append(f"{pair_id}: appended document is not project evidence")
            if not document.get("title") or not document.get("content"):
                errors.append(f"{pair_id}: appended document is incomplete")
            if _is_fresh(document, variant["as_of"], contract.get("freshness_seconds", 0)):
                errors.append(f"{pair_id}: appended document is not stale")
            try:
                age_seconds = (
                    _parse_timestamp(variant["as_of"])
                    - _parse_timestamp(document["observed_at"])
                ).total_seconds()
                if age_seconds <= contract.get("freshness_seconds", 0):
                    errors.append(f"{pair_id}: stale document age is not beyond the boundary")
            except (KeyError, TypeError, ValueError):
                errors.append(f"{pair_id}: frozen appended timestamp is missing or malformed")

        expected_fresh_ids = pair.get("expected_fresh_project_evidence_ids", [])
        if expected_fresh_ids != control.get("expected", {}).get("retrieval_ids"):
            errors.append(f"{pair_id}: expected fresh evidence differs from the control")
        documents_by_id = {document["id"]: document for document in variant_documents}
        if not expected_fresh_ids or any(
            documents_by_id.get(document_id, {}).get("kind") not in project_kinds
            or not _is_fresh(
                documents_by_id.get(document_id, {}),
                variant["as_of"],
                contract.get("freshness_seconds", 0),
            )
            for document_id in expected_fresh_ids
        ):
            errors.append(f"{pair_id}: expected fresh project evidence is missing or not fresh")

        prechange_documents = _released_v2_retrieve(
            variant["prompt"],
            variant_documents,
            contract.get("retrieval_limit", 0),
            project_kinds,
        )
        prechange_ids = [document["id"] for document in prechange_documents]
        retained = sorted(set(prechange_ids) & set(expected_fresh_ids))
        if retained:
            errors.append(f"{pair_id}: pre-change retriever does not demonstrate the frozen failure")
        if not set(prechange_ids).issubset(set(appended_ids)):
            errors.append(f"{pair_id}: pre-change top four are not fully consumed by stale additions")
        if any(_is_fresh(document, variant["as_of"], contract["freshness_seconds"]) for document in prechange_documents):
            errors.append(f"{pair_id}: pre-change result is not fully stale")
        if split == "development":
            development_observations.append(
                {
                    "pair_id": pair_id,
                    "retrieved_document_ids": prechange_ids,
                    "retained_fresh_project_evidence_ids": retained,
                    "fresh_project_evidence_recall_at_4": 0.0,
                    "stale_project_evidence_saturation": 1.0,
                }
            )
        elif split == "test":
            held_out_contract_failures_verified += 1

    if counts_by_split != Counter({"development": 1, "test": 1}):
        errors.append("exactly one stale-evidence pair is required per split")
    if errors:
        raise SystemExit(json.dumps({"status": "remediate", "errors": sorted(set(errors))}, indent=2))
    print(
        json.dumps(
            {
                "status": "pass",
                "catalog_schema": catalog["schema_version"],
                "stress_type": contract["stress_type"],
                "pair_count": len(pairs),
                "pair_count_by_split": dict(sorted(counts_by_split.items())),
                "retrieval_limit": contract["retrieval_limit"],
                "freshness_seconds": contract["freshness_seconds"],
                "appended_document_count_per_variant": contract["appended_document_count"],
                "development_prechange_observations": development_observations,
                "held_out_prechange_contract_failures_verified": held_out_contract_failures_verified,
                "held_out_candidate_results_revealed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
