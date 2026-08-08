from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/action-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/action-split-coverage-prechange.json"
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
EXPECTED_ACTIONS = {"restart_worker", "rollback_deployment", "warm_cache"}
EXPECTED_SPLITS = {"development", "test"}
EXPECTED_CASE_ID = "test-bad-deployment-current"
EXPECTED_MISSING = {("rollback_deployment", "test")}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
    parent_path = ROOT / prechange.get("identity_parent_path", "")
    parent = json.loads(parent_path.read_text(encoding="utf-8")) if parent_path.is_file() else {}
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if contract.get("contract_id") != "action-split-coverage-v1":
        errors.append("contract_id_mismatch")
    if contract.get("checkpoint") != "baseline-0020":
        errors.append("checkpoint_mismatch")
    if contract.get("status") != "frozen" or contract.get("frozen_before_implementation") is not True:
        errors.append("contract_not_frozen_before_implementation")
    if contract.get("source_measurement") != "artifacts/verification/action-split-gap-baseline-0020.json":
        errors.append("source_measurement_mismatch")
    research = contract.get("research_basis", {})
    if research.get("new_external_asset_imported") is not False:
        errors.append("external_asset_boundary_mismatch")

    coverage = contract.get("coverage_contract", {})
    actions = coverage.get("required_actions", [])
    splits = coverage.get("required_splits", [])
    if set(actions) != EXPECTED_ACTIONS or len(actions) != len(EXPECTED_ACTIONS):
        errors.append("required_action_inventory_mismatch")
    if set(splits) != EXPECTED_SPLITS or len(splits) != len(EXPECTED_SPLITS):
        errors.append("required_split_inventory_mismatch")
    if coverage.get("minimum_cases_per_action_split") != 1 or coverage.get("pair_count") != 6:
        errors.append("coverage_cardinality_mismatch")
    missing = {
        (item.get("action"), item.get("split"))
        for item in coverage.get("prechange_missing_pairs", [])
    }
    if missing != EXPECTED_MISSING:
        errors.append("prechange_missing_pair_mismatch")
    if coverage.get("prechange_covered_pair_count") != 5:
        errors.append("prechange_covered_pair_count_mismatch")
    if coverage.get("prechange_action_split_coverage") != 5 / 6:
        errors.append("prechange_action_split_coverage_mismatch")
    if coverage.get("prechange_split_action_coverage") != {
        "development": 1.0,
        "test": 2 / 3,
    }:
        errors.append("prechange_split_action_coverage_mismatch")
    if coverage.get("target_action_split_coverage") != 1.0:
        errors.append("target_action_split_coverage_mismatch")
    if coverage.get("target_split_action_coverage") != {
        "development": 1.0,
        "test": 1.0,
    }:
        errors.append("target_split_action_coverage_mismatch")
    if coverage.get("target_missing_pairs") != []:
        errors.append("target_missing_pairs_mismatch")

    cases = contract.get("cases", [])
    if len(cases) != 1 or cases[0].get("id") != EXPECTED_CASE_ID:
        errors.append("case_inventory_mismatch")
    else:
        case = cases[0]
        expected = case.get("expected", {})
        terminal = case.get("terminal_state", {})
        if case.get("split") != "test" or case.get("domain") != "deployment":
            errors.append("case_domain_split_mismatch")
        if case.get("adversarial") is not False or case.get("evidence_conditions") != ["complete"]:
            errors.append("case_condition_mismatch")
        if expected.get("outcome") != "propose_action" or expected.get("action") != "rollback_deployment":
            errors.append("case_expected_action_mismatch")
        if terminal.get("execute") is not True or terminal.get("action") != "rollback_deployment":
            errors.append("case_terminal_action_mismatch")
        if terminal.get("trajectory") != "approved_execution_v1" or terminal.get("incident_status") != "mitigated":
            errors.append("case_terminal_trajectory_mismatch")

    catalog_contract = contract.get("catalog_contract", {})
    if catalog_contract.get("prechange_identity_path") != "eval/action-split-coverage-prechange.json":
        errors.append("prechange_identity_path_mismatch")
    if catalog_contract.get("prechange_scenario_count") != 30 or catalog_contract.get("target_scenario_count") != 31:
        errors.append("scenario_count_contract_mismatch")
    if catalog_contract.get("required_case_ids") != [EXPECTED_CASE_ID]:
        errors.append("required_case_inventory_mismatch")
    if catalog_contract.get("existing_scenarios_immutable") is not True:
        errors.append("existing_scenario_boundary_mismatch")
    if catalog_contract.get("existing_terminal_states_immutable") is not True:
        errors.append("existing_terminal_boundary_mismatch")

    if prechange.get("schema_version") != "1.1" or prechange.get("checkpoint") != "baseline-0020":
        errors.append("prechange_header_mismatch")
    if prechange.get("starting_commit") != "9cb80f7806baab987329fd6fda5f9e34df9c6d04":
        errors.append("prechange_starting_commit_mismatch")
    if prechange.get("prechange_catalog_sha256") != "a97fcc118d59c487954e52946bf7bcb936478473756089271c52c9527238d3be":
        errors.append("prechange_catalog_sha256_mismatch")
    if prechange.get("scenario_count") != 30 or prechange.get("parent_scenario_count") != 28:
        errors.append("prechange_count_mismatch")
    if not parent:
        errors.append("identity_parent_missing")
    elif parent.get("scenario_count") != 28:
        errors.append("identity_parent_count_mismatch")

    scenario_identities = dict(parent.get("scenario_sha256", {}))
    terminal_identities = dict(parent.get("terminal_state_sha256", {}))
    scenario_identities.update(prechange.get("scenario_sha256", {}))
    terminal_identities.update(prechange.get("terminal_state_sha256", {}))
    if len(scenario_identities) != 30 or set(scenario_identities) != set(terminal_identities):
        errors.append("composed_identity_inventory_mismatch")
    if EXPECTED_CASE_ID in scenario_identities:
        errors.append("new_case_present_in_prechange_identities")

    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    terminal_states = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    changed_scenarios = sorted(
        scenario_id
        for scenario_id, expected in scenario_identities.items()
        if scenario_id not in scenarios_by_id or object_sha256(scenarios_by_id[scenario_id]) != expected
    )
    changed_terminal_states = sorted(
        scenario_id
        for scenario_id, expected in terminal_identities.items()
        if scenario_id not in terminal_states or object_sha256(terminal_states[scenario_id]) != expected
    )
    if changed_scenarios:
        errors.append("prechange_scenarios_changed")
    if changed_terminal_states:
        errors.append("prechange_terminal_states_changed")

    candidate_results = contract.get("candidate_results")
    if candidate_results is not None:
        if not isinstance(candidate_results, dict) or candidate_results.get("status") != "recorded":
            errors.append("candidate_results_invalid")
        else:
            expected_paths = {
                "report_path": "artifacts/evaluations/runs/baseline-0020-attempt-001.json",
                "manifest_path": "artifacts/evaluations/runs/baseline-0020-attempt-001.manifest.json",
                "trace_path": "artifacts/evaluations/runs/baseline-0020-attempt-001.traces.jsonl",
            }
            resolved: dict[str, Path] = {}
            for key, relative in expected_paths.items():
                if candidate_results.get(key) != relative:
                    errors.append(f"candidate_{key}_mismatch")
                    continue
                path = ROOT / relative
                resolved[key] = path
                if not path.is_file():
                    errors.append(f"candidate_{key}_missing")
                elif candidate_results.get(key.replace("_path", "_sha256")) != sha256(path):
                    errors.append(f"candidate_{key}_digest_mismatch")
            report_path = resolved.get("report_path")
            if report_path is not None and report_path.is_file():
                report = json.loads(report_path.read_text(encoding="utf-8"))
                report_coverage = report.get("metrics", {}).get("coverage", {})
                if report.get("checkpoint") != "baseline-0020" or report.get("scenario_count") != 31:
                    errors.append("candidate_report_identity_mismatch")
                if report.get("attempt_count") != 93 or report.get("gates", {}).get("baseline_disposition") != "pass":
                    errors.append("candidate_report_disposition_mismatch")
                if report_coverage.get("action_split_coverage") != 1.0:
                    errors.append("candidate_action_split_coverage_mismatch")
                if report_coverage.get("split_action_coverage") != {"development": 1.0, "test": 1.0}:
                    errors.append("candidate_split_action_coverage_mismatch")
                if report_coverage.get("missing_action_split_pairs") != []:
                    errors.append("candidate_missing_action_pair_mismatch")
                selected = next(
                    (case for case in report.get("cases", []) if case.get("scenario_id") == EXPECTED_CASE_ID),
                    None,
                )
                if selected is None or selected.get("all_trials_pass") is not True:
                    errors.append("candidate_case_not_exact")
                elif any(
                    attempt.get("actual", {}).get("outcome") != "propose_action"
                    or attempt.get("actual", {}).get("action") != "rollback_deployment"
                    or attempt.get("trajectory_exact") is not True
                    or attempt.get("terminal_state_exact") is not True
                    for attempt in selected.get("attempts", [])
                ):
                    errors.append("candidate_case_not_exact")

    gates = contract.get("gates", {})
    for key in (
        "contract_valid",
        "all_six_action_split_pairs_covered",
        "all_prior_source_package_and_real_surface_gates",
    ):
        if gates.get(key) is not True:
            errors.append(f"required_gate_not_true:{key}")
    for key in (
        "action_split_coverage",
        "development_action_split_coverage",
        "test_action_split_coverage",
        "new_case_exact",
        "all_prior_scenarios_exact",
        "all_prior_terminal_states_exact",
    ):
        if gates.get(key) != 1.0:
            errors.append(f"required_rate_not_one:{key}")

    forbidden = " ".join(contract.get("forbidden_changes", [])).lower()
    for phrase in ("existing scenario", "agent or model", "action", "dependency", "real-infrastructure"):
        if phrase not in forbidden:
            errors.append(f"missing_forbidden_boundary:{phrase}")

    result = {
        "candidate_results_absent": candidate_results is None,
        "candidate_results_status": candidate_results.get("status") if isinstance(candidate_results, dict) else None,
        "case_count": len(cases),
        "checkpoint": contract.get("checkpoint"),
        "composed_prechange_identity_count": len(scenario_identities),
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_id": contract.get("contract_id"),
        "errors": sorted(errors),
        "prechange_action_split_coverage": coverage.get("prechange_action_split_coverage"),
        "status": "pass" if not errors else "fail",
        "target_action_split_coverage": coverage.get("target_action_split_coverage"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
