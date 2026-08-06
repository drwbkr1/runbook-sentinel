from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "eval/model-contract.json",
    "src/runbook_sentinel/data/scenarios.json",
    "src/runbook_sentinel/catalog.py",
    "src/runbook_sentinel/retrieval.py",
    "src/runbook_sentinel/agent.py",
    "src/runbook_sentinel/model_adapter.py",
    "src/runbook_sentinel/policy.py",
    "src/runbook_sentinel/service.py",
    "src/runbook_sentinel/storage.py",
    "src/runbook_sentinel/api.py",
    "src/runbook_sentinel/mcp_server.py",
    "src/runbook_sentinel/evaluation.py",
    "scripts/verify_terminal_contract.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="baseline-0004")
    parser.add_argument("--frozen-at")
    parser.add_argument("--output", default="eval/manifest.json")
    args = parser.parse_args()
    frozen_at = args.frozen_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = {
        "schema_version": "1.0",
        "checkpoint": args.checkpoint,
        "frozen_at_utc": frozen_at,
        "files": {relative: sha256(ROOT / relative) for relative in FILES},
    }
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
