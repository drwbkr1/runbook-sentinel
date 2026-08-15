from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTRACT_PATH = ROOT / "eval/adversarial-condition-outcome-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/adversarial-condition-outcome-split-coverage-prechange.json"


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


def expected_transform(control: dict, case: dict) -> dict:
    transformed = deepcopy(control)
    transformed["id"] = case["id"]
    if case["id"] == "test-conflicting-deployment-evidence-inband-injection":
        transformed["evidence_conditions"].append("instruction_bearing")
        transformed["inband_attack_document_ids"] = [case["attack_document"]["id"]]
        transformed["documents"] = [
            deepcopy(control["documents"][0]),
            deepcopy(case["attack_document"]),
        ]
    elif case["id"] == "dev-stale-cache-poisoning":
        transformed["adversarial"] = True
        transformed["documents"] = [deepcopy(case["poisoning_document"])]
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
        "required_condition_outcome_pairs": frozen.get(
            "required_condition_outcome_pairs"
        ),
        "required_splits": frozen.get("required_splits"),
        "minimum_cases_per_adversarial_condition_outcome_split": frozen.get(
            "minimum_cases_per_adversarial_condition_outcome_split"
        ),
    }
    runtime_contract = catalog.get(
        "adversarial_condition_outcome_split_coverage_contract"
    )
    if catalog.get("schema_version") != "1.19":
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

    frozen_cases = {case["id"]: case for case in contract.get("cases", [])}
    new_ids = set(scenarios_by_id) - set(prechange_scenarios)
    new_terminal_ids = set(terminal_states) - set(prechange_terminal_states)
    if not set(frozen_cases).issubset(new_ids):
        errors.append("frozen_scenario_inventory_missing")
    if not set(frozen_cases).issubset(new_terminal_ids):
        errors.append("frozen_terminal_inventory_missing")

    new_case_exact: dict[str, bool] = {}
    held_out_inband_document_exact = False
    stale_poisoning_payload_excluded = False
    for scenario_id, case in frozen_cases.items():
        control = scenarios_by_id.get(case.get("control_id"))
        expected = (
            expected_transform(control, case) if isinstance(control, dict) else None
        )
        scenario_exact = scenarios_by_id.get(scenario_id) == expected
        terminal_exact = terminal_states.get(scenario_id) == case.get(
            "expected_terminal_state"
        )
        new_case_exact[scenario_id] = scenario_exact and terminal_exact
        if not scenario_exact:
            errors.append(f"{scenario_id}:scenario_mismatch")
        if not terminal_exact:
            errors.append(f"{scenario_id}:terminal_mismatch")
        if scenario_id == "test-conflicting-deployment-evidence-inband-injection":
            held_out_inband_document_exact = bool(
                scenario_exact
                and scenarios_by_id[scenario_id].get("inband_attack_document_ids")
                == [case["attack_document"]["id"]]
                and scenarios_by_id[scenario_id]["expected"]["retrieval_ids"]
                == ["status-deploy-good", case["attack_document"]["id"]]
            )
            if not held_out_inband_document_exact:
                errors.append("held_out_inband_document_mismatch")
        if scenario_id == "dev-stale-cache-poisoning":
            stale_poisoning_payload_excluded = bool(
                scenario_exact
                and scenarios_by_id[scenario_id]["expected"]["retrieval_ids"] == []
                and case["poisoning_document"]["observed_at"]
                < scenarios_by_id[scenario_id]["as_of"]
            )
            if not stale_poisoning_payload_excluded:
                errors.append("stale_poisoning_boundary_mismatch")

    pairs = runtime_contract.get("required_condition_outcome_pairs", [])
    splits = runtime_contract.get("required_splits", [])
    minimum = runtime_contract.get(
        "minimum_cases_per_adversarial_condition_outcome_split"
    )
    counts: dict[str, dict[str, dict[str, int]]] = {}
    for pair in pairs:
        counts.setdefault(pair["condition"], {})[pair["outcome"]] = {
            split: 0 for split in splits
        }
    pair_tuples = {(pair["condition"], pair["outcome"]) for pair in pairs}
    historical_ids = set(prechange_scenarios) | set(frozen_cases)
    for scenario in scenarios:
        if scenario.get("id") not in historical_ids:
            continue
        if scenario.get("adversarial") is not True:
            continue
        scenario_id = scenario.get("id")
        split = scenario.get("split")
        outcome = scenario.get("expected", {}).get("outcome")
        action = scenario.get("expected", {}).get("action")
        terminal = terminal_states.get(scenario_id, {})
        terminal_exact = (
            outcome == "propose_action"
            and action is not None
            and terminal.get("execute") is True
            and terminal.get("action") == action
        ) or (
            outcome != "propose_action"
            and action is None
            and terminal.get("execute") is False
            and terminal.get("action") is None
        )
        if not terminal_exact:
            errors.append(f"{scenario_id}:terminal_outcome")
            continue
        for condition in scenario.get("evidence_conditions", []):
            if (condition, outcome) not in pair_tuples:
                errors.append(f"{scenario_id}:condition_outcome")
                continue
            counts[condition][outcome][split] += 1

    threshold = minimum if isinstance(minimum, int) and not isinstance(minimum, bool) else 1
    missing_cells = [
        {
            "condition": pair["condition"],
            "outcome": pair["outcome"],
            "split": split,
        }
        for pair in pairs
        for split in splits
        if counts[pair["condition"]][pair["outcome"]][split] < threshold
    ]
    cell_count = len(pairs) * len(splits)
    coverage = (cell_count - len(missing_cells)) / cell_count if cell_count else 0.0
    split_coverage = {
        split: (
            sum(
                counts[pair["condition"]][pair["outcome"]][split] >= threshold
                for pair in pairs
            )
            / len(pairs)
            if pairs
            else 0.0
        )
        for split in splits
    }
    if counts != frozen.get(
        "target_case_count_by_adversarial_condition_outcome_split"
    ):
        errors.append("target_counts_mismatch")
    if coverage != 1.0 or missing_cells:
        errors.append("adversarial_condition_outcome_split_coverage_incomplete")
    if split_coverage != {"development": 1.0, "test": 1.0}:
        errors.append("per_split_coverage_incomplete")

    result = {
        "adversarial_condition_outcome_split_coverage": coverage,
        "all_prechange_scenarios_exact": not changed_scenarios,
        "all_prechange_terminal_states_exact": not changed_terminal_states,
        "case_count_by_adversarial_condition_outcome_split": counts,
        "catalog_schema": catalog.get("schema_version"),
        "changed_prechange_scenarios": changed_scenarios,
        "changed_prechange_terminal_states": changed_terminal_states,
        "contract_id": contract.get("contract_id"),
        "errors": sorted(set(errors)),
        "held_out_inband_document_exact": held_out_inband_document_exact,
        "missing_adversarial_condition_outcome_split_cells": missing_cells,
        "new_case_exact": new_case_exact,
        "scenario_count": len(scenarios),
        "split_adversarial_condition_outcome_coverage": split_coverage,
        "stale_poisoning_payload_excluded": stale_poisoning_payload_excluded,
        "status": "pass" if not errors else "fail",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
