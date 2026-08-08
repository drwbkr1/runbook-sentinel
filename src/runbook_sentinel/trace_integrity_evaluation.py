from __future__ import annotations

import json
import tempfile
from importlib.resources import files
from pathlib import Path

from .telemetry import (
    GENESIS_PREVIOUS_EVENT_SHA256,
    TraceWriter,
    build_trace_event,
    canonical_json,
    verify_trace_file,
    verify_trace_text,
)


CONTRACT_ID = "trace-integrity-v1"
VALID_SPLITS = ("development", "test")


def load_trace_integrity_contract() -> dict:
    repository_contract = (
        Path(__file__).resolve().parents[2] / "eval/trace-integrity-contract.json"
    )
    if repository_contract.is_file():
        return json.loads(repository_contract.read_text(encoding="utf-8"))
    try:
        return json.loads(
            files("runbook_sentinel")
            .joinpath("data/trace-integrity-contract.json")
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise FileNotFoundError(
            "Trace-integrity evaluation requires the frozen contract"
        ) from exc


def _contract_valid(contract: dict) -> bool:
    cases = contract.get("cases")
    coverage = contract.get("coverage", {})
    if contract.get("contract_id") != CONTRACT_ID or not isinstance(cases, list):
        return False
    case_ids = [case.get("case_id") for case in cases]
    splits = [case.get("split") for case in cases]
    return all(
        (
            len(cases) == 10,
            len(case_ids) == len(set(case_ids)),
            set(splits) == set(VALID_SPLITS),
            coverage.get("case_count") == len(cases),
            coverage.get("development_case_count")
            == splits.count("development"),
            coverage.get("test_case_count") == splits.count("test"),
        )
    )


def _base_events() -> list[dict]:
    definitions = (
        (
            "00000000000000000000000000000001",
            "2026-08-08T00:00:01+00:00",
            "sentinel.run",
            {"incident_id": "trace-eval-incident", "outcome": "propose_action"},
        ),
        (
            "00000000000000000000000000000002",
            "2026-08-08T00:00:02+00:00",
            "sentinel.execute",
            {"action": "restart_worker", "postconditions": True},
        ),
        (
            "00000000000000000000000000000003",
            "2026-08-08T00:00:03+00:00",
            "sentinel.audit",
            {"result": "executed", "state": "healthy"},
        ),
    )
    events: list[dict] = []
    previous = GENESIS_PREVIOUS_EVENT_SHA256
    for sequence, (trace_id, timestamp, name, attributes) in enumerate(definitions, 1):
        event = build_trace_event(
            sequence=sequence,
            previous_event_sha256=previous,
            trace_id=trace_id,
            timestamp=timestamp,
            name=name,
            attributes=attributes,
        )
        events.append(event)
        previous = event["event_sha256"]
    return events


def _lines(events: list[dict]) -> list[str]:
    return [canonical_json(event) for event in events]


def _anchor(events: list[dict]) -> tuple[int, str | None]:
    return len(events), events[-1]["event_sha256"] if events else None


def _verify_case(case: dict, base_events: list[dict]) -> dict:
    transformation = case["transformation"]
    anchor_mode = case["anchor"]
    transformed = json.loads(json.dumps(base_events))
    original_count, original_final = _anchor(base_events)
    resume_sequence = None
    resume_previous_exact = None

    if transformation == "none":
        lines = _lines(transformed)
    elif transformation.startswith("change second event attributes.postconditions"):
        transformed[1]["attributes"]["postconditions"] = False
        lines = _lines(transformed)
    elif transformation.startswith("change second event sequence"):
        transformed[1]["sequence"] = 7
        lines = _lines(transformed)
    elif transformation.startswith("remove the final event"):
        transformed = transformed[:-1]
        lines = _lines(transformed)
    elif transformation.startswith("swap the second and third events"):
        transformed[1], transformed[2] = transformed[2], transformed[1]
        lines = _lines(transformed)
    elif transformation.startswith("replace the third event previous_event_sha256"):
        transformed[2]["previous_event_sha256"] = "f" * 64
        lines = _lines(transformed)
    elif transformation.startswith("remove the second event"):
        transformed = [transformed[0], transformed[2]]
        lines = _lines(transformed)
    elif transformation.startswith("replace the second line with malformed JSON"):
        lines = _lines(transformed)
        lines[1] = '{"schema":"trace-chain/v1"'
    elif transformation.startswith("initialize a writer from the valid three-event prefix"):
        with tempfile.TemporaryDirectory(prefix="sentinel-trace-integrity-") as temp_dir:
            trace_path = Path(temp_dir) / "prefix.jsonl"
            trace_path.write_text("\n".join(_lines(base_events)) + "\n", encoding="utf-8")
            writer = TraceWriter(trace_path)
            appended = writer.write("sentinel.resume", {"result": "continued"})
            new_anchor = writer.anchor()
            verification = verify_trace_file(
                trace_path,
                expected_event_count=new_anchor["event_count"],
                expected_final_event_sha256=new_anchor["final_event_sha256"],
            )
            resume_sequence = appended["sequence"]
            resume_previous_exact = (
                appended["previous_event_sha256"] == original_final
            )
        return _case_record(
            case,
            verification,
            resume_sequence=resume_sequence,
            resume_previous_exact=resume_previous_exact,
        )
    else:
        raise ValueError(f"Unknown trace-integrity transformation: {transformation}")

    text = "\n".join(lines) + ("\n" if lines else "")
    if anchor_mode in {"exact", "original_exact"}:
        verification = verify_trace_text(
            text,
            expected_event_count=original_count,
            expected_final_event_sha256=original_final,
        )
    elif anchor_mode == "absent":
        verification = verify_trace_text(text)
    else:
        raise ValueError(f"Unknown trace-integrity anchor mode: {anchor_mode}")
    return _case_record(case, verification)


def _case_record(
    case: dict,
    verification: dict,
    *,
    resume_sequence: int | None = None,
    resume_previous_exact: bool | None = None,
) -> dict:
    error_codes = sorted({error["code"] for error in verification["errors"]})
    actual = {
        "valid": verification["valid"],
        "anchored": verification["anchored"],
        "event_count": verification["event_count"],
        "error_codes": error_codes,
    }
    if resume_sequence is not None:
        actual["resume_sequence"] = resume_sequence
        actual["resume_previous_event_sha256_exact"] = resume_previous_exact

    expected = case["expected"]
    exact = all(
        actual.get(key) == expected_value
        for key, expected_value in expected.items()
        if key not in {"required_error_codes"}
    )
    if "required_error_codes" in expected:
        exact = exact and set(expected["required_error_codes"]).issubset(error_codes)
    return {
        "case_id": case["case_id"],
        "split": case["split"],
        "transformation": case["transformation"],
        "anchor": case["anchor"],
        "expected": expected,
        "actual": actual,
        "exact": exact,
    }


def run_trace_integrity_evaluation(split: str | None = None) -> dict:
    if split is not None and split not in VALID_SPLITS:
        raise ValueError(f"Unknown trace-integrity split: {split}")
    contract = load_trace_integrity_contract()
    contract_valid = _contract_valid(contract)
    selected_cases = [
        case for case in contract["cases"] if split is None or case["split"] == split
    ]
    base_events = _base_events()
    records = [_verify_case(case, base_events) for case in selected_cases]
    exact_count = sum(record["exact"] for record in records)
    corruption_records = [
        record for record in records if record["expected"].get("valid") is False
    ]
    split_exact = {
        selected_split: all(
            record["exact"]
            for record in records
            if record["split"] == selected_split
        )
        for selected_split in VALID_SPLITS
        if any(record["split"] == selected_split for record in records)
    }
    record_by_id = {record["case_id"]: record for record in records}
    anchor_truncation_exact = record_by_id.get(
        "dev-tail-truncation-anchor-detected", {}
    ).get("exact")
    resume_exact = record_by_id.get("test-valid-prefix-resume-exact", {}).get("exact")
    all_selected_exact = bool(records) and exact_count == len(records)
    return {
        "contract_id": contract["contract_id"],
        "contract_valid": contract_valid,
        "selected_split": split or "all",
        "metrics": {
            "case_count": len(records),
            "exact_match_count": exact_count,
            "exact_match_rate": exact_count / len(records) if records else 0.0,
            "corruption_case_count": len(corruption_records),
            "corruption_detection_rate": (
                sum(record["exact"] for record in corruption_records)
                / len(corruption_records)
                if corruption_records
                else None
            ),
            "split_exact_match": split_exact,
        },
        "gates": {
            "contract_valid": contract_valid,
            "all_selected_cases_exact": all_selected_exact,
            "development_exact": split_exact.get("development"),
            "test_exact": split_exact.get("test"),
            "anchored_tail_truncation_detected": anchor_truncation_exact,
            "valid_prefix_resume_exact": resume_exact,
        },
        "cases": records,
    }
