from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.evaluation import (  # noqa: E402
    _adversarial_domain_outcome_split_coverage,
)


CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTRACT_PATH = ROOT / "eval/adversarial-domain-outcome-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/adversarial-domain-outcome-split-coverage-prechange.json"


def object_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).hexdigest()


def identity_chain(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    record = json.loads(path.read_text(encoding="utf-8"))
    scenarios: dict[str, str] = {}
    terminal_states: dict[str, str] = {}
    parent = record.get("identity_parent_path")
    if parent:
        scenarios, terminal_states = identity_chain(ROOT / parent)
    scenarios.update(record.get("scenario_sha256", {}))
    terminal_states.update(record.get("terminal_state_sha256", {}))
    return scenarios, terminal_states


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    pair_semantics = contract.get("pair_semantics", {})
    frozen = contract.get("coverage_contract", {})
    expected_runtime_contract = {
        "schema_version": "1.0",
        "contract_id": contract.get("contract_id"),
        "required_domain_outcome_pairs": pair_semantics.get(
            "required_domain_outcome_pairs"
        ),
        "required_splits": frozen.get("required_splits"),
        "minimum_cases_per_adversarial_domain_outcome_split": frozen.get(
            "minimum_cases_per_adversarial_domain_outcome_split"
        ),
    }
    runtime_contract = catalog.get(
        "adversarial_domain_outcome_split_coverage_contract"
    )
    if catalog.get("schema_version") != "1.17":
        errors.append("catalog_schema_mismatch")
    if runtime_contract != expected_runtime_contract:
        errors.append("runtime_contract_mismatch")

    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    terminal_states = catalog.get("terminal_state_contract", {}).get(
        "scenarios", {}
    )
    if len(scenarios) != 57 or len(scenarios_by_id) != 57:
        errors.append("scenario_inventory_mismatch")
    if len(terminal_states) != 57:
        errors.append("terminal_inventory_mismatch")

    prechange_scenarios, prechange_terminal_states = identity_chain(PRECHANGE_PATH)
    changed_scenarios = sorted(
        scenario_id
        for scenario_id, digest in prechange_scenarios.items()
        if scenario_id not in scenarios_by_id
        or object_sha256(scenarios_by_id[scenario_id]) != digest
    )
    changed_terminal_states = sorted(
        scenario_id
        for scenario_id, digest in prechange_terminal_states.items()
        if scenario_id not in terminal_states
        or object_sha256(terminal_states[scenario_id]) != digest
    )
    if changed_scenarios:
        errors.append("prechange_scenarios_changed")
    if changed_terminal_states:
        errors.append("prechange_terminal_states_changed")

    transformations = {
        item["id"]: item for item in contract.get("transformations", [])
    }
    new_ids = set(scenarios_by_id) - set(prechange_scenarios)
    new_terminal_ids = set(terminal_states) - set(prechange_terminal_states)
    if not set(transformations).issubset(new_ids):
        errors.append("frozen_scenario_inventory_missing")
    if not set(transformations).issubset(new_terminal_ids):
        errors.append("frozen_terminal_inventory_missing")

    new_case_exact: dict[str, bool] = {}
    for scenario_id, transformation in transformations.items():
        control = scenarios_by_id.get(transformation.get("control_id"))
        expected = deepcopy(control) if isinstance(control, dict) else None
        if expected is not None:
            expected["id"] = scenario_id
            expected["split"] = transformation["target_split"]
        scenario = scenarios_by_id.get(scenario_id)
        scenario_exact = scenario == expected
        terminal_exact = bool(
            isinstance(control, dict)
            and terminal_states.get(scenario_id)
            == terminal_states.get(transformation["control_id"])
        )
        semantic_exact = bool(
            isinstance(scenario, dict)
            and scenario.get("domain") == transformation["domain"]
            and scenario.get("expected", {}).get("outcome")
            == transformation["outcome"]
        )
        new_case_exact[scenario_id] = (
            scenario_exact and terminal_exact and semantic_exact
        )
        if not scenario_exact:
            errors.append(f"{scenario_id}:scenario_mismatch")
        if not terminal_exact:
            errors.append(f"{scenario_id}:terminal_mismatch")
        if not semantic_exact:
            errors.append(f"{scenario_id}:semantic_mismatch")

    historical_ids = set(prechange_scenarios) | set(transformations)
    historical_scenarios = [
        scenario for scenario in scenarios if scenario.get("id") in historical_ids
    ]
    historical_terminal_contract = {
        **catalog.get("terminal_state_contract", {}),
        "scenarios": {
            scenario_id: terminal_states[scenario_id]
            for scenario_id in historical_ids
        },
    }
    measured = _adversarial_domain_outcome_split_coverage(
        historical_scenarios,
        historical_terminal_contract,
        runtime_contract,
    )
    if not measured["adversarial_domain_outcome_split_contract_valid"]:
        errors.extend(measured["adversarial_domain_outcome_split_contract_errors"])
    if measured["case_count_by_adversarial_domain_outcome_split"] != frozen.get(
        "target_case_count_by_adversarial_domain_outcome_split"
    ):
        errors.append("target_counts_mismatch")
    if measured["adversarial_domain_outcome_split_coverage"] != 1.0:
        errors.append("adversarial_domain_outcome_split_coverage_incomplete")
    if measured["split_adversarial_domain_outcome_coverage"] != {
        "development": 1.0,
        "test": 1.0,
    }:
        errors.append("per_split_coverage_incomplete")
    if measured["missing_adversarial_domain_outcome_split_cells"]:
        errors.append("missing_cells_present")

    result = {
        "adversarial_domain_outcome_split_coverage": measured[
            "adversarial_domain_outcome_split_coverage"
        ],
        "all_prechange_scenarios_exact": not changed_scenarios,
        "all_prechange_terminal_states_exact": not changed_terminal_states,
        "case_count_by_adversarial_domain_outcome_split": measured[
            "case_count_by_adversarial_domain_outcome_split"
        ],
        "catalog_schema": catalog.get("schema_version"),
        "changed_prechange_scenarios": changed_scenarios,
        "changed_prechange_terminal_states": changed_terminal_states,
        "contract_id": contract.get("contract_id"),
        "errors": sorted(set(errors)),
        "missing_adversarial_domain_outcome_split_cells": measured[
            "missing_adversarial_domain_outcome_split_cells"
        ],
        "new_case_exact": new_case_exact,
        "scenario_count": len(scenarios),
        "split_adversarial_domain_outcome_coverage": measured[
            "split_adversarial_domain_outcome_coverage"
        ],
        "status": "pass" if not errors else "fail",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
