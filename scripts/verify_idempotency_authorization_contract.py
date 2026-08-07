from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/idempotency-authorization-contract.json"
FREEZE_TIMESTAMP = "2026-08-07T21:33:08Z"

TOP_LEVEL_KEYS = {
    "schema_version",
    "contract_id",
    "checkpoint",
    "frozen_at_utc",
    "frozen_before_candidate_implementation",
    "purpose",
    "policy",
    "cases",
    "state_contract",
    "coverage",
    "prechange_evidence",
    "unchanged_boundaries",
}
POLICY = {
    "same_proposal_cache_disclosure_requires": [
        "approval row belongs to the requested proposal",
        "supplied token hash matches the stored approval token hash",
        "approval consumed_at is not null",
    ],
    "completed_retry_expiry_rule": "Do not recheck approval expiry for the original consumed token retrieving its exact same-proposal same-key completed result.",
    "invalid_http_status": 409,
    "invalid_error_type": "ApprovalError",
    "invalid_error_message": "Approval token is invalid",
    "cross_proposal_key_error": "Idempotency key is already bound to a different proposal",
    "new_key_replay_error_type": "ReplayRejected",
    "new_key_replay_error_message": "Proposal has already been executed",
    "unauthorized_mutation_forbidden": [
        "executor invocation",
        "incident state or status change",
        "proposal status or updated_at change",
        "approval consumed_at or expiry change",
        "idempotency row",
        "audit event",
        "trace event",
    ],
}
INVALID = {
    "http_status": 409,
    "error_type": "ApprovalError",
    "error_message": "Approval token is invalid",
    "exact_cached_result": False,
    "state_unchanged": True,
}
AUTHORIZED = {
    "http_status": 200,
    "error_type": None,
    "error_message": None,
    "exact_cached_result": True,
    "state_unchanged": True,
}
REPLAY = {
    "http_status": 409,
    "error_type": "ReplayRejected",
    "error_message": "Proposal has already been executed",
    "exact_cached_result": False,
    "state_unchanged": True,
}
EXPECTED_CASES = [
    {
        "case_id": "dev-wrong-token-same-key",
        "split": "development",
        "retry": {"proposal": "executed_target", "approval_token": "wrong_syntactically_valid", "idempotency_key": "original"},
        "expected": INVALID,
    },
    {
        "case_id": "dev-missing-token-same-key",
        "split": "development",
        "retry": {"proposal": "executed_target", "approval_token": "missing", "idempotency_key": "original"},
        "expected": INVALID,
    },
    {
        "case_id": "dev-original-consumed-token-same-key",
        "split": "development",
        "retry": {"proposal": "executed_target", "approval_token": "original_consumed", "idempotency_key": "original"},
        "expected": AUTHORIZED,
    },
    {
        "case_id": "test-other-proposal-token-same-key",
        "split": "test",
        "retry": {"proposal": "executed_target", "approval_token": "other_proposal_valid_unconsumed", "idempotency_key": "original"},
        "expected": INVALID,
    },
    {
        "case_id": "test-expired-original-consumed-token-same-key",
        "split": "test",
        "fixture_after_execution": {"set_original_approval_expires_at": "2000-01-01T00:00:00+00:00"},
        "retry": {"proposal": "executed_target", "approval_token": "original_consumed", "idempotency_key": "original"},
        "expected": AUTHORIZED,
    },
    {
        "case_id": "test-original-consumed-token-new-key",
        "split": "test",
        "retry": {"proposal": "executed_target", "approval_token": "original_consumed", "idempotency_key": "new"},
        "expected": REPLAY,
    },
]
COVERAGE = {
    "required_splits": ["development", "test"],
    "case_count": 6,
    "authorized_cache_case_count": 2,
    "unauthorized_cache_case_count": 3,
    "new_key_replay_case_count": 1,
    "development_case_count": 3,
    "test_case_count": 3,
}
PRECHANGE = {
    "revealed_case_ids": ["dev-wrong-token-same-key", "dev-missing-token-same-key", "dev-original-consumed-token-same-key"],
    "released_wrong_and_missing_token_result": "fail",
    "released_original_token_result": "pass",
    "held_out_candidate_results_revealed": False,
    "receipt": "artifacts/verification/idempotency-authorization-gap-baseline-0014.json",
}


def validate(contract: dict | None = None) -> list[str]:
    contract = contract or json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if set(contract) != TOP_LEVEL_KEYS:
        errors.append("top-level contract keys are not exact")
    if contract.get("schema_version") != "1.0":
        errors.append("schema version must be 1.0")
    if contract.get("contract_id") != "idempotency-authorization-v1":
        errors.append("contract ID is not exact")
    if contract.get("checkpoint") != "baseline-0014":
        errors.append("checkpoint must be baseline-0014")
    if contract.get("frozen_at_utc") != FREEZE_TIMESTAMP:
        errors.append("freeze timestamp is not exact")
    if contract.get("frozen_before_candidate_implementation") is not True:
        errors.append("contract must be frozen before candidate implementation")
    if contract.get("policy") != POLICY:
        errors.append("idempotency authorization policy is not exact")
    if contract.get("coverage") != COVERAGE:
        errors.append("coverage requirements are not exact")
    if contract.get("prechange_evidence") != PRECHANGE:
        errors.append("revealed and held-out evidence declaration is not exact")
    cases = contract.get("cases")
    if cases != EXPECTED_CASES:
        errors.append("six ordered cases, split membership, fixtures, retries, or expected results changed")
    state_contract = contract.get("state_contract")
    if not isinstance(state_contract, dict) or state_contract.get("fingerprint_before_and_after_retry") != [
        "incidents ordered rows",
        "runs ordered rows",
        "proposals ordered rows",
        "approvals ordered rows",
        "idempotency ordered rows",
        "audit_log ordered rows",
        "trace file bytes",
    ]:
        errors.append("state fingerprint boundary changed")
    unchanged = contract.get("unchanged_boundaries")
    if not isinstance(unchanged, list) or len(unchanged) != 7:
        errors.append("unchanged boundary declaration is not exact")
    return errors


def main() -> int:
    errors = validate()
    result = {
        "valid": not errors,
        "contract": "idempotency-authorization-v1",
        "checkpoint": "baseline-0014",
        "case_count": 6,
        "development_case_count": 3,
        "test_case_count": 3,
        "held_out_candidate_results_revealed": False,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
