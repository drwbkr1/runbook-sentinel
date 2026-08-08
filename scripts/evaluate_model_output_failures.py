from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from runbook_sentinel.model_adapter import (
    ModelOutputValidationError,
    parse_model_content,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/model-output-failure-contract.json"


def _content(case: dict) -> str:
    if case["content_encoding"] == "literal":
        return case["content_literal"]
    return json.dumps(case["payload"], sort_keys=True, separators=(",", ":"))


def _evaluate_case(case: dict) -> dict:
    content = _content(case)
    accepted = False
    error_code = None
    try:
        parse_model_content(content, set(case["allowed_document_ids"]))
        accepted = True
    except ModelOutputValidationError as exc:
        error_code = exc.code
    expected = case["expected"]
    return {
        "case_id": case["case_id"],
        "split": case["split"],
        "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "expected": {
            "accepted": expected["accepted"],
            "error_code": expected["error_code"],
        },
        "actual": {"accepted": accepted, "error_code": error_code},
        "exact": accepted is expected["accepted"] and error_code == expected["error_code"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "all"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"Taxonomy evaluation is immutable: {output}")

    contract_bytes = CONTRACT_PATH.read_bytes()
    contract = json.loads(contract_bytes)
    selected_cases = [
        case
        for case in contract["cases"]
        if args.split == "all" or case["split"] == "development"
    ]
    case_results = [_evaluate_case(case) for case in selected_cases]
    invalid_results = [
        result for result in case_results if result["expected"]["accepted"] is False
    ]
    valid_results = [
        result for result in case_results if result["expected"]["accepted"] is True
    ]
    unclassified = [
        result
        for result in invalid_results
        if result["actual"]["error_code"] is None
    ]
    split_results = {}
    for split in ("development", "test"):
        items = [result for result in case_results if result["split"] == split]
        split_results[split] = {
            "case_count": len(items),
            "exact_match_rate": (
                sum(result["exact"] for result in items) / len(items) if items else None
            ),
        }
    report = {
        "schema_version": "1.0",
        "checkpoint": contract["checkpoint"],
        "contract_id": contract["contract_id"],
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "requested_split": args.split,
        "raw_content_retained": False,
        "case_count": len(case_results),
        "metrics": {
            "exact_match_rate": (
                sum(result["exact"] for result in case_results) / len(case_results)
                if case_results
                else None
            ),
            "development_exact": split_results["development"]["exact_match_rate"],
            "test_exact": split_results["test"]["exact_match_rate"],
            "invalid_output_classification_rate": (
                sum(result["actual"]["error_code"] is not None for result in invalid_results)
                / len(invalid_results)
                if invalid_results
                else None
            ),
            "valid_output_acceptance_rate": (
                sum(result["actual"]["accepted"] for result in valid_results)
                / len(valid_results)
                if valid_results
                else None
            ),
            "unclassified_content_failure_count": len(unclassified),
        },
        "split_metrics": split_results,
        "cases": case_results,
        "disposition": "pass" if case_results and all(result["exact"] for result in case_results) else "fail",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["disposition"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
