from __future__ import annotations

import json
from pathlib import Path

from runbook_sentinel.agent import DeterministicIncidentAgent
from runbook_sentinel.evidence import PROJECT_EVIDENCE_KINDS, is_fresh_project_evidence
from runbook_sentinel.retrieval import LexicalRetriever, select_decision_documents


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
EXPECTED_CONTRACT_KEYS = {
    "schema_version",
    "stress_type",
    "required_splits",
    "retrieval_configuration",
    "prechange_decision_context",
    "candidate_decision_context",
    "project_evidence_kinds",
    "freshness_seconds",
    "required_stale_fields",
    "forbidden_stale_payload_fields",
    "required_fresh_fields",
    "comparison_fields",
    "invariants",
    "cases",
}
EXPECTED_INVARIANTS = {
    "full_retrieved_documents_retained_for_audit": True,
    "projection_applies_only_at_agent_boundary": True,
    "fresh_project_documents_remain_complete": True,
    "stale_project_documents_retain_exactly_required_fields": True,
    "stale_title_and_content_never_reach_agent": True,
    "freshness_derived_from_scenario_as_of": True,
    "unparseable_missing_or_future_timestamp_projects_payload": True,
    "exact_behavior_unchanged": True,
    "held_out_candidate_not_used_for_implementation_feedback": True,
    "boundary_grading_separate_from_retrieval_and_behavior": True,
}
EXPECTED_COMPARISON_FIELDS = [
    "stale_identity_retained",
    "stale_metadata_exact",
    "stale_payload_exposure",
    "fresh_payload_retained",
    "outcome",
    "diagnosis_code",
    "missing_evidence",
    "action",
    "trajectory",
    "incident_status",
    "terminal_state",
]


def _action(result: dict) -> str | None:
    return (result.get("proposal") or {}).get("action")


def validate(catalog: dict | None = None) -> list[str]:
    catalog = catalog or json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if catalog.get("schema_version") != "1.9":
        errors.append("catalog schema must be 1.9")
    contract = catalog.get("stale_payload_projection_contract")
    if not isinstance(contract, dict):
        return errors + ["stale-payload projection contract is missing"]
    if set(contract) != EXPECTED_CONTRACT_KEYS:
        errors.append("stale-payload projection contract keys are not exact")
    if contract.get("schema_version") != "1.0":
        errors.append("stale-payload projection contract schema must be 1.0")
    if contract.get("stress_type") != "stale_project_payload_decision_boundary":
        errors.append("stale-payload stress type is not exact")
    if contract.get("required_splits") != ["development", "test"]:
        errors.append("stale-payload required splits are not exact")
    if contract.get("retrieval_configuration") != "freshness-priority-lexical-v3":
        errors.append("stale-payload retrieval configuration is not exact")
    if contract.get("prechange_decision_context") != "evidence-only-context-v2":
        errors.append("stale-payload pre-change context is not exact")
    if contract.get("candidate_decision_context") != "fresh-content-stale-metadata-context-v3":
        errors.append("stale-payload candidate context is not exact")
    if contract.get("project_evidence_kinds") != ["telemetry", "status"] or set(
        contract["project_evidence_kinds"]
    ) != PROJECT_EVIDENCE_KINDS:
        errors.append("stale-payload evidence kinds are not exact")
    if contract.get("freshness_seconds") != 3600:
        errors.append("stale-payload freshness boundary changed")
    if contract.get("required_stale_fields") != ["id", "kind", "observed_at"]:
        errors.append("stale metadata fields are not exact")
    if contract.get("forbidden_stale_payload_fields") != ["title", "content"]:
        errors.append("forbidden stale payload fields are not exact")
    if contract.get("required_fresh_fields") != ["id", "kind", "observed_at", "title", "content"]:
        errors.append("fresh payload fields are not exact")
    if contract.get("comparison_fields") != EXPECTED_COMPARISON_FIELDS:
        errors.append("stale-payload comparison fields are not exact")
    if contract.get("invariants") != EXPECTED_INVARIANTS:
        errors.append("stale-payload invariants are not exact")

    scenarios = {item["id"]: item for item in catalog.get("scenarios", [])}
    cases = contract.get("cases", [])
    if not isinstance(cases, list) or len(cases) != 2:
        return errors + ["exactly two stale-payload cases are required"]
    if {item.get("split") for item in cases if isinstance(item, dict)} != {"development", "test"}:
        errors.append("exactly one stale-payload case is required per split")
    if len({item.get("id") for item in cases if isinstance(item, dict)}) != len(cases):
        errors.append("stale-payload case IDs must be unique")

    agent = DeterministicIncidentAgent()
    for item in cases:
        if not isinstance(item, dict):
            errors.append("stale-payload case must be an object")
            continue
        case_id = item.get("id", "unknown")
        scenario = scenarios.get(item.get("scenario_id"))
        if scenario is None:
            errors.append(f"{case_id}: scenario is missing")
            continue
        if scenario.get("split") != item.get("split"):
            errors.append(f"{case_id}: split does not match scenario")
        documents = {document["id"]: document for document in scenario.get("documents", [])}
        stale_ids = item.get("stale_document_ids", [])
        fresh_ids = item.get("fresh_document_ids", [])
        if not stale_ids:
            errors.append(f"{case_id}: at least one stale document is required")
        if set(stale_ids) & set(fresh_ids):
            errors.append(f"{case_id}: fresh and stale IDs overlap")
        for document_id in stale_ids:
            document = documents.get(document_id)
            if document is None:
                errors.append(f"{case_id}: stale document {document_id} is missing")
                continue
            if document.get("kind") not in PROJECT_EVIDENCE_KINDS:
                errors.append(f"{case_id}: {document_id} is not project evidence")
            if is_fresh_project_evidence(document, scenario["as_of"]):
                errors.append(f"{case_id}: {document_id} is not stale")
            if not all(field in document for field in contract["required_stale_fields"]):
                errors.append(f"{case_id}: {document_id} lacks required stale metadata")
            if not all(field in document for field in contract["forbidden_stale_payload_fields"]):
                errors.append(f"{case_id}: {document_id} does not discriminate payload exposure")
        for document_id in fresh_ids:
            document = documents.get(document_id)
            if document is None:
                errors.append(f"{case_id}: fresh document {document_id} is missing")
                continue
            if not is_fresh_project_evidence(document, scenario["as_of"]):
                errors.append(f"{case_id}: {document_id} is not fresh")
            if not all(field in document for field in contract["required_fresh_fields"]):
                errors.append(f"{case_id}: {document_id} lacks required fresh payload")

        retrieved = LexicalRetriever(contract["retrieval_configuration"]).retrieve(
            scenario["prompt"], scenario["documents"], as_of=scenario["as_of"]
        )
        retrieved_ids = {document["id"] for document in retrieved}
        if not set(stale_ids).issubset(retrieved_ids):
            errors.append(f"{case_id}: frozen retriever omits declared stale evidence")
        if not set(fresh_ids).issubset(retrieved_ids):
            errors.append(f"{case_id}: frozen retriever omits declared fresh evidence")
        decision = select_decision_documents(contract["prechange_decision_context"], retrieved)
        decision_by_id = {document["id"]: document for document in decision}
        if not set(stale_ids).issubset(decision_by_id):
            errors.append(f"{case_id}: pre-change context does not expose stale identity")
        for document_id in stale_ids:
            exposed = decision_by_id.get(document_id, {})
            if not all(field in exposed for field in contract["forbidden_stale_payload_fields"]):
                errors.append(f"{case_id}: pre-change context is not discriminating")
        for document_id in fresh_ids:
            exposed = decision_by_id.get(document_id, {})
            if not all(field in exposed for field in contract["required_fresh_fields"]):
                errors.append(f"{case_id}: pre-change context does not retain fresh payload")

        result = agent.analyze(scenario["prompt"], decision, scenario["as_of"])
        expected = item.get("expected", {})
        if result.get("outcome") != expected.get("outcome"):
            errors.append(f"{case_id}: pre-change outcome is not frozen exact")
        if result.get("diagnosis_code") != expected.get("diagnosis_code"):
            errors.append(f"{case_id}: pre-change diagnosis is not frozen exact")
        if result.get("missing_evidence", []) != expected.get("missing_evidence", []):
            errors.append(f"{case_id}: pre-change missing evidence is not frozen exact")
        if _action(result) != expected.get("action"):
            errors.append(f"{case_id}: pre-change action is not frozen exact")
        scenario_expected = scenario.get("expected", {})
        for field in ("outcome", "diagnosis_code", "action"):
            if expected.get(field) != scenario_expected.get(field):
                errors.append(f"{case_id}: contract {field} disagrees with scenario")
        if expected.get("trajectory") != "no_execution_v1":
            errors.append(f"{case_id}: frozen trajectory must be no_execution_v1")
        if expected.get("incident_status") != "open":
            errors.append(f"{case_id}: frozen incident status must remain open")
        if expected.get("terminal_state") != scenario.get("initial_state"):
            errors.append(f"{case_id}: frozen terminal state must equal initial state")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "contract": "stale_project_payload_decision_boundary", "case_count": 2, "splits": ["development", "test"], "prechange_discriminating": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
