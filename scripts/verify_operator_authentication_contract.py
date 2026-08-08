from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/operator-authentication-contract.json"
FREEZE_TIMESTAMP = "2026-08-07T23:18:58Z"

TOP_LEVEL_KEYS = {
    "schema_version",
    "contract_id",
    "checkpoint",
    "frozen_at_utc",
    "frozen_before_candidate_implementation",
    "purpose",
    "architecture",
    "policy",
    "cases",
    "state_contract",
    "secret_exclusion_contract",
    "coverage",
    "prechange_evidence",
    "unchanged_boundaries",
}
ARCHITECTURE = {
    "protected_surface": "POST /api/proposals/{proposal_id}/approve",
    "http_authentication_scheme": "Sentinel-Capability",
    "http_challenge": 'Sentinel-Capability realm="runbook-sentinel-operator"',
    "not_bearer_or_oauth": True,
    "capability_lifecycle": "Supplied interactively for each server launch, retained only as an in-process verifier, and never loaded from an argument, environment variable, repository file, package file, database, audit event, or trace.",
    "operator_identity": "A launch-scoped operator-[0-9a-f]{16} identifier derived server-side from the capability and a fresh in-memory launch nonce.",
    "approval_cli": "The approve command is an HTTP client, accepts no actor, obtains the capability from a hidden prompt or standard input, and cannot call the approval store directly.",
    "server_cli": "The serve command obtains the capability from a hidden prompt or standard input and has no command-line capability value option.",
    "dashboard_label": "authenticated external operator",
}
POLICY = {
    "capability_shape": "43 through 128 ASCII URL-safe characters matching [A-Za-z0-9_-]+",
    "recommended_generation": "secrets.token_urlsafe(32)",
    "comparison": "SHA-256 verifier bytes compared with hmac.compare_digest",
    "authorization_header_count": 1,
    "authentication_precedes_body_parsing": True,
    "caller_actor_field_forbidden": True,
    "caller_actor_error_status": 400,
    "caller_actor_error_type": "ValueError",
    "caller_actor_error_message": "Approval request must not contain actor",
    "invalid_status": 401,
    "invalid_error_type": "OperatorAuthenticationError",
    "invalid_error_message": "Operator capability is invalid",
    "unauthorized_mutation_forbidden": [
        "proposal status or updated_at change",
        "approval row",
        "proposal.approved audit event",
        "sentinel.approval trace event",
        "incident state or status change",
        "executor invocation",
        "idempotency row",
    ],
}


def _denied(case_id: str, split: str, authorization: str, body: object, *, body_not_parsed: bool = False) -> dict:
    expected = {
        "accepted": False,
        "http_status": 401,
        "challenge_exact": True,
        "error_type": "OperatorAuthenticationError",
        "error_message": "Operator capability is invalid",
        "state_unchanged": True,
    }
    if body_not_parsed:
        expected["body_not_parsed"] = True
    return {"case_id": case_id, "split": split, "authorization": authorization, "body": body, "expected": expected}


def _accepted(case_id: str, split: str, body: dict) -> dict:
    return {
        "case_id": case_id,
        "split": split,
        "authorization": "current_launch",
        "body": body,
        "expected": {
            "accepted": True,
            "http_status": 201,
            "challenge_exact": False,
            "proposal_status": "approved",
            "approval_count": 1,
            "approval_audit_count": 1,
            "approval_trace_count": 1,
            "operator_identity_server_derived": True,
            "caller_actor_absent": True,
            "capability_absent_from_surfaces": True,
            "lifetime_seconds": 300,
            "execution_http_status": 200,
            "postconditions_verified": True,
        },
    }


EXPECTED_CASES = [
    _denied("dev-missing-authorization-caller-actor", "development", "missing", {"actor": "sentinel-agent-self-declared"}),
    _denied("dev-missing-authorization-malformed-body", "development", "missing", "malformed_json", body_not_parsed=True),
    _denied("dev-wrong-capability", "development", "wrong_valid_shape", {}),
    _accepted("dev-valid-default-lifetime", "development", {}),
    {
        "case_id": "test-caller-actor-rejected",
        "split": "test",
        "authorization": "current_launch",
        "body": {"actor": "claimed-human"},
        "expected": {"accepted": False, "http_status": 400, "challenge_exact": False, "error_type": "ValueError", "error_message": "Approval request must not contain actor", "state_unchanged": True},
    },
    _denied("test-bearer-scheme-rejected", "test", "bearer_current_capability", {}),
    _denied("test-missing-scheme-value-rejected", "test", "scheme_without_value", {}),
    _denied("test-duplicate-authorization-rejected", "test", "duplicate_current_launch", {}),
    _denied("test-prior-launch-capability-rejected", "test", "prior_launch", {}),
    _accepted("test-valid-maximum-lifetime", "test", {"ttl_seconds": 300}),
]
COVERAGE = {
    "required_splits": ["development", "test"],
    "case_count": 10,
    "authorized_case_count": 2,
    "authentication_denial_case_count": 7,
    "authorized_actor_rejection_case_count": 1,
    "development_case_count": 4,
    "test_case_count": 6,
}
PRECHANGE = {
    "revealed_case_ids": ["dev-missing-authorization-caller-actor"],
    "released_result": "fail",
    "held_out_candidate_results_revealed": False,
    "receipt": "artifacts/verification/approval-authority-gap-baseline-0015.json",
}
UNCHANGED = [
    "agent outcomes, model contract, retrieval, and decision context",
    "proposal schema, action hash, capability allowlist, and executor actions",
    "approval-token hashing, expiry, action binding, and one-time consumption",
    "idempotency, replay, precondition, postcondition, and state-transition enforcement",
    "synthetic scenario catalog and every prior frozen expectation",
    "MCP exposes no approval or execution authority",
    "loopback-only HTTP and disconnected real infrastructure",
    "no new dependency, paid service, external asset, or OAuth component",
]
STATE_CONTRACT = {
    "fingerprint_before_and_after_denied_request": [
        "incidents ordered rows",
        "runs ordered rows",
        "proposals ordered rows",
        "approvals ordered rows",
        "idempotency ordered rows",
        "audit_log ordered rows",
        "trace file bytes",
    ],
    "authorized_terminal_state": {
        "incident_status": "mitigated",
        "proposal_status": "executed",
        "approval_consumed": True,
        "idempotency_record_count": 1,
        "execution_audit_count": 1,
        "execution_trace_count": 1,
    },
}
SECRET_EXCLUSION = {
    "raw_capability_permitted_locations": [
        "operator input process memory",
        "approval HTTP Authorization field in transit over loopback",
        "server request-processing memory",
    ],
    "raw_capability_forbidden_locations": [
        "agent or model input, output, configuration, or telemetry",
        "MCP request, response, tool schema, or server state",
        "repository tracked or untracked files",
        "package entries or package metadata",
        "database rows, audit payloads, or idempotency results",
        "trace events, evaluation reports, dashboard HTML, HTTP error bodies, or structured logs",
        "process arguments or environment variables",
    ],
    "persisted_identity_is_not_human_presence": True,
    "same_process_or_hostile_os_out_of_scope": True,
}


def validate(contract: dict | None = None) -> list[str]:
    contract = contract or json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if set(contract) != TOP_LEVEL_KEYS:
        errors.append("top-level contract keys are not exact")
    if contract.get("schema_version") != "1.0":
        errors.append("schema version must be 1.0")
    if contract.get("contract_id") != "operator-authentication-v1":
        errors.append("contract ID is not exact")
    if contract.get("checkpoint") != "baseline-0015":
        errors.append("checkpoint must be baseline-0015")
    if contract.get("frozen_at_utc") != FREEZE_TIMESTAMP:
        errors.append("freeze timestamp is not exact")
    if contract.get("frozen_before_candidate_implementation") is not True:
        errors.append("contract must be frozen before candidate implementation")
    if contract.get("architecture") != ARCHITECTURE:
        errors.append("operator authentication architecture changed")
    if contract.get("policy") != POLICY:
        errors.append("operator authentication policy changed")
    if contract.get("cases") != EXPECTED_CASES:
        errors.append("ten ordered cases, split membership, requests, or exact expectations changed")
    if contract.get("coverage") != COVERAGE:
        errors.append("coverage requirements changed")
    if contract.get("prechange_evidence") != PRECHANGE:
        errors.append("revealed and held-out evidence declaration changed")
    if contract.get("unchanged_boundaries") != UNCHANGED:
        errors.append("unchanged security boundaries changed")
    if contract.get("state_contract") != STATE_CONTRACT:
        errors.append("state or authorized-terminal boundary changed")
    if contract.get("secret_exclusion_contract") != SECRET_EXCLUSION:
        errors.append("secret exclusion or non-claim boundary changed")
    return errors


def main() -> int:
    errors = validate()
    print(json.dumps({
        "valid": not errors,
        "contract": "operator-authentication-v1",
        "checkpoint": "baseline-0015",
        "case_count": 10,
        "development_case_count": 4,
        "test_case_count": 6,
        "held_out_candidate_results_revealed": False,
        "errors": errors,
    }, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
