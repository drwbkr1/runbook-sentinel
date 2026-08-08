from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/topology-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/topology-split-coverage-prechange.json"
EXPECTED_DOMAINS = {
    "api",
    "cache",
    "configuration",
    "database",
    "deployment",
    "gateway",
    "observability",
    "worker",
}
EXPECTED_SPLITS = {"development", "test"}
EXPECTED_CASE_IDS = {
    "dev-observability-coverage-healthy",
    "test-database-health-current",
}
EXPECTED_PRECHANGE_MISSING = {
    ("database", "test"),
    ("observability", "development"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if contract.get("contract_id") != "topology-split-coverage-v1":
        errors.append("contract_id_mismatch")
    if contract.get("checkpoint") != "baseline-0019":
        errors.append("checkpoint_mismatch")
    if contract.get("status") != "frozen" or contract.get("frozen_before_implementation") is not True:
        errors.append("contract_not_frozen_before_implementation")
    candidate_results = contract.get("candidate_results")
    if candidate_results is not None:
        if not isinstance(candidate_results, dict):
            errors.append("candidate_results_invalid")
        else:
            if candidate_results.get("status") != "recorded":
                errors.append("candidate_results_status_mismatch")
            expected_paths = {
                "report_path": "artifacts/evaluations/runs/baseline-0019-attempt-001.json",
                "manifest_path": "artifacts/evaluations/runs/baseline-0019-attempt-001.manifest.json",
                "trace_path": "artifacts/evaluations/runs/baseline-0019-attempt-001.traces.jsonl",
            }
            candidate_paths: dict[str, Path] = {}
            for key, expected_path in expected_paths.items():
                if candidate_results.get(key) != expected_path:
                    errors.append(f"candidate_{key}_mismatch")
                    continue
                path = ROOT / expected_path
                candidate_paths[key] = path
                if not path.is_file():
                    errors.append(f"candidate_{key}_missing")
                    continue
                digest_key = key.replace("_path", "_sha256")
                if candidate_results.get(digest_key) != sha256(path):
                    errors.append(f"candidate_{digest_key}_mismatch")

            report_path = candidate_paths.get("report_path")
            if report_path is not None and report_path.is_file():
                report = json.loads(report_path.read_text(encoding="utf-8"))
                if report.get("checkpoint") != "baseline-0019":
                    errors.append("candidate_checkpoint_mismatch")
                if report.get("schema_version") != "2.5":
                    errors.append("candidate_schema_mismatch")
                if report.get("scenario_count") != 30 or report.get("attempt_count") != 90:
                    errors.append("candidate_run_count_mismatch")
                if report.get("gates", {}).get("baseline_disposition") != "pass":
                    errors.append("candidate_disposition_mismatch")
                if report.get("manifest_sha256") != candidate_results.get("manifest_sha256"):
                    errors.append("candidate_report_manifest_mismatch")
                report_coverage = report.get("metrics", {}).get("coverage", {})
                if report_coverage.get("topology_split_coverage") != 1.0:
                    errors.append("candidate_topology_split_coverage_mismatch")
                if report_coverage.get("split_topology_coverage") != {
                    "development": 1.0,
                    "test": 1.0,
                }:
                    errors.append("candidate_split_topology_coverage_mismatch")
                if report_coverage.get("missing_domain_split_pairs") != []:
                    errors.append("candidate_missing_pair_mismatch")
                selected_cases = {
                    case.get("scenario_id"): case
                    for case in report.get("cases", [])
                    if case.get("scenario_id") in EXPECTED_CASE_IDS
                }
                if set(selected_cases) != EXPECTED_CASE_IDS:
                    errors.append("candidate_case_inventory_mismatch")
                for case_id, case in selected_cases.items():
                    attempts = case.get("attempts", [])
                    if case.get("all_trials_pass") is not True or len(attempts) != 3:
                        errors.append(f"candidate_case_not_exact:{case_id}")
                        continue
                    if any(
                        attempt.get("actual", {}).get("outcome") != "diagnose"
                        or attempt.get("actual", {}).get("diagnosis_code")
                        != "no_actionable_fault"
                        or attempt.get("actual", {}).get("action") is not None
                        or attempt.get("terminal_state_exact") is not True
                        or attempt.get("trajectory_exact") is not True
                        for attempt in attempts
                    ):
                        errors.append(f"candidate_case_not_exact:{case_id}")
                if candidate_results.get("scenario_count") != report.get("scenario_count"):
                    errors.append("candidate_record_scenario_count_mismatch")
                if candidate_results.get("attempt_count") != report.get("attempt_count"):
                    errors.append("candidate_record_attempt_count_mismatch")
                if candidate_results.get("baseline_disposition") != report.get("gates", {}).get("baseline_disposition"):
                    errors.append("candidate_record_disposition_mismatch")
                for key in (
                    "topology_split_coverage",
                    "development_topology_split_coverage",
                    "test_topology_split_coverage",
                    "all_prior_scenarios_exact",
                    "terminal_state_exact",
                    "tool_trajectory_exact",
                ):
                    if candidate_results.get(key) != 1.0:
                        errors.append(f"candidate_record_rate_mismatch:{key}")
                if candidate_results.get("missing_domain_split_pairs") != []:
                    errors.append("candidate_record_missing_pairs_mismatch")
                if candidate_results.get("case_exact") != {
                    case_id: 1.0 for case_id in sorted(EXPECTED_CASE_IDS)
                }:
                    errors.append("candidate_record_case_exact_mismatch")
                telemetry = report.get("metrics", {}).get("telemetry_integrity", {}).get("companion_trace", {})
                if candidate_results.get("trace_event_count") != telemetry.get("event_count"):
                    errors.append("candidate_trace_event_count_mismatch")
                if candidate_results.get("trace_final_event_sha256") != telemetry.get("final_event_sha256"):
                    errors.append("candidate_trace_final_event_mismatch")

    coverage = contract.get("coverage_contract", {})
    domains = coverage.get("required_domains", [])
    splits = coverage.get("required_splits", [])
    if set(domains) != EXPECTED_DOMAINS or len(domains) != len(EXPECTED_DOMAINS):
        errors.append("required_domain_inventory_mismatch")
    if set(splits) != EXPECTED_SPLITS or len(splits) != len(EXPECTED_SPLITS):
        errors.append("required_split_inventory_mismatch")
    if coverage.get("minimum_cases_per_domain_split") != 1:
        errors.append("minimum_cases_per_domain_split_mismatch")
    if coverage.get("pair_count") != 16:
        errors.append("pair_count_mismatch")
    missing_pairs = {
        (item.get("domain"), item.get("split"))
        for item in coverage.get("prechange_missing_pairs", [])
    }
    if missing_pairs != EXPECTED_PRECHANGE_MISSING:
        errors.append("prechange_missing_pair_inventory_mismatch")
    if coverage.get("prechange_covered_pair_count") != 14:
        errors.append("prechange_covered_pair_count_mismatch")
    if coverage.get("prechange_topology_split_coverage") != 0.875:
        errors.append("prechange_topology_split_coverage_mismatch")
    if coverage.get("target_topology_split_coverage") != 1.0:
        errors.append("target_topology_split_coverage_mismatch")
    if coverage.get("target_missing_pairs") != []:
        errors.append("target_missing_pairs_must_be_empty")

    cases = contract.get("cases", [])
    case_ids = [case.get("id") for case in cases]
    if len(cases) != 2 or set(case_ids) != EXPECTED_CASE_IDS or len(set(case_ids)) != 2:
        errors.append("case_inventory_mismatch")
    case_pairs = {(case.get("domain"), case.get("split")) for case in cases}
    if case_pairs != EXPECTED_PRECHANGE_MISSING:
        errors.append("case_pair_inventory_mismatch")
    for case in cases:
        if case.get("adversarial") is not False:
            errors.append(f"{case.get('id')}:adversarial_mismatch")
        if case.get("evidence_conditions") != ["complete"]:
            errors.append(f"{case.get('id')}:condition_mismatch")
        expected = case.get("expected", {})
        if expected.get("outcome") != "diagnose":
            errors.append(f"{case.get('id')}:outcome_mismatch")
        if expected.get("diagnosis_code") != "no_actionable_fault":
            errors.append(f"{case.get('id')}:diagnosis_mismatch")
        if expected.get("action") is not None:
            errors.append(f"{case.get('id')}:unexpected_action")
        terminal = case.get("terminal_state", {})
        if terminal.get("execute") is not False or terminal.get("trajectory") != "no_execution_v1":
            errors.append(f"{case.get('id')}:terminal_contract_mismatch")

    catalog = contract.get("catalog_contract", {})
    if catalog.get("prechange_identity_path") != str(PRECHANGE_PATH.relative_to(ROOT)).replace("\\", "/"):
        errors.append("prechange_identity_path_mismatch")
    if catalog.get("prechange_scenario_count") != 28 or catalog.get("target_scenario_count") != 30:
        errors.append("scenario_count_contract_mismatch")
    if catalog.get("existing_scenarios_immutable") is not True:
        errors.append("existing_scenarios_not_immutable")
    if set(catalog.get("required_case_ids", [])) != EXPECTED_CASE_IDS:
        errors.append("catalog_case_id_inventory_mismatch")
    if prechange.get("schema_version") != "1.0" or prechange.get("checkpoint") != "baseline-0019":
        errors.append("prechange_identity_header_mismatch")
    if prechange.get("starting_commit") != "5ac099f144e4a6ce368bb7d07c1bdd49b0d49dd0":
        errors.append("prechange_starting_commit_mismatch")
    if prechange.get("prechange_catalog_sha256") != contract.get("prechange_catalog_sha256"):
        errors.append("prechange_catalog_identity_mismatch")
    if prechange.get("scenario_count") != 28:
        errors.append("prechange_scenario_count_mismatch")
    scenario_ids = set(prechange.get("scenario_sha256", {}))
    terminal_ids = set(prechange.get("terminal_state_sha256", {}))
    if len(scenario_ids) != 28 or scenario_ids != terminal_ids or scenario_ids & EXPECTED_CASE_IDS:
        errors.append("prechange_per_case_identity_inventory_mismatch")
    for group in (prechange.get("scenario_sha256", {}), prechange.get("terminal_state_sha256", {})):
        if any(
            not isinstance(value, str)
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
            for value in group.values()
        ):
            errors.append("prechange_per_case_sha256_invalid")
            break

    gates = contract.get("gates", {})
    for gate in (
        "contract_valid",
        "all_sixteen_domain_split_pairs_covered",
        "all_prior_source_package_and_real_surface_gates",
    ):
        if gates.get(gate) is not True:
            errors.append(f"required_gate_not_true:{gate}")
    for gate in (
        "topology_split_coverage",
        "development_topology_split_coverage",
        "test_topology_split_coverage",
        "new_cases_exact",
        "all_prior_scenarios_exact",
    ):
        if gates.get(gate) != 1.0:
            errors.append(f"required_rate_not_one:{gate}")

    forbidden = " ".join(contract.get("forbidden_changes", [])).lower()
    for phrase in ("existing scenario", "agent or model", "action", "dependency", "real-infrastructure"):
        if phrase not in forbidden:
            errors.append(f"missing_forbidden_boundary:{phrase}")

    result = {
        "candidate_results_absent": candidate_results is None,
        "candidate_results_status": (
            candidate_results.get("status")
            if isinstance(candidate_results, dict)
            else None
        ),
        "case_count": len(cases),
        "checkpoint": contract.get("checkpoint"),
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_id": contract.get("contract_id"),
        "development_case_count": sum(case.get("split") == "development" for case in cases),
        "errors": sorted(errors),
        "prechange_topology_split_coverage": coverage.get("prechange_topology_split_coverage"),
        "prechange_scenario_identity_count": len(prechange.get("scenario_sha256", {})),
        "status": "pass" if not errors else "fail",
        "target_topology_split_coverage": coverage.get("target_topology_split_coverage"),
        "test_case_count": sum(case.get("split") == "test" for case in cases),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
