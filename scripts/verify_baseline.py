from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = os.environ.get("RUNBOOK_SENTINEL_PYTHONPATH", str(ROOT / "src"))
CHECKPOINT = "baseline-0015"


def run(command: list[str]) -> None:
    print("RUN", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=ENV, check=True)


def main() -> None:
    run([sys.executable, "scripts/verify_manifest.py"])
    run([sys.executable, "scripts/verify_evidence_conditions.py"])
    run([sys.executable, "scripts/verify_behavioral_relations.py"])
    run([sys.executable, "scripts/verify_retrieval_stress.py"])
    run([sys.executable, "scripts/verify_stale_evidence_stress.py"])
    run([sys.executable, "scripts/verify_stale_payload_projection.py"])
    run([sys.executable, "scripts/verify_terminal_contract.py"])
    run([sys.executable, "scripts/verify_approval_lifetime_contract.py"])
    run([sys.executable, "scripts/verify_idempotency_authorization_contract.py"])
    run([sys.executable, "scripts/verify_operator_authentication_contract.py"])
    run([sys.executable, "scripts/verify_package_contract.py"])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    runs_dir = ROOT / "artifacts/evaluations/runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    attempt = 1
    while True:
        output = runs_dir / f"{CHECKPOINT}-attempt-{attempt:03d}.json"
        trace = output.with_name(output.stem + ".traces.jsonl")
        manifest_copy = output.with_name(output.stem + ".manifest.json")
        if not output.exists() and not trace.exists() and not manifest_copy.exists():
            break
        attempt += 1
    shutil.copyfile(ROOT / "eval/manifest.json", manifest_copy)
    run([sys.executable, "-m", "runbook_sentinel", "evaluate", "--output", str(output.relative_to(ROOT)), "--trials", "3"])
    report = json.loads(output.read_text(encoding="utf-8"))
    if report["gates"]["baseline_disposition"] != "pass":
        raise SystemExit(f"Evaluation retained at {output}; baseline did not pass")
    shutil.copyfile(output, ROOT / "artifacts/evaluations/latest.json")
    print(f"PROMOTED {output} -> artifacts/evaluations/latest.json")


if __name__ == "__main__":
    main()
