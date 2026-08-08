from __future__ import annotations

import argparse
import json
from pathlib import Path

from runbook_sentinel.telemetry import verify_trace_file


def verify_evaluation_trace(report_path: str | Path, trace_path: str | Path) -> dict:
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    telemetry = report.get("metrics", {}).get("telemetry_integrity", {})
    anchor = telemetry.get("companion_trace", {})
    if set(anchor) != {
        "schema",
        "file_name",
        "event_count",
        "final_event_sha256",
    }:
        return {
            "valid": False,
            "anchored": False,
            "event_count": 0,
            "final_event_sha256": None,
            "errors": [{"code": "evaluation_trace_anchor_missing_or_invalid"}],
        }
    result = verify_trace_file(
        trace_path,
        expected_event_count=anchor["event_count"],
        expected_final_event_sha256=anchor["final_event_sha256"],
    )
    if Path(trace_path).name != anchor["file_name"]:
        result["valid"] = False
        result["errors"].append(
            {
                "code": "companion_trace_file_name_mismatch",
                "expected": anchor["file_name"],
                "actual": Path(trace_path).name,
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an evaluation report against its exact companion trace"
    )
    parser.add_argument("report")
    parser.add_argument("trace")
    args = parser.parse_args()
    result = verify_evaluation_trace(args.report, args.trace)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] and result["anchored"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
