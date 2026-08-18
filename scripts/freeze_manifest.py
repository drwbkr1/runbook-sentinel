from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ".dockerignore",
    "Dockerfile",
    "pyproject.toml",
    "eval/container-contract.json",
    "eval/container-contract-0027.json",
    "eval/container-contract-0027-v2.json",
    "eval/container-contract-0027-v3.json",
    "eval/container-contract-0027-v4.json",
    "eval/container-contract-0027-v5.json",
    "eval/container-contract-0027-v6.json",
    "eval/container-contract-0027-v7.json",
    "eval/container-contract-0028-v8.json",
    "eval/container-contract-0029-v9.json",
    "eval/container-contract-0030-v10.json",
    "eval/model-contract.json",
    "eval/model-contract-0018-v2.json",
    "eval/model-output-conformance-contract.json",
    "eval/model-output-failure-contract.json",
    "eval/package-contract.json",
    "eval/package-contract-0012.json",
    "eval/package-contract-0013.json",
    "eval/package-contract-0014.json",
    "eval/package-contract-0015.json",
    "eval/package-contract-0016.json",
    "eval/package-contract-0017.json",
    "eval/package-contract-0018.json",
    "eval/package-contract-0019.json",
    "eval/package-contract-0020.json",
    "eval/package-contract-0021.json",
    "eval/package-contract-0022.json",
    "eval/package-contract-0023.json",
    "eval/package-contract-0024.json",
    "eval/package-contract-0025.json",
    "eval/package-contract-0026.json",
    "eval/package-contract-0027.json",
    "eval/package-contract-0028.json",
    "eval/package-contract-0029.json",
    "eval/package-contract-0030.json",
    "eval/approval-lifetime-contract.json",
    "eval/idempotency-authorization-contract.json",
    "eval/operator-authentication-contract.json",
    "eval/trace-integrity-contract.json",
    "eval/live-trace-anchor-contract.json",
    "eval/dashboard-identity-contract.json",
    "eval/topology-split-coverage-contract.json",
    "eval/topology-split-coverage-prechange.json",
    "eval/action-split-coverage-contract.json",
    "eval/action-split-coverage-prechange.json",
    "eval/adversarial-topology-split-coverage-contract.json",
    "eval/adversarial-topology-split-coverage-prechange.json",
    "eval/adversarial-action-split-coverage-contract.json",
    "eval/adversarial-action-split-coverage-prechange.json",
    "eval/adversarial-outcome-split-coverage-contract.json",
    "eval/adversarial-outcome-split-coverage-prechange.json",
    "eval/adversarial-condition-outcome-split-coverage-contract.json",
    "eval/adversarial-condition-outcome-split-coverage-prechange.json",
    "eval/adversarial-domain-outcome-split-coverage-contract.json",
    "eval/adversarial-domain-outcome-split-coverage-prechange.json",
    "eval/adversarial-exposure-stage-outcome-split-coverage-contract.json",
    "eval/adversarial-exposure-stage-outcome-split-coverage-prechange.json",
    "eval/adversarial-retrieval-stage-outcome-split-coverage-contract.json",
    "eval/adversarial-retrieval-stage-outcome-split-coverage-prechange.json",
    "eval/retrieval-quality-observability-contract.json",
    "eval/retrieval-quality-observability-prechange.json",
    "eval/retrieval-tier-cap-contract.json",
    "eval/manifest-0030-precomparison.json",
    "artifacts/evaluations/baseline-0030-model-contract-comparison.json",
    "artifacts/verification/intake-public-v0.0.23-package-baseline-0028.json",
    "artifacts/verification/controlled-intake/baseline-0028-historical-package-v0.0.23-001/runbook-sentinel-0.0.23.pyz",
    "src/runbook_sentinel/__init__.py",
    "src/runbook_sentinel/__main__.py",
    "src/runbook_sentinel/data/scenarios.json",
    "src/runbook_sentinel/catalog.py",
    "src/runbook_sentinel/cli.py",
    "src/runbook_sentinel/errors.py",
    "src/runbook_sentinel/retrieval.py",
    "src/runbook_sentinel/retrieval_quality.py",
    "src/runbook_sentinel/evidence.py",
    "src/runbook_sentinel/agent.py",
    "src/runbook_sentinel/model_adapter.py",
    "src/runbook_sentinel/policy.py",
    "src/runbook_sentinel/service.py",
    "src/runbook_sentinel/storage.py",
    "src/runbook_sentinel/telemetry.py",
    "src/runbook_sentinel/api.py",
    "src/runbook_sentinel/approval_lifetime_evaluation.py",
    "src/runbook_sentinel/idempotency_authorization_evaluation.py",
    "src/runbook_sentinel/operator_auth.py",
    "src/runbook_sentinel/operator_authentication_evaluation.py",
    "src/runbook_sentinel/mcp_server.py",
    "src/runbook_sentinel/evaluation.py",
    "src/runbook_sentinel/trace_integrity_evaluation.py",
    "src/runbook_sentinel/live_trace_anchor_evaluation.py",
    "scripts/verify_baseline.py",
    "scripts/verify_container_contract.py",
    "scripts/verify_container_runtime.py",
    "scripts/verify_live_api.ps1",
    "scripts/verify_mcp_stdio.py",
    "scripts/inspect_runtime_evidence.py",
    "scripts/verify_terminal_contract.py",
    "scripts/verify_approval_lifetime_contract.py",
    "scripts/verify_idempotency_authorization_contract.py",
    "scripts/verify_operator_authentication_contract.py",
    "scripts/verify_trace_integrity_contract.py",
    "scripts/verify_live_trace_anchor_contract.py",
    "scripts/verify_model_output_failure_contract.py",
    "scripts/verify_model_output_conformance_contract.py",
    "scripts/verify_model_output_conformance_result.py",
    "scripts/verify_model_comparison.py",
    "scripts/verify_evaluation_trace.py",
    "scripts/verify_evidence_conditions.py",
    "scripts/verify_topology_split_coverage_contract.py",
    "scripts/verify_topology_split_coverage.py",
    "scripts/verify_action_split_coverage_contract.py",
    "scripts/verify_action_split_coverage.py",
    "scripts/verify_adversarial_topology_split_coverage_contract.py",
    "scripts/verify_adversarial_topology_split_coverage.py",
    "scripts/verify_adversarial_action_split_coverage_contract.py",
    "scripts/verify_adversarial_action_split_coverage.py",
    "scripts/verify_adversarial_outcome_split_coverage_contract.py",
    "scripts/verify_adversarial_outcome_split_coverage.py",
    "scripts/verify_adversarial_condition_outcome_split_coverage_contract.py",
    "scripts/verify_adversarial_condition_outcome_split_coverage.py",
    "scripts/verify_adversarial_domain_outcome_split_coverage_contract.py",
    "scripts/verify_adversarial_domain_outcome_split_coverage.py",
    "scripts/verify_adversarial_exposure_stage_outcome_split_coverage_contract.py",
    "scripts/verify_adversarial_exposure_stage_outcome_split_coverage.py",
    "scripts/verify_adversarial_retrieval_stage_outcome_split_coverage_contract.py",
    "scripts/verify_adversarial_retrieval_stage_outcome_split_coverage.py",
    "scripts/verify_retrieval_quality_observability_contract.py",
    "scripts/verify_retrieval_tier_cap_contract.py",
    "scripts/verify_retrieval_tier_cap_result.py",
    "scripts/materialize_baseline_0025_catalog.py",
    "scripts/verify_behavioral_relations.py",
    "scripts/verify_retrieval_stress.py",
    "scripts/verify_stale_evidence_stress.py",
    "scripts/verify_stale_payload_projection.py",
    "scripts/evaluate_stale_payload_projection.py",
    "scripts/evaluate_approval_lifetime.py",
    "scripts/evaluate_idempotency_authorization.py",
    "scripts/evaluate_operator_authentication.py",
    "scripts/evaluate_trace_integrity.py",
    "scripts/evaluate_live_trace_anchor.py",
    "scripts/evaluate_model_output_failures.py",
    "scripts/build_zipapp.py",
    "scripts/verify_package_contract.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="baseline-0030")
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
