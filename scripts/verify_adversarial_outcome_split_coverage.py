from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTRACT_PATH = ROOT / "eval/adversarial-outcome-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/adversarial-outcome-split-coverage-prechange.json"


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


def expected_transform(control: dict, case: dict) -> dict:
    transformed = deepcopy(control)
    attack = deepcopy(case["attack_document"])
    transformed["id"] = case["id"]
    transformed["adversarial"] = True
    transformed["evidence_conditions"].append("instruction_bearing")
    transformed["inband_attack_document_ids"] = [attack["id"]]
    transformed["documents"] = [deepcopy(control["documents"][0]), attack]
    transformed["expected"] = deepcopy(case["expected"])
    return transformed


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    frozen = contract.get("coverage_contract", {})
    expected_runtime_contract = {
        "schema_version": "1.0",
        "contract_id": contract.get("contract_id"),
        "required_outcomes": frozen.get("required_outcomes"),
        "required_splits": frozen.get("required_splits"),
        "minimum_cases_per_adversarial_outcome_split": frozen.get(
            "minimum_cases_per_adversarial_outcome_split"
        ),
    }
    runtime_contract = catalog.get("adversarial_outcome_split_coverage_contract")
    if catalog.get("schema_version") != "1.18":
        errors.append("catalog_schema_mismatch")
    if runtime_contract != expected_runtime_contract:
        errors.append("runtime_contract_mismatch")

    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    terminal_states = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    if len(scenarios) != 57 or len(scenarios_by_id) != 57:
        errors.append("scenario_inventory_mismatch")
    if len(terminal_states) != 57:
        errors.append("terminal_inventory_mismatch")

    prechange_scenarios, prechange_terminal_states = identity_chain(PRECHANGE_PATH)
    changed_scenarios = sorted(
        scenario_id
        for scenario_id, expected in prechange_scenarios.items()
        if scenario_id not in scenarios_by_id
        or object_sha256(scenarios_by_id[scenario_id]) != expected
    )
    changed_terminal_states = sorted(
        scenario_id
        for scenario_id, expected in prechange_terminal_states.items()
        if scenario_id not in terminal_states
        or object_sha256(terminal_states[scenario_id]) != expected
    )
    if changed_scenarios:
        errors.append("prechange_scenarios_changed")
    if changed_terminal_states:
        errors.append("prechange_terminal_states_changed")

    frozen_cases = {case["id"]: case for case in contract.get("cases", [])}
    new_ids = set(scenarios_by_id) - set(prechange_scenarios)
    new_terminal_ids = set(terminal_states) - set(prechange_terminal_states)
    if not set(frozen_cases).issubset(new_ids):
        errors.append("frozen_scenario_inventory_missing")
    if not set(frozen_cases).issubset(new_terminal_ids):
        errors.append("frozen_terminal_inventory_missing")

    new_case_exact: dict[str, bool] = {}
    inband_document_exact: dict[str, bool] = {}
    for scenario_id, case in frozen_cases.items():
        control_id = case.get("control_id")
        control = scenarios_by_id.get(control_id)
        expected = expected_transform(control, case) if isinstance(control, dict) else None
        scenario_exact = scenarios_by_id.get(scenario_id) == expected
        terminal_exact = terminal_states.get(scenario_id) == case.get(
            "expected_terminal_state"
        )
        inband_exact = bool(
            scenario_exact
            and scenarios_by_id[scenario_id].get("inband_attack_document_ids")
            == [case["attack_document"]["id"]]
            and scenarios_by_id[scenario_id]["expected"]["retrieval_ids"]
            == ["telemetry-db-conflict-a", case["attack_document"]["id"]]
        )
        new_case_exact[scenario_id] = scenario_exact and terminal_exact
        inband_document_exact[scenario_id] = inband_exact
        if not scenario_exact:
            errors.append(f"{scenario_id}:scenario_mismatch")
        if not terminal_exact:
            errors.append(f"{scenario_id}:terminal_state_mismatch")
        if not inband_exact:
            errors.append(f"{scenario_id}:inband_document_mismatch")

    outcomes = (
        runtime_contract.get("required_outcomes", [])
        if isinstance(runtime_contract, dict)
        else []
    )
    splits = (
        runtime_contract.get("required_splits", [])
        if isinstance(runtime_contract, dict)
        else []
    )
    minimum = (
        runtime_contract.get("minimum_cases_per_adversarial_outcome_split")
        if isinstance(runtime_contract, dict)
        else None
    )
    counts = {outcome: {split: 0 for split in splits} for outcome in outcomes}
    historical_ids = set(prechange_scenarios) | set(frozen_cases)
    for scenario in scenarios:
        if scenario.get("id") not in historical_ids:
            continue
        if scenario.get("adversarial") is not True:
            continue
        outcome = scenario.get("expected", {}).get("outcome")
        split = scenario.get("split")
        scenario_id = scenario.get("id")
        terminal = terminal_states.get(scenario_id, {})
        if outcome not in counts or split not in counts[outcome]:
            errors.append(f"{scenario_id}:outcome_or_split")
            continue
        action = scenario.get("expected", {}).get("action")
        if outcome == "propose_action":
            terminal_exact = (
                action is not None
                and terminal.get("execute") is True
                and terminal.get("action") == action
            )
        else:
            terminal_exact = (
                action is None
                and terminal.get("execute") is False
                and terminal.get("action") is None
            )
        if not terminal_exact:
            errors.append(f"{scenario_id}:terminal_outcome")
            continue
        counts[outcome][split] += 1
    threshold = minimum if isinstance(minimum, int) and not isinstance(minimum, bool) else 1
    missing_pairs = [
        {"outcome": outcome, "split": split}
        for outcome in outcomes
        for split in splits
        if counts[outcome][split] < threshold
    ]
    pair_count = len(outcomes) * len(splits)
    coverage = (pair_count - len(missing_pairs)) / pair_count if pair_count else 0.0
    split_coverage = {
        split: (
            sum(counts[outcome][split] >= threshold for outcome in outcomes)
            / len(outcomes)
            if outcomes
            else 0.0
        )
        for split in splits
    }
    if counts != frozen.get("target_case_count_by_adversarial_outcome_split"):
        errors.append("target_counts_mismatch")
    if coverage != 1.0 or missing_pairs:
        errors.append("adversarial_outcome_split_coverage_incomplete")
    if split_coverage != {"development": 1.0, "test": 1.0}:
        errors.append("per_split_adversarial_outcome_coverage_incomplete")

    result = {
        "adversarial_outcome_split_coverage": coverage,
        "all_prechange_scenarios_exact": not changed_scenarios,
        "all_prechange_terminal_states_exact": not changed_terminal_states,
        "case_count_by_adversarial_outcome_split": counts,
        "catalog_schema": catalog.get("schema_version"),
        "changed_prechange_scenarios": changed_scenarios,
        "changed_prechange_terminal_states": changed_terminal_states,
        "contract_id": contract.get("contract_id"),
        "errors": sorted(set(errors)),
        "inband_document_exact": inband_document_exact,
        "missing_adversarial_outcome_split_pairs": missing_pairs,
        "new_case_exact": new_case_exact,
        "scenario_count": len(scenarios),
        "split_adversarial_outcome_coverage": split_coverage,
        "status": "pass" if not errors else "fail",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
