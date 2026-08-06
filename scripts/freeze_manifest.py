from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "src/runbook_sentinel/data/scenarios.json",
    "src/runbook_sentinel/retrieval.py",
    "src/runbook_sentinel/agent.py",
    "src/runbook_sentinel/policy.py",
    "src/runbook_sentinel/service.py",
    "src/runbook_sentinel/storage.py",
    "src/runbook_sentinel/api.py",
    "src/runbook_sentinel/mcp_server.py",
    "src/runbook_sentinel/evaluation.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "checkpoint": "baseline-0001",
        "frozen_at_utc": "2026-08-06T18:28:35Z",
        "files": {relative: sha256(ROOT / relative) for relative in FILES},
    }
    destination = ROOT / "eval/manifest.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
