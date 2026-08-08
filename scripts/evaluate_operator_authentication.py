from __future__ import annotations

import argparse
import json
from pathlib import Path

from runbook_sentinel.operator_authentication_evaluation import (
    run_operator_authentication_evaluation,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite immutable result: {output}")
    result = run_operator_authentication_evaluation()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "case_count": result["metrics"]["case_count"],
        "exact_match_rate": result["metrics"]["exact_match_rate"],
        "disposition": result["gates"]["operator_authentication_disposition"],
    }, indent=2))
    return 0 if result["gates"]["operator_authentication_disposition"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
