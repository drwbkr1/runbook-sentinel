from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTRACT_PATH = ROOT / "eval/topology-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/topology-split-coverage-prechange.json"


def _sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if catalog.get("schema_version") != "1.11":
        errors.append("catalog_schema_mismatch")
    runtime_contract = catalog.get("topology_split_coverage_contract")
    frozen_coverage = contract.get("coverage_contract", {})
    expected_runtime_contract = {
        "schema_version": "1.0",
        "contract_id": "topology-split-coverage-v1",
        "required_domains": frozen_coverage.get("required_domains"),
        "required_splits": frozen_coverage.get("required_splits"),
        "minimum_cases_per_domain_split": frozen_coverage.get(
            "minimum_cases_per_domain_split"
        ),
    }
    if runtime_contract != expected_runtime_contract:
        errors.append("runtime_contract_mismatch")

    scenarios = catalog.get("scenarios", [])
    terminal_states = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    if len(scenarios) < 30 or len(scenarios_by_id) != len(scenarios):
        errors.append("scenario_inventory_mismatch")

    prechange_scenarios = prechange.get("scenario_sha256", {})
    prechange_terminal_states = prechange.get("terminal_state_sha256", {})
    changed_prechange_scenarios = sorted(
        scenario_id
        for scenario_id, expected in prechange_scenarios.items()
        if scenario_id not in scenarios_by_id or _sha256(scenarios_by_id[scenario_id]) != expected
    )
    changed_prechange_terminal_states = sorted(
        scenario_id
        for scenario_id, expected in prechange_terminal_states.items()
        if scenario_id not in terminal_states or _sha256(terminal_states[scenario_id]) != expected
    )
    if changed_prechange_scenarios:
        errors.append("prechange_scenarios_changed")
    if changed_prechange_terminal_states:
        errors.append("prechange_terminal_states_changed")

    frozen_cases = {case["id"]: case for case in contract.get("cases", [])}
    required_new_ids = set(frozen_cases)
    actual_new_ids = set(scenarios_by_id) - set(prechange_scenarios)
    actual_new_terminal_ids = set(terminal_states) - set(prechange_terminal_states)
    if not required_new_ids.issubset(actual_new_ids):
        errors.append("new_scenario_inventory_mismatch")
    if not required_new_ids.issubset(actual_new_terminal_ids):
        errors.append("new_terminal_state_inventory_mismatch")
    new_case_exact: dict[str, bool] = {}
    for scenario_id, frozen_case in frozen_cases.items():
        expected_scenario = {
            key: value
            for key, value in frozen_case.items()
            if key != "terminal_state"
        }
        scenario_exact = scenarios_by_id.get(scenario_id) == expected_scenario
        terminal_exact = terminal_states.get(scenario_id) == frozen_case.get("terminal_state")
        new_case_exact[scenario_id] = scenario_exact and terminal_exact
        if not scenario_exact:
            errors.append(f"{scenario_id}:scenario_mismatch")
        if not terminal_exact:
            errors.append(f"{scenario_id}:terminal_state_mismatch")

    required_domains = runtime_contract.get("required_domains", []) if isinstance(runtime_contract, dict) else []
    required_splits = runtime_contract.get("required_splits", []) if isinstance(runtime_contract, dict) else []
    minimum = runtime_contract.get("minimum_cases_per_domain_split") if isinstance(runtime_contract, dict) else None
    counts = {
        domain: {split: 0 for split in required_splits}
        for domain in required_domains
    }
    for scenario in scenarios:
        domain = scenario.get("domain")
        split = scenario.get("split")
        if domain in counts and split in counts[domain]:
            counts[domain][split] += 1
    missing_pairs = [
        {"domain": domain, "split": split}
        for domain in required_domains
        for split in required_splits
        if not isinstance(minimum, int) or counts[domain][split] < minimum
    ]
    pair_count = len(required_domains) * len(required_splits)
    coverage = (pair_count - len(missing_pairs)) / pair_count if pair_count else 0.0
    split_coverage = {
        split: (
            sum(
                isinstance(minimum, int) and counts[domain][split] >= minimum
                for domain in required_domains
            )
            / len(required_domains)
            if required_domains
            else 0.0
        )
        for split in required_splits
    }
    if coverage != 1.0 or missing_pairs:
        errors.append("topology_split_coverage_incomplete")
    if any(value != 1.0 for value in split_coverage.values()):
        errors.append("per_split_topology_coverage_incomplete")

    result = {
        "all_prechange_scenarios_exact": not changed_prechange_scenarios,
        "all_prechange_terminal_states_exact": not changed_prechange_terminal_states,
        "case_count_by_domain_split": counts,
        "catalog_schema": catalog.get("schema_version"),
        "changed_prechange_scenarios": changed_prechange_scenarios,
        "changed_prechange_terminal_states": changed_prechange_terminal_states,
        "contract_id": contract.get("contract_id"),
        "errors": sorted(errors),
        "missing_domain_split_pairs": missing_pairs,
        "new_case_exact": new_case_exact,
        "scenario_count": len(scenarios),
        "split_topology_coverage": split_coverage,
        "status": "pass" if not errors else "fail",
        "topology_split_coverage": coverage,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
