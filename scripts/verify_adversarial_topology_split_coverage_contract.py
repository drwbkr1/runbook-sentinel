from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/adversarial-topology-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/adversarial-topology-split-coverage-prechange.json"
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
MEASUREMENT_PATH = ROOT / "artifacts/verification/adversarial-topology-gap-baseline-0021.json"
EXPECTED_DOMAINS = {
    "gateway",
    "api",
    "worker",
    "database",
    "cache",
    "deployment",
    "configuration",
    "observability",
}
EXPECTED_SPLITS = {"development", "test"}
EXPECTED_MISSING = {
    ("gateway", "development"),
    ("api", "development"),
    ("api", "test"),
    ("database", "development"),
    ("database", "test"),
    ("cache", "development"),
    ("deployment", "development"),
    ("configuration", "development"),
    ("observability", "development"),
}
EXPECTED_CASES = {
    "dev-gateway-injection-coverage": ("dev-gateway-evidence-incomplete", "gateway", "development"),
    "dev-api-injection-coverage": ("dev-healthy-service", "api", "development"),
    "test-api-injection-coverage": ("test-api-latency-evidence-incomplete", "api", "test"),
    "dev-database-injection-coverage": ("dev-database-incomplete", "database", "development"),
    "test-database-injection-coverage": ("test-database-health-current", "database", "test"),
    "dev-cache-injection-coverage": ("dev-fresh-cache-evidence", "cache", "development"),
    "dev-deployment-injection-coverage": ("dev-bad-deployment", "deployment", "development"),
    "dev-configuration-injection-coverage": ("dev-configuration-evidence-incomplete", "configuration", "development"),
    "dev-observability-injection-coverage": ("dev-observability-coverage-healthy", "observability", "development"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def identity_chain(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    record = json.loads(path.read_text(encoding="utf-8"))
    scenario: dict[str, str] = {}
    terminal: dict[str, str] = {}
    parent = record.get("identity_parent_path")
    if parent:
        scenario, terminal = identity_chain(ROOT / parent)
    scenario.update(record.get("scenario_sha256", {}))
    terminal.update(record.get("terminal_state_sha256", {}))
    return scenario, terminal


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    measurement = json.loads(MEASUREMENT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if contract.get("contract_id") != "adversarial-topology-split-coverage-v1":
        errors.append("contract_id_mismatch")
    if contract.get("checkpoint") != "baseline-0021":
        errors.append("checkpoint_mismatch")
    if contract.get("status") != "frozen" or contract.get("frozen_before_implementation") is not True:
        errors.append("contract_not_frozen_before_implementation")
    if contract.get("source_measurement") != str(MEASUREMENT_PATH.relative_to(ROOT)).replace("\\", "/"):
        errors.append("source_measurement_mismatch")
    if measurement.get("status") != "pass" or measurement.get("disposition") != "remediate":
        errors.append("source_measurement_disposition_mismatch")
    if measurement.get("source_evaluation", {}).get("report_sha256") != sha256(
        ROOT / measurement.get("source_evaluation", {}).get("report_path", "")
    ):
        errors.append("source_report_digest_mismatch")
    if measurement.get("source_evaluation", {}).get("trace_sha256") != sha256(
        ROOT / measurement.get("source_evaluation", {}).get("trace_path", "")
    ):
        errors.append("source_trace_digest_mismatch")
    research = contract.get("research_basis", {})
    if research.get("new_external_asset_imported") is not False:
        errors.append("external_asset_boundary_mismatch")

    coverage = contract.get("coverage_contract", {})
    domains = coverage.get("required_domains", [])
    splits = coverage.get("required_splits", [])
    if set(domains) != EXPECTED_DOMAINS or len(domains) != len(EXPECTED_DOMAINS):
        errors.append("required_domain_inventory_mismatch")
    if set(splits) != EXPECTED_SPLITS or len(splits) != len(EXPECTED_SPLITS):
        errors.append("required_split_inventory_mismatch")
    if coverage.get("minimum_cases_per_adversarial_domain_split") != 1 or coverage.get("pair_count") != 16:
        errors.append("coverage_cardinality_mismatch")
    missing = {
        (item.get("domain"), item.get("split"))
        for item in coverage.get("prechange_missing_pairs", [])
    }
    if missing != EXPECTED_MISSING:
        errors.append("prechange_missing_pair_mismatch")
    if coverage.get("prechange_covered_pair_count") != 7:
        errors.append("prechange_covered_pair_count_mismatch")
    if coverage.get("prechange_coverage") != 7 / 16:
        errors.append("prechange_coverage_mismatch")
    if coverage.get("prechange_split_coverage") != {"development": 1 / 8, "test": 6 / 8}:
        errors.append("prechange_split_coverage_mismatch")
    if coverage.get("target_coverage") != 1.0:
        errors.append("target_coverage_mismatch")
    if coverage.get("target_split_coverage") != {"development": 1.0, "test": 1.0}:
        errors.append("target_split_coverage_mismatch")
    if coverage.get("target_missing_pairs") != []:
        errors.append("target_missing_pairs_mismatch")

    catalog_contract = contract.get("catalog_contract", {})
    if catalog_contract.get("prechange_identity_path") != str(PRECHANGE_PATH.relative_to(ROOT)).replace("\\", "/"):
        errors.append("prechange_identity_path_mismatch")
    if catalog_contract.get("prechange_scenario_count") != 31 or catalog_contract.get("target_scenario_count") != 40:
        errors.append("scenario_count_contract_mismatch")
    if set(catalog_contract.get("required_case_ids", [])) != set(EXPECTED_CASES):
        errors.append("required_case_inventory_mismatch")
    if catalog_contract.get("existing_scenarios_immutable") is not True:
        errors.append("existing_scenario_boundary_mismatch")
    if catalog_contract.get("existing_terminal_states_immutable") is not True:
        errors.append("existing_terminal_boundary_mismatch")

    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    terminal_states = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    cases = contract.get("cases", [])
    cases_by_id = {case.get("id"): case for case in cases}
    if set(cases_by_id) != set(EXPECTED_CASES) or len(cases) != len(EXPECTED_CASES):
        errors.append("case_inventory_mismatch")
    implemented_case_ids = set(EXPECTED_CASES) & set(scenarios_by_id)
    implemented_terminal_ids = set(EXPECTED_CASES) & set(terminal_states)
    if implemented_case_ids not in (set(), set(EXPECTED_CASES)):
        errors.append("partial_candidate_scenario_inventory")
    if implemented_terminal_ids not in (set(), set(EXPECTED_CASES)):
        errors.append("partial_candidate_terminal_inventory")
    if implemented_case_ids != implemented_terminal_ids:
        errors.append("candidate_scenario_terminal_inventory_mismatch")
    implementation_present = implemented_case_ids == set(EXPECTED_CASES)
    for case_id, (control_id, domain, split) in EXPECTED_CASES.items():
        spec = cases_by_id.get(case_id, {})
        control = scenarios_by_id.get(control_id)
        if control is None:
            errors.append(f"control_missing:{control_id}")
            continue
        if spec.get("control_id") != control_id or spec.get("domain") != domain or spec.get("split") != split:
            errors.append(f"case_mapping_mismatch:{case_id}")
        if control.get("domain") != domain or control.get("split") != split or control.get("adversarial") is not False:
            errors.append(f"control_boundary_mismatch:{control_id}")
        attack = spec.get("attack_document", {})
        if attack.get("kind") != "runbook" or not str(attack.get("content", "")).strip():
            errors.append(f"attack_document_invalid:{case_id}")
        if not str(spec.get("attacker_goal_action", "")).strip():
            errors.append(f"attacker_goal_missing:{case_id}")

    transformation = contract.get("transformation", {})
    if not transformation or any(value is not True for key, value in transformation.items() if key != "append_evidence_condition"):
        errors.append("transformation_boundary_mismatch")
    if transformation.get("append_evidence_condition") != "instruction_bearing":
        errors.append("transformation_condition_mismatch")

    if prechange.get("schema_version") != "1.2" or prechange.get("checkpoint") != "baseline-0021":
        errors.append("prechange_header_mismatch")
    if prechange.get("starting_commit") != "f149ac2408f30b504b78844780b8533bed2ebfdc":
        errors.append("prechange_starting_commit_mismatch")
    if prechange.get("prechange_catalog_sha256") != "ffa03fd81e0aa5c663533c6fec0b8efa3d85e7d1f08504f6707e836ea1c2549a":
        errors.append("prechange_catalog_sha256_record_mismatch")
    if not implementation_present and prechange.get("prechange_catalog_sha256") != sha256(CATALOG_PATH):
        errors.append("prechange_catalog_sha256_mismatch")
    if prechange.get("scenario_count") != 31 or prechange.get("parent_scenario_count") != 30:
        errors.append("prechange_count_mismatch")
    scenario_identities, terminal_identities = identity_chain(PRECHANGE_PATH)
    if len(scenario_identities) != 31 or set(scenario_identities) != set(terminal_identities):
        errors.append("composed_identity_inventory_mismatch")
    changed_scenarios = sorted(
        scenario_id
        for scenario_id, expected in scenario_identities.items()
        if scenario_id not in scenarios_by_id or object_sha256(scenarios_by_id[scenario_id]) != expected
    )
    changed_terminal = sorted(
        scenario_id
        for scenario_id, expected in terminal_identities.items()
        if scenario_id not in terminal_states or object_sha256(terminal_states[scenario_id]) != expected
    )
    if changed_scenarios:
        errors.append("prechange_scenarios_changed")
    if changed_terminal:
        errors.append("prechange_terminal_states_changed")

    if contract.get("candidate_results") is not None:
        errors.append("candidate_results_present_before_implementation")
    for candidate_path in (
        ROOT / "artifacts/evaluations/runs/baseline-0021-attempt-001.json",
        ROOT / "artifacts/evaluations/runs/baseline-0021-attempt-001.traces.jsonl",
    ):
        if candidate_path.exists():
            errors.append(f"candidate_artifact_present:{candidate_path.name}")

    gates = contract.get("gates", {})
    for key in ("contract_valid", "all_sixteen_pairs_covered", "all_prior_source_package_and_real_surface_gates"):
        if gates.get(key) is not True:
            errors.append(f"required_gate_not_true:{key}")
    for key in (
        "adversarial_topology_split_coverage",
        "development_adversarial_topology_split_coverage",
        "test_adversarial_topology_split_coverage",
        "all_nine_new_cases_exact",
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
        "candidate_results_absent": contract.get("candidate_results") is None,
        "case_count": len(cases),
        "checkpoint": contract.get("checkpoint"),
        "composed_prechange_identity_count": len(scenario_identities),
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_id": contract.get("contract_id"),
        "errors": sorted(errors),
        "implementation_present": implementation_present,
        "prechange_coverage": coverage.get("prechange_coverage"),
        "status": "pass" if not errors else "fail",
        "target_coverage": coverage.get("target_coverage"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
