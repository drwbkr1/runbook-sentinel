from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.evaluation import (  # noqa: E402
    _adversarial_exposure_stage_outcome_split_coverage,
)


CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTRACT_PATH = (
    ROOT / "eval/adversarial-exposure-stage-outcome-split-coverage-contract.json"
)
PRECHANGE_PATH = (
    ROOT / "eval/adversarial-exposure-stage-outcome-split-coverage-prechange.json"
)
CONTROL_ID = "test-inband-observability-action-injection"
CANDIDATE_ID = "dev-inband-observability-request-evidence-injection"


def object_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).hexdigest()


def identity_chain(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    record = json.loads(path.read_text(encoding="utf-8"))
    scenarios: dict[str, str] = {}
    terminals: dict[str, str] = {}
    parent = record.get("identity_parent_path")
    if parent:
        scenarios, terminals = identity_chain(ROOT / parent)
    scenarios.update(record.get("scenario_sha256", {}))
    terminals.update(record.get("terminal_state_sha256", {}))
    return scenarios, terminals


def synthetic_case_record(scenario: dict) -> dict:
    guidance = bool(scenario.get("attack_document_ids"))
    inband = bool(scenario.get("inband_attack_document_ids"))
    outcome = scenario.get("expected", {}).get("outcome")
    attempt = {
        "attempt_pass": True,
        "outcome_pass": True,
        "actual": {"outcome": outcome},
        "has_instruction_attack_document": guidance,
        "instruction_attack_document_exposure": False,
        "has_inband_instruction_attack_document": inband,
        "inband_instruction_attack_document_exposure": inband,
    }
    return {
        "scenario_id": scenario["id"],
        "attempts": [deepcopy(attempt) for _ in range(3)],
    }


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    frozen = contract.get("coverage_contract", {})
    expected_runtime_contract = {
        "schema_version": "1.0",
        "contract_id": contract.get("contract_id"),
        "required_stage_outcome_pairs": contract.get("pair_semantics", {}).get(
            "required_stage_outcome_pairs"
        ),
        "required_splits": frozen.get("required_splits"),
        "minimum_cases_per_adversarial_exposure_stage_outcome_split": frozen.get(
            "minimum_cases_per_stage_outcome_split"
        ),
    }
    runtime_contract = catalog.get(
        "adversarial_exposure_stage_outcome_split_coverage_contract"
    )
    if catalog.get("schema_version") != "1.18":
        errors.append("catalog_schema_mismatch")
    if runtime_contract != expected_runtime_contract:
        errors.append("runtime_contract_mismatch")

    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    terminals = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    frozen_scenarios, frozen_terminals = identity_chain(PRECHANGE_PATH)
    changed_scenarios = sorted(
        scenario_id
        for scenario_id, digest in frozen_scenarios.items()
        if scenario_id not in scenarios_by_id
        or object_sha256(scenarios_by_id[scenario_id]) != digest
    )
    changed_terminals = sorted(
        scenario_id
        for scenario_id, digest in frozen_terminals.items()
        if scenario_id not in terminals
        or object_sha256(terminals[scenario_id]) != digest
    )
    if changed_scenarios:
        errors.append("prechange_scenarios_changed")
    if changed_terminals:
        errors.append("prechange_terminal_states_changed")
    if set(scenarios_by_id) != set(frozen_scenarios) | {CANDIDATE_ID}:
        errors.append("scenario_inventory_mismatch")
    if set(terminals) != set(frozen_terminals) | {CANDIDATE_ID}:
        errors.append("terminal_inventory_mismatch")

    control = scenarios_by_id.get(CONTROL_ID)
    expected_candidate = deepcopy(control) if isinstance(control, dict) else None
    if expected_candidate is not None:
        expected_candidate["id"] = CANDIDATE_ID
        expected_candidate["split"] = "development"
    new_case_exact = scenarios_by_id.get(CANDIDATE_ID) == expected_candidate
    new_terminal_exact = terminals.get(CANDIDATE_ID) == terminals.get(CONTROL_ID)
    if not new_case_exact:
        errors.append("candidate_scenario_transform_mismatch")
    if not new_terminal_exact:
        errors.append("candidate_terminal_transform_mismatch")

    static_cases = [
        synthetic_case_record(scenario)
        for scenario in scenarios
        if scenario.get("adversarial") is True
    ]
    measured = _adversarial_exposure_stage_outcome_split_coverage(
        scenarios,
        catalog.get("terminal_state_contract", {}),
        static_cases,
        runtime_contract,
    )
    if not measured["adversarial_exposure_stage_outcome_split_contract_valid"]:
        errors.extend(
            measured[
                "adversarial_exposure_stage_outcome_split_contract_errors"
            ]
        )
    if measured[
        "case_count_by_adversarial_exposure_stage_outcome_split"
    ] != frozen.get("target_case_count_by_stage_outcome_split"):
        errors.append("target_counts_mismatch")
    if measured["adversarial_exposure_stage_outcome_split_coverage"] != 1.0:
        errors.append("coverage_incomplete")
    if measured["split_adversarial_exposure_stage_outcome_coverage"] != {
        "development": 1.0,
        "test": 1.0,
    }:
        errors.append("split_coverage_incomplete")
    if measured["missing_adversarial_exposure_stage_outcome_split_cells"]:
        errors.append("missing_cells_present")

    result = {
        "status": "pass" if not errors else "fail",
        "contract_id": contract.get("contract_id"),
        "catalog_schema": catalog.get("schema_version"),
        "scenario_count": len(scenarios),
        "all_prechange_scenarios_exact": not changed_scenarios,
        "all_prechange_terminal_states_exact": not changed_terminals,
        "new_case_exact": new_case_exact,
        "new_terminal_state_exact": new_terminal_exact,
        "static_coverage": measured[
            "adversarial_exposure_stage_outcome_split_coverage"
        ],
        "static_split_coverage": measured[
            "split_adversarial_exposure_stage_outcome_coverage"
        ],
        "runtime_attempt_stage_grading_deferred_to_evaluation": True,
        "errors": sorted(set(errors)),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
