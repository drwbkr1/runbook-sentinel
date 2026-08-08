from __future__ import annotations

import hashlib
import json
import tempfile
from importlib.resources import files
from pathlib import Path

from .errors import TraceIntegrityError
from .telemetry import (
    GENESIS_PREVIOUS_EVENT_SHA256,
    TraceWriter,
    build_trace_anchor,
    build_trace_event,
    canonical_json,
    verify_anchored_trace_files,
)


CONTRACT_ID = "live-trace-anchor-v1"
VALID_SPLITS = ("development", "test")


def load_live_trace_anchor_contract() -> dict:
    repository_contract = (
        Path(__file__).resolve().parents[2] / "eval/live-trace-anchor-contract.json"
    )
    if repository_contract.is_file():
        return json.loads(repository_contract.read_text(encoding="utf-8"))
    try:
        return json.loads(
            files("runbook_sentinel")
            .joinpath("data/live-trace-anchor-contract.json")
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise FileNotFoundError(
            "Live-trace-anchor evaluation requires the frozen contract"
        ) from exc


def _contract_valid(contract: dict) -> bool:
    cases = contract.get("cases")
    if contract.get("contract_id") != CONTRACT_ID or not isinstance(cases, list):
        return False
    case_ids = [case.get("case_id") for case in cases]
    splits = [case.get("split") for case in cases]
    return all(
        (
            len(cases) == 10,
            len(case_ids) == len(set(case_ids)),
            splits.count("development") == 4,
            splits.count("test") == 6,
            contract.get("status") == "frozen",
            contract.get("frozen_before_implementation") is True,
            contract.get("candidate_results") is None,
        )
    )


def _base_events(count: int) -> list[dict]:
    events: list[dict] = []
    previous = GENESIS_PREVIOUS_EVENT_SHA256
    for sequence in range(1, count + 1):
        event = build_trace_event(
            sequence=sequence,
            previous_event_sha256=previous,
            trace_id=f"{sequence:032d}",
            timestamp=f"2026-08-08T00:00:{sequence:02d}+00:00",
            name="sentinel.live-anchor-evaluation",
            attributes={"case_event": sequence},
        )
        events.append(event)
        previous = event["event_sha256"]
    return events


def _write_events(path: Path, count: int) -> list[dict]:
    events = _base_events(count)
    path.write_text(
        "".join(canonical_json(event) + "\n" for event in events),
        encoding="utf-8",
    )
    return events


def _write_anchor(path: Path, trace_path: Path, events: list[dict]) -> dict:
    anchor = build_trace_anchor(
        trace_path=trace_path,
        event_count=len(events),
        final_event_sha256=events[-1]["event_sha256"],
    )
    path.write_text(canonical_json(anchor) + "\n", encoding="utf-8")
    return anchor


def _bytes_sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _error_codes(verification: dict) -> list[str]:
    return sorted({error["code"] for error in verification.get("errors", [])})


def _attempt_initialize(trace_path: Path, anchor_path: Path) -> bool:
    try:
        TraceWriter(trace_path, anchor_path)
    except TraceIntegrityError:
        return False
    return True


def _run_case(case: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="sentinel-live-trace-anchor-") as temp_dir:
        base = Path(temp_dir)
        trace_path = base / "live.jsonl"
        anchor_path = base / "live.jsonl.anchor.json"
        case_id = case["case_id"]
        resume_sequence = None
        resume_previous_exact = None

        if case_id == "dev-empty-start":
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "dev-first-write-exact":
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            writer = TraceWriter(trace_path, anchor_path)
            writer.write("sentinel.evaluation", {"event": 1})
            accepted = True
        elif case_id == "dev-tail-truncation-detected":
            events = _write_events(trace_path, 3)
            _write_anchor(anchor_path, trace_path, events)
            trace_path.write_text(
                "".join(canonical_json(event) + "\n" for event in events[:2]),
                encoding="utf-8",
            )
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "dev-anchor-digest-mutation-detected":
            events = _write_events(trace_path, 2)
            anchor = _write_anchor(anchor_path, trace_path, events)
            anchor["event_count"] = 1
            anchor_path.write_text(canonical_json(anchor) + "\n", encoding="utf-8")
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "test-missing-anchor-detected":
            _write_events(trace_path, 1)
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "test-orphan-anchor-detected":
            events = _base_events(1)
            _write_anchor(anchor_path, trace_path, events)
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "test-extra-suffix-detected":
            events = _write_events(trace_path, 2)
            _write_anchor(anchor_path, trace_path, events)
            third = _base_events(3)[2]
            with trace_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(canonical_json(third) + "\n")
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "test-valid-restart-resume-exact":
            events = _write_events(trace_path, 2)
            _write_anchor(anchor_path, trace_path, events)
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            writer = TraceWriter(trace_path, anchor_path)
            appended = writer.write("sentinel.resume", {"result": "continued"})
            resume_sequence = appended["sequence"]
            resume_previous_exact = (
                appended["previous_event_sha256"] == events[-1]["event_sha256"]
            )
            accepted = True
        elif case_id == "test-malformed-anchor-detected":
            _write_events(trace_path, 1)
            anchor_path.write_text('{"schema":"trace-anchor/v1"', encoding="utf-8")
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        elif case_id == "test-wrong-trace-name-detected":
            events = _write_events(trace_path, 1)
            anchor = build_trace_anchor(
                trace_path=base / "other.jsonl",
                event_count=1,
                final_event_sha256=events[-1]["event_sha256"],
            )
            anchor_path.write_text(canonical_json(anchor) + "\n", encoding="utf-8")
            trace_before = _bytes_sha256(trace_path)
            anchor_before = _bytes_sha256(anchor_path)
            accepted = _attempt_initialize(trace_path, anchor_path)
        else:
            raise ValueError(f"Unknown live-trace-anchor case: {case_id}")

        verification = verify_anchored_trace_files(trace_path, anchor_path)
        trace_after = _bytes_sha256(trace_path)
        anchor_after = _bytes_sha256(anchor_path)
        actual = {
            "accepted": accepted,
            "event_count": verification["event_count"],
            "anchor_exists": anchor_path.exists(),
            "new_event_written": trace_before != trace_after,
            "error_codes": _error_codes(verification),
            "anchor_digest_exact": bool(
                verification.get("valid") and verification.get("anchor_sha256")
            ),
            "trace_endpoint_exact": verification.get("valid", False),
        }
        if resume_sequence is not None:
            actual["resume_sequence"] = resume_sequence
            actual["resume_previous_event_sha256_exact"] = resume_previous_exact

        expected = case["expected"]
        checks = {
            key: actual.get(key) == value
            for key, value in expected.items()
            if key != "required_error_codes"
        }
        if "required_error_codes" in expected:
            checks["required_error_codes_present"] = set(
                expected["required_error_codes"]
            ).issubset(actual["error_codes"])
        checks["invalid_state_unchanged"] = (
            True
            if expected.get("accepted") is not False
            else trace_before == trace_after and anchor_before == anchor_after
        )
        return {
            "case_id": case_id,
            "split": case["split"],
            "setup": case["setup"],
            "operation": case["operation"],
            "expected": expected,
            "actual": actual,
            "checks": checks,
            "exact": all(checks.values()),
        }


def _rate(records: list[dict]) -> float | None:
    if not records:
        return None
    return sum(record["exact"] for record in records) / len(records)


def run_live_trace_anchor_evaluation(split: str | None = None) -> dict:
    if split is not None and split not in VALID_SPLITS:
        raise ValueError(f"Unknown live-trace-anchor split: {split}")
    contract = load_live_trace_anchor_contract()
    contract_valid = _contract_valid(contract)
    selected_cases = [
        case for case in contract["cases"] if split is None or case["split"] == split
    ]
    records = [_run_case(case) for case in selected_cases]
    development = [record for record in records if record["split"] == "development"]
    test = [record for record in records if record["split"] == "test"]
    invalid = [
        record for record in records if record["expected"].get("accepted") is False
    ]
    tail = [
        record
        for record in records
        if record["case_id"]
        in {"dev-tail-truncation-detected", "test-extra-suffix-detected"}
    ]
    resume = [
        record
        for record in records
        if record["case_id"] == "test-valid-restart-resume-exact"
    ]
    exact_rate = _rate(records)
    development_rate = _rate(development)
    test_rate = _rate(test)
    invalid_no_append_rate = (
        sum(
            record["checks"].get("new_event_written", True)
            and record["checks"]["invalid_state_unchanged"]
            for record in invalid
        )
        / len(invalid)
        if invalid
        else None
    )
    tail_rate = _rate(tail)
    resume_rate = _rate(resume)
    return {
        "contract_id": contract["contract_id"],
        "checkpoint": contract["checkpoint"],
        "selected_split": split or "all",
        "contract_valid": contract_valid,
        "case_count": len(records),
        "development_case_count": len(development),
        "test_case_count": len(test),
        "metrics": {
            "exact_match_rate": exact_rate,
            "development_exact_match_rate": development_rate,
            "test_exact_match_rate": test_rate,
            "tail_truncation_detection_rate": tail_rate,
            "invalid_state_no_append_rate": invalid_no_append_rate,
            "valid_resume_exact_rate": resume_rate,
        },
        "gates": {
            "contract_valid": contract_valid,
            "all_selected_cases_exact": exact_rate == 1.0,
            "development_exact": (
                development_rate == 1.0 if development_rate is not None else None
            ),
            "test_exact": test_rate == 1.0 if test_rate is not None else None,
            "tail_truncation_detection_rate": tail_rate,
            "invalid_state_no_append_rate": invalid_no_append_rate,
            "valid_resume_exact_rate": resume_rate,
        },
        "cases": records,
    }
