from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "eval/live-trace-anchor-contract.json"


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    errors: list[str] = []
    if contract.get("contract_id") != "live-trace-anchor-v1":
        errors.append("contract_id mismatch")
    if contract.get("checkpoint") != "baseline-0017":
        errors.append("checkpoint mismatch")
    if contract.get("status") != "frozen" or not contract.get("frozen_before_implementation"):
        errors.append("contract is not frozen before implementation")
    if contract.get("candidate_results") is not None:
        errors.append("candidate results were revealed in the frozen contract")

    cases = contract.get("cases", [])
    case_ids = [case.get("case_id") for case in cases]
    splits = [case.get("split") for case in cases]
    if len(cases) != 10 or len(set(case_ids)) != 10:
        errors.append("contract must contain ten unique cases")
    if splits.count("development") != 4 or splits.count("test") != 6:
        errors.append("contract must contain four development and six test cases")
    required_ids = {
        "dev-empty-start",
        "dev-first-write-exact",
        "dev-tail-truncation-detected",
        "dev-anchor-digest-mutation-detected",
        "test-missing-anchor-detected",
        "test-orphan-anchor-detected",
        "test-extra-suffix-detected",
        "test-valid-restart-resume-exact",
        "test-malformed-anchor-detected",
        "test-wrong-trace-name-detected",
    }
    if set(case_ids) != required_ids:
        errors.append("case inventory mismatch")

    exact_fields = contract.get("anchor_schema", {}).get("exact_fields", [])
    if exact_fields != sorted(exact_fields) or set(exact_fields) != {
        "schema",
        "trace_schema",
        "trace_file_name",
        "event_count",
        "final_event_sha256",
        "anchor_sha256",
    }:
        errors.append("anchor exact field contract mismatch")
    if contract.get("anchor_schema", {}).get("schema") != "trace-anchor/v1":
        errors.append("anchor schema mismatch")

    write_order = contract.get("persistence_contract", {}).get("write_order", [])
    required_phrases = ("flush", "fsync", "temporary", "replace")
    joined_order = " ".join(write_order).lower()
    if not all(phrase in joined_order for phrase in required_phrases):
        errors.append("persistence write order is incomplete")

    gates = contract.get("gates", {})
    for gate in (
        "all_ten_cases_exact",
        "development_exact",
        "test_exact",
        "all_prior_source_package_and_real_surface_gates",
    ):
        if gates.get(gate) is not True:
            errors.append(f"required gate not frozen true: {gate}")
    for gate in (
        "tail_truncation_detection_rate",
        "invalid_state_no_append_rate",
        "valid_resume_exact_rate",
    ):
        if gates.get(gate) != 1.0:
            errors.append(f"required rate not frozen at 1.0: {gate}")

    forbidden_text = " ".join(contract.get("forbidden_changes", [])).lower()
    for phrase in ("hmac key", "signing key", "external collector", "writer-authentication"):
        if phrase not in forbidden_text:
            errors.append(f"missing forbidden boundary: {phrase}")

    result = {
        "contract": str(CONTRACT.relative_to(ROOT)),
        "contract_id": contract.get("contract_id"),
        "checkpoint": contract.get("checkpoint"),
        "case_count": len(cases),
        "development_case_count": splits.count("development"),
        "test_case_count": splits.count("test"),
        "candidate_results_absent": contract.get("candidate_results") is None,
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
