from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads((ROOT / "eval/manifest.json").read_text(encoding="utf-8"))
    mismatches = []
    for relative, expected in manifest["files"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
    if mismatches:
        raise SystemExit(json.dumps({"status": "mismatch", "files": mismatches}, indent=2))
    print(json.dumps({"status": "pass", "checkpoint": manifest["checkpoint"], "file_count": len(manifest["files"])}))


if __name__ == "__main__":
    main()
