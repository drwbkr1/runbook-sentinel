from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/approval-lifetime-contract.json"

TOP_LEVEL_KEYS = {
    "schema_version",
    "contract_id",
    "checkpoint",
    "frozen_at_utc",
    "frozen_before_candidate_implementation",
    "purpose",
    "policy",
    "cases",
    "coverage",
    "prechange_evidence",
    "unchanged_boundaries",
}
POLICY = {
    "default_ttl_seconds": 300,
    "minimum_ttl_seconds": 1,
    "maximum_ttl_seconds": 300,
    "accepted_json_type": "integer",
    "boolean_is_integer": False,
    "invalid_http_status": 400,
    "invalid_error_type": "ValueError",
    "invalid_error_message": "Approval TTL must be an integer from 1 through 300 seconds",
    "invalid_mutation_forbidden": [
        "proposal status change",
        "approval row",
        "proposal.approved audit event",
        "sentinel.approval trace event",
        "incident state change",
    ],
}
INVALID_EXPECTED = {
    "accepted": False,
    "http_status": 400,
    "proposal_status": "pending",
    "approval_count": 0,
    "approval_audit_count": 0,
    "approval_trace_count": 0,
    "incident_status": "open",
}


def _valid_expected(lifetime_seconds: int) -> dict:
    return {
        "accepted": True,
        "http_status": 201,
        "proposal_status": "approved",
        "approval_count": 1,
        "approval_audit_count": 1,
        "approval_trace_count": 1,
        "incident_status": "open",
        "lifetime_seconds": lifetime_seconds,
    }


EXPECTED_CASES = [
    ("dev-negative-ttl", "development", True, -1, INVALID_EXPECTED),
    ("dev-above-maximum-ttl", "development", True, 301, INVALID_EXPECTED),
    ("dev-minimum-ttl", "development", True, 1, _valid_expected(1)),
    ("test-zero-ttl", "test", True, 0, INVALID_EXPECTED),
    ("test-fractional-ttl", "test", True, 1.5, INVALID_EXPECTED),
    ("test-string-ttl", "test", True, "300", INVALID_EXPECTED),
    ("test-boolean-ttl", "test", True, True, INVALID_EXPECTED),
    ("test-maximum-ttl", "test", True, 300, _valid_expected(300)),
    ("test-default-ttl", "test", False, None, _valid_expected(300)),
]
COVERAGE = {
    "required_splits": ["development", "test"],
    "case_count": 9,
    "invalid_case_count": 6,
    "valid_case_count": 3,
    "development_case_count": 3,
    "test_case_count": 6,
}
PRECHANGE_EVIDENCE = {
    "revealed_case_ids": ["dev-negative-ttl"],
    "revealed_result": "fail",
    "held_out_candidate_results_revealed": False,
    "receipt": "artifacts/verification/approval-lifetime-gap-baseline-0013.json",
}
UNCHANGED_BOUNDARIES = [
    "agent outcomes and configuration",
    "retrieval and decision context",
    "proposal schema and action hash",
    "capability allowlist and executor actions",
    "approval token storage and hashing",
    "idempotency, replay, precondition, and postcondition enforcement",
    "synthetic scenario catalog and existing frozen expectations",
    "real infrastructure remains disconnected",
]


def _same_typed_value(actual: object, expected: object) -> bool:
    return type(actual) is type(expected) and actual == expected


def validate(contract: dict | None = None) -> list[str]:
    contract = contract or json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if set(contract) != TOP_LEVEL_KEYS:
        errors.append("top-level contract keys are not exact")
    if contract.get("schema_version") != "1.0":
        errors.append("schema version must be 1.0")
    if contract.get("contract_id") != "approval-lifetime-v1":
        errors.append("contract ID is not exact")
    if contract.get("checkpoint") != "baseline-0013":
        errors.append("checkpoint must be baseline-0013")
    if contract.get("frozen_at_utc") != "2026-08-07T20:05:11Z":
        errors.append("freeze timestamp is not exact")
    if contract.get("frozen_before_candidate_implementation") is not True:
        errors.append("contract must be frozen before candidate implementation")
    if contract.get("policy") != POLICY:
        errors.append("approval lifetime policy is not exact")
    if contract.get("coverage") != COVERAGE:
        errors.append("coverage requirements are not exact")
    if contract.get("prechange_evidence") != PRECHANGE_EVIDENCE:
        errors.append("revealed and held-out evidence declaration is not exact")
    if contract.get("unchanged_boundaries") != UNCHANGED_BOUNDARIES:
        errors.append("unchanged security boundaries are not exact")

    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) != len(EXPECTED_CASES):
        return errors + ["exactly nine ordered approval lifetime cases are required"]
    for actual, expected in zip(cases, EXPECTED_CASES, strict=True):
        case_id, split, ttl_present, ttl_value, expected_result = expected
        expected_keys = {"case_id", "split", "ttl_present", "expected"}
        if ttl_present:
            expected_keys.add("ttl_value")
        if not isinstance(actual, dict) or set(actual) != expected_keys:
            errors.append(f"{case_id}: case keys are not exact")
            continue
        if actual.get("case_id") != case_id:
            errors.append(f"{case_id}: case ID or ordering changed")
        if actual.get("split") != split:
            errors.append(f"{case_id}: split changed")
        if actual.get("ttl_present") is not ttl_present:
            errors.append(f"{case_id}: TTL presence changed")
        if ttl_present and not _same_typed_value(actual.get("ttl_value"), ttl_value):
            errors.append(f"{case_id}: typed TTL value changed")
        if actual.get("expected") != expected_result:
            errors.append(f"{case_id}: expected result or mutation boundary changed")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "contract": "approval-lifetime-v1",
                "checkpoint": "baseline-0013",
                "case_count": 9,
                "invalid_case_count": 6,
                "valid_case_count": 3,
                "development_case_count": 3,
                "test_case_count": 6,
                "held_out_candidate_results_revealed": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
