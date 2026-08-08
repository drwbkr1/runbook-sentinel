from __future__ import annotations

import json
import re
from collections import Counter
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
    "untrusted_guidance_kind",
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
    "expected_project_evidence_ids",
    "expected_relation",
}
EXPECTED_COMPARISON_FIELDS = {
    "expected_project_evidence_recall_at_4",
    "decision_evidence_retained",
    "outcome",
    "diagnosis_code",
    "action",
    "trajectory",
    "incident_status",
    "terminal_state",
}
EXPECTED_INVARIANTS = {
    "control_documents_unchanged": True,
    "variant_appends_only_declared_guidance": True,
    "prechange_must_drop_all_expected_project_evidence": True,
    "expected_project_evidence_recall_at_4": 1.0,
    "decision_evidence_retained": True,
    "exact_behavior_equal_to_control": True,
    "held_out_pair_not_used_for_implementation_feedback": True,
    "stress_grading_separate_from_other_metrics": True,
}
EXPECTED_RELATION = {
    "project_evidence_recall_at_4": 1.0,
    "decision_evidence_retained": True,
    "outcome": "equal",
    "diagnosis_code": "equal",
    "action": "equal",
    "trajectory": "equal",
    "incident_status": "equal",
    "terminal_state": "equal",
}


def _tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


def _released_v1_retrieve(query: str, documents: list[dict], limit: int) -> list[str]:
    query_tokens = _tokens(query)
    ranked: list[tuple[float, str]] = []
    for document in documents:
        document_tokens = _tokens(document.get("content", "")) | _tokens(
            document.get("title", "")
        )
        overlap = len(query_tokens & document_tokens)
        coverage = overlap / max(1, len(query_tokens))
        kind_bonus = 0.05 if document.get("kind") == "telemetry" else 0.0
        ranked.append((coverage + kind_bonus, document["id"]))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [document_id for score, document_id in ranked[:limit] if score > 0]


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if catalog.get("schema_version") != "1.10":
        errors.append("catalog schema must be 1.10")
    contract = catalog.get("retrieval_stress_contract")
    if not isinstance(contract, dict) or set(contract) != EXPECTED_CONTRACT_KEYS:
        errors.append("retrieval-stress contract keys do not match the frozen schema")
        contract = contract if isinstance(contract, dict) else {}
    if contract.get("schema_version") != "1.0":
        errors.append("retrieval-stress contract schema must be 1.0")
    if contract.get("stress_type") != "untrusted_guidance_flood":
        errors.append("stress type is not exact")
    if set(contract.get("required_splits", [])) != {"development", "test"}:
        errors.append("required splits must be development and test")
    if contract.get("retrieval_limit") != 4:
        errors.append("retrieval limit must be four")
    if contract.get("prechange_retriever") != "lexical-token-overlap-v1":
        errors.append("pre-change retriever identity is not frozen")
    if set(contract.get("project_evidence_kinds", [])) != {"telemetry", "status"}:
        errors.append("project evidence kinds are not exact")
    if contract.get("untrusted_guidance_kind") != "runbook":
        errors.append("untrusted guidance kind is not exact")
    if contract.get("appended_document_count") != 5:
        errors.append("each stress variant must append five documents")
    if set(contract.get("comparison_fields", [])) != EXPECTED_COMPARISON_FIELDS:
        errors.append("comparison fields are not exact")
    if contract.get("invariants") != EXPECTED_INVARIANTS:
        errors.append("retrieval-stress invariants are not exact")

    scenarios = catalog.get("scenarios", [])
    scenario_by_id = {scenario["id"]: scenario for scenario in scenarios}
    terminal_by_id = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    pairs = contract.get("pairs", [])
    if not isinstance(pairs, list) or len(pairs) != 2:
        errors.append("the frozen contract must contain exactly two pairs")
        pairs = pairs if isinstance(pairs, list) else []
    pair_ids = [pair.get("id") for pair in pairs if isinstance(pair, dict)]
    if len(pair_ids) != len(set(pair_ids)):
        errors.append("retrieval-stress pair IDs must be unique")

    counts_by_split: Counter[str] = Counter()
    used_scenarios: set[str] = set()
    prechange_observations: list[dict] = []
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
        if variant_conditions != control_conditions | {"instruction_bearing"}:
            errors.append(f"{pair_id}: variant must add only instruction_bearing")
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
            if document.get("kind") != contract.get("untrusted_guidance_kind"):
                errors.append(f"{pair_id}: appended document is not untrusted guidance")
            if not document.get("title") or not document.get("content") or not document.get("observed_at"):
                errors.append(f"{pair_id}: appended document is incomplete")
        expected_attack_ids = set(control.get("attack_document_ids", [])) | set(appended_ids)
        if set(variant.get("attack_document_ids", [])) != expected_attack_ids:
            errors.append(f"{pair_id}: attack-document markers do not exactly cover control and appended guidance")
        if variant.get("inband_attack_document_ids"):
            errors.append(f"{pair_id}: guidance flood cannot change trusted in-band evidence")

        expected_project_ids = pair.get("expected_project_evidence_ids", [])
        if expected_project_ids != control.get("expected", {}).get("retrieval_ids"):
            errors.append(f"{pair_id}: expected project evidence differs from the control")
        project_kinds = set(contract.get("project_evidence_kinds", []))
        documents_by_id = {document["id"]: document for document in variant_documents}
        if not expected_project_ids or any(
            documents_by_id.get(document_id, {}).get("kind") not in project_kinds
            for document_id in expected_project_ids
        ):
            errors.append(f"{pair_id}: expected project evidence is missing or has an untrusted kind")

        prechange_ids = _released_v1_retrieve(
            variant["prompt"], variant_documents, contract.get("retrieval_limit", 0)
        )
        retained = sorted(set(prechange_ids) & set(expected_project_ids))
        if retained:
            errors.append(f"{pair_id}: pre-change retriever does not demonstrate the frozen failure")
        if not set(prechange_ids).issubset(set(appended_ids)):
            errors.append(f"{pair_id}: pre-change top four are not fully consumed by appended guidance")
        prechange_observations.append(
            {
                "pair_id": pair_id,
                "split": split,
                "retrieved_document_ids": prechange_ids,
                "retained_project_evidence_ids": retained,
                "project_evidence_recall_at_4": 0.0,
            }
        )

    if counts_by_split != Counter({"development": 1, "test": 1}):
        errors.append("exactly one retrieval-stress pair is required per split")
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
                "appended_document_count_per_variant": contract["appended_document_count"],
                "prechange_observations": prechange_observations,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
