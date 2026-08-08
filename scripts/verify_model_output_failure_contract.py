from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/model-output-failure-contract.json"
EXPECTED_CODES = {
    "json_invalid",
    "top_level_not_object",
    "top_level_keys_mismatch",
    "outcome_invalid",
    "diagnosis_code_invalid",
    "evidence_ids_invalid",
    "evidence_ids_duplicate",
    "evidence_id_out_of_context",
    "missing_evidence_invalid",
    "missing_evidence_duplicate",
    "missing_evidence_identifier_invalid",
    "reason_invalid",
    "proposal_shape_invalid",
    "proposal_action_invalid",
    "proposal_capability_mismatch",
    "proposal_arguments_invalid",
    "proposal_nonnull_for_outcome",
}


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if contract.get("contract_id") != "model-output-failure-taxonomy-v1":
        errors.append("contract_id_mismatch")
    if contract.get("checkpoint") != "baseline-0018":
        errors.append("checkpoint_mismatch")
    if contract.get("status") != "frozen" or contract.get("frozen_before_implementation") is not True:
        errors.append("contract_not_frozen")
    codes = contract.get("error_codes")
    if not isinstance(codes, list) or set(codes) != EXPECTED_CODES or len(codes) != len(EXPECTED_CODES):
        errors.append("error_code_inventory_mismatch")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) != 19:
        errors.append("case_count_mismatch")
        cases = []
    case_ids = [case.get("case_id") for case in cases]
    if len(case_ids) != len(set(case_ids)) or any(not isinstance(case_id, str) for case_id in case_ids):
        errors.append("case_ids_invalid")
    split_counts = {
        split: sum(case.get("split") == split for case in cases)
        for split in ("development", "test")
    }
    if split_counts != {"development": 8, "test": 11}:
        errors.append("split_counts_mismatch")
    classified_codes = [
        case.get("expected", {}).get("error_code")
        for case in cases
        if case.get("expected", {}).get("accepted") is False
    ]
    if set(classified_codes) != EXPECTED_CODES or len(classified_codes) != len(EXPECTED_CODES):
        errors.append("case_error_code_coverage_mismatch")
    valid_cases = [case for case in cases if case.get("expected", {}).get("accepted") is True]
    if len(valid_cases) != 2 or any(case.get("expected", {}).get("error_code") is not None for case in valid_cases):
        errors.append("valid_case_inventory_mismatch")
    for case in cases:
        if case.get("content_encoding") not in {"canonical_json", "literal"}:
            errors.append(f"{case.get('case_id')}:content_encoding_invalid")
        if case.get("content_encoding") == "canonical_json" and "payload" not in case:
            errors.append(f"{case.get('case_id')}:payload_missing")
        if case.get("content_encoding") == "literal" and not isinstance(case.get("content_literal"), str):
            errors.append(f"{case.get('case_id')}:content_literal_missing")
        allowed = case.get("allowed_document_ids")
        if not isinstance(allowed, list) or any(not isinstance(item, str) for item in allowed):
            errors.append(f"{case.get('case_id')}:allowed_document_ids_invalid")
    candidate_results = contract.get("candidate_results")
    candidate_results_status = "absent"
    if candidate_results is not None:
        candidate_results_status = "recorded"
        expected_result_keys = {
            "attempt",
            "report_sha256",
            "report_bytes",
            "contract_sha256_before_results",
            "case_count",
            "development_exact",
            "test_exact",
            "invalid_output_classification_rate",
            "valid_output_acceptance_rate",
            "unclassified_content_failure_count",
            "raw_content_retained",
            "disposition",
        }
        if not isinstance(candidate_results, dict) or set(candidate_results) != expected_result_keys:
            errors.append("candidate_results_shape_invalid")
        else:
            result_path = ROOT / candidate_results["attempt"]
            if not result_path.is_file():
                errors.append("candidate_result_missing")
            else:
                result_bytes = result_path.read_bytes()
                result = json.loads(result_bytes)
                if hashlib.sha256(result_bytes).hexdigest() != candidate_results["report_sha256"]:
                    errors.append("candidate_result_sha256_mismatch")
                if len(result_bytes) != candidate_results["report_bytes"]:
                    errors.append("candidate_result_size_mismatch")
                expected_values = {
                    "case_count": result.get("case_count"),
                    "development_exact": result.get("metrics", {}).get("development_exact"),
                    "test_exact": result.get("metrics", {}).get("test_exact"),
                    "invalid_output_classification_rate": result.get("metrics", {}).get(
                        "invalid_output_classification_rate"
                    ),
                    "valid_output_acceptance_rate": result.get("metrics", {}).get(
                        "valid_output_acceptance_rate"
                    ),
                    "unclassified_content_failure_count": result.get("metrics", {}).get(
                        "unclassified_content_failure_count"
                    ),
                    "raw_content_retained": result.get("raw_content_retained"),
                    "disposition": result.get("disposition"),
                    "contract_sha256_before_results": result.get("contract_sha256"),
                }
                for field, expected_value in expected_values.items():
                    if candidate_results[field] != expected_value:
                        errors.append(f"candidate_results_{field}_mismatch")
    result = {
        "candidate_results_absent": candidate_results is None,
        "candidate_results_status": candidate_results_status,
        "case_count": len(cases),
        "checkpoint": contract.get("checkpoint"),
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_id": contract.get("contract_id"),
        "development_case_count": split_counts["development"],
        "error_code_count": len(codes) if isinstance(codes, list) else 0,
        "errors": sorted(errors),
        "status": "pass" if not errors else "fail",
        "test_case_count": split_counts["test"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
