from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/trace-integrity-contract.json"
FREEZE_TIMESTAMP = "2026-08-08T00:44:20Z"

TOP_LEVEL_KEYS = {
    "schema_version",
    "contract_id",
    "checkpoint",
    "frozen_at_utc",
    "frozen_before_candidate_implementation",
    "purpose",
    "event_contract",
    "cases",
    "coverage",
    "prechange_evidence",
    "non_claims",
    "unchanged_boundaries",
}
EXPECTED_CASE_IDS = [
    "dev-valid-anchored-chain",
    "dev-content-mutation-detected",
    "dev-sequence-gap-detected",
    "dev-tail-truncation-anchor-detected",
    "test-valid-unanchored-chain",
    "test-reordered-events-detected",
    "test-previous-hash-mutation-detected",
    "test-interior-deletion-detected",
    "test-malformed-json-detected",
    "test-valid-prefix-resume-exact",
]
EXPECTED_TRANSFORMATIONS = [
    "none",
    "change second event attributes.postconditions from true to false without recomputing hashes",
    "change second event sequence from 2 to 7 without recomputing hashes",
    "remove the final event while retaining the original completed-evaluation anchor",
    "none",
    "swap the second and third events",
    "replace the third event previous_event_sha256 without recomputing event_sha256",
    "remove the second event while retaining the original completed-evaluation anchor",
    "replace the second line with malformed JSON",
    "initialize a writer from the valid three-event prefix and append one event",
]
EXPECTED_COVERAGE = {
    "required_splits": ["development", "test"],
    "case_count": 10,
    "development_case_count": 4,
    "test_case_count": 6,
    "valid_case_count": 3,
    "corruption_case_count": 7,
    "required_corruption_classes": [
        "content mutation",
        "sequence gap",
        "tail truncation with anchor",
        "reordering",
        "previous-hash mutation",
        "interior deletion",
        "malformed JSON",
    ],
}
EXPECTED_PRECHANGE = {
    "revealed_case_ids": ["dev-content-mutation-detected"],
    "released_result": "fail",
    "held_out_candidate_results_revealed": False,
    "receipt": "artifacts/verification/trace-integrity-gap-baseline-0016.json",
}
EXPECTED_EVENT_CONTRACT = {
    "schema": "trace-chain/v1",
    "required_top_level_fields": [
        "schema",
        "sequence",
        "previous_event_sha256",
        "trace_id",
        "timestamp",
        "name",
        "attributes",
        "event_sha256",
    ],
    "exact_top_level_fields": True,
    "sequence_origin": 1,
    "sequence_step": 1,
    "genesis_previous_event_sha256": "0" * 64,
    "hash_algorithm": "sha256",
    "hash_input": "UTF-8 canonical JSON of every required field except event_sha256, with sorted keys, no insignificant whitespace, ensure_ascii=True, and allow_nan=False",
    "hash_encoding": "64 lowercase hexadecimal characters",
    "append_rule": "A writer must validate every existing nonempty record before append and resume from the exact next sequence and final event_sha256; any invalid existing prefix refuses append.",
    "completed_evaluation_anchor": "The completed evaluation report records the exact companion trace event count and final event_sha256, and independent verification requires both to match.",
    "empty_trace": "An empty trace is valid only when expected_event_count is zero and expected_final_event_sha256 is null.",
}
EXPECTED_NON_CLAIMS = [
    "The unkeyed chain does not authenticate the writer and does not resist an attacker who can recompute the entire chain and its external anchor.",
    "The implementation is not RFC 5848 signed syslog, a digital signature, immutable storage, non-repudiation, or a production log collector.",
    "An unanchored valid prefix cannot by itself prove that no tail records were removed.",
    "A hostile operating system, compromised process, compromised repository policy, and real infrastructure remain out of scope.",
]
EXPECTED_UNCHANGED = [
    "agent outcomes, model contract, retrieval, decision context, and scenario catalog",
    "proposal schema, action hash, capability allowlist, and executor actions",
    "operator capability exclusion, approval-token hashing, expiry, action binding, and one-time consumption",
    "idempotency, replay, precondition, postcondition, and state-transition enforcement",
    "MCP exposes no approval or execution authority",
    "loopback-only HTTP and disconnected real infrastructure",
    "no new dependency, secret, key, paid service, external asset, or collector",
]


def validate(contract: dict | None = None) -> list[str]:
    contract = contract or json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if set(contract) != TOP_LEVEL_KEYS:
        errors.append("top-level contract keys are not exact")
    if contract.get("schema_version") != "1.0":
        errors.append("schema version must be 1.0")
    if contract.get("contract_id") != "trace-integrity-v1":
        errors.append("contract ID is not exact")
    if contract.get("checkpoint") != "baseline-0016":
        errors.append("checkpoint must be baseline-0016")
    if contract.get("frozen_at_utc") != FREEZE_TIMESTAMP:
        errors.append("freeze timestamp is not exact")
    if contract.get("frozen_before_candidate_implementation") is not True:
        errors.append("contract must be frozen before candidate implementation")
    if contract.get("event_contract") != EXPECTED_EVENT_CONTRACT:
        errors.append("event schema, hash, append, or anchor contract changed")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) != 10:
        errors.append("case count must be ten")
    else:
        if [case.get("case_id") for case in cases] != EXPECTED_CASE_IDS:
            errors.append("ordered case identities changed")
        if [case.get("transformation") for case in cases] != EXPECTED_TRANSFORMATIONS:
            errors.append("ordered transformations changed")
        if [case.get("split") for case in cases] != ["development"] * 4 + ["test"] * 6:
            errors.append("split membership changed")
        if any(set(case) != {"case_id", "split", "transformation", "anchor", "expected"} for case in cases):
            errors.append("case keys are not exact")
    if contract.get("coverage") != EXPECTED_COVERAGE:
        errors.append("coverage requirements changed")
    if contract.get("prechange_evidence") != EXPECTED_PRECHANGE:
        errors.append("revealed and held-out evidence declaration changed")
    if contract.get("non_claims") != EXPECTED_NON_CLAIMS:
        errors.append("integrity non-claims changed")
    if contract.get("unchanged_boundaries") != EXPECTED_UNCHANGED:
        errors.append("unchanged boundaries changed")
    return errors


def main() -> int:
    errors = validate()
    print(json.dumps({
        "valid": not errors,
        "contract": "trace-integrity-v1",
        "checkpoint": "baseline-0016",
        "case_count": 10,
        "development_case_count": 4,
        "test_case_count": 6,
        "held_out_candidate_results_revealed": False,
        "errors": errors,
    }, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
