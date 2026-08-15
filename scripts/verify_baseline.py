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
CHECKPOINT = "baseline-0029"


def run(command: list[str]) -> None:
    print("RUN", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=ENV, check=True)


def main() -> None:
    run([sys.executable, "scripts/verify_manifest.py"])
    run([sys.executable, "scripts/verify_evidence_conditions.py"])
    run([sys.executable, "scripts/verify_topology_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_topology_split_coverage.py"])
    run([sys.executable, "scripts/verify_action_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_action_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_topology_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_adversarial_topology_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_action_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_adversarial_action_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_outcome_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_adversarial_outcome_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_condition_outcome_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_adversarial_condition_outcome_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_domain_outcome_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_adversarial_domain_outcome_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_exposure_stage_outcome_split_coverage_contract.py"])
    run([sys.executable, "scripts/verify_adversarial_exposure_stage_outcome_split_coverage.py"])
    run([sys.executable, "scripts/verify_adversarial_retrieval_stage_outcome_split_coverage_contract.py", "--require-implementation"])
    run([sys.executable, "scripts/verify_adversarial_retrieval_stage_outcome_split_coverage.py"])
    run(
        [
            sys.executable,
            "scripts/verify_retrieval_quality_observability_contract.py",
            "--require-implementation",
            "--implementation-only",
        ]
    )
    run([sys.executable, "scripts/verify_behavioral_relations.py"])
    run([sys.executable, "scripts/verify_retrieval_stress.py"])
    run([sys.executable, "scripts/verify_stale_evidence_stress.py"])
    run([sys.executable, "scripts/verify_stale_payload_projection.py"])
    run([sys.executable, "scripts/verify_terminal_contract.py"])
    run([sys.executable, "scripts/verify_approval_lifetime_contract.py"])
    run([sys.executable, "scripts/verify_idempotency_authorization_contract.py"])
    run([sys.executable, "scripts/verify_operator_authentication_contract.py"])
    run([sys.executable, "scripts/verify_trace_integrity_contract.py"])
    run([sys.executable, "scripts/verify_live_trace_anchor_contract.py"])
    run([sys.executable, "scripts/verify_model_output_failure_contract.py"])
    run([sys.executable, "scripts/verify_model_comparison.py"])
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
    run(
        [
            sys.executable,
            "scripts/verify_retrieval_quality_observability_contract.py",
            "--require-implementation",
            "--report",
            str(output.relative_to(ROOT)),
        ]
    )
    run(
        [
            sys.executable,
            "scripts/verify_evaluation_trace.py",
            str(output.relative_to(ROOT)),
            str(trace.relative_to(ROOT)),
        ]
    )
    shutil.copyfile(output, ROOT / "artifacts/evaluations/latest.json")
    print(f"PROMOTED {output} -> artifacts/evaluations/latest.json")


if __name__ == "__main__":
    main()
