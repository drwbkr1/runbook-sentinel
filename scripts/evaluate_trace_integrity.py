from __future__ import annotations

import argparse
import json
from pathlib import Path

from runbook_sentinel.trace_integrity_evaluation import (
    run_trace_integrity_evaluation,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the frozen trace-integrity contract"
    )
    parser.add_argument("--split", choices=("development", "test", "all"), default="all")
    parser.add_argument("--output")
    args = parser.parse_args()
    report = run_trace_integrity_evaluation(
        None if args.split == "all" else args.split
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise FileExistsError(f"Trace-integrity attempt already exists: {output}")
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not report["gates"]["all_selected_cases_exact"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
