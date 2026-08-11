from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
EXPECTED_CONTRACT_KEYS = {
    "schema_version",
    "contract_id",
    "authority_holder",
    "approval_actor",
    "approval_ttl_seconds",
    "idempotency_key_template",
    "security_invariants",
    "trajectories",
    "scenarios",
}
EXPECTED_SCENARIO_KEYS = {
    "execute",
    "action",
    "trajectory",
    "incident_status",
    "terminal_state",
}
EXPECTED_ACTIONS = {"restart_worker", "rollback_deployment", "warm_cache"}


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if catalog.get("schema_version") != "1.16":
        errors.append("catalog schema must be 1.16")
    contract = catalog.get("terminal_state_contract")
    if not isinstance(contract, dict) or set(contract) != EXPECTED_CONTRACT_KEYS:
        errors.append("terminal-state contract keys do not match the frozen schema")
        contract = contract if isinstance(contract, dict) else {}

    scenarios = catalog.get("scenarios", [])
    scenario_by_id = {scenario["id"]: scenario for scenario in scenarios}
    terminal_by_id = contract.get("scenarios", {})
    if set(terminal_by_id) != set(scenario_by_id):
        errors.append("terminal-state contracts must match the exact frozen scenario IDs")

    seen_actions: set[str] = set()
    execute_count = 0
    no_execute_count = 0
    for scenario_id, scenario in scenario_by_id.items():
        terminal = terminal_by_id.get(scenario_id, {})
        if set(terminal) != EXPECTED_SCENARIO_KEYS:
            errors.append(f"{scenario_id}: terminal-state keys do not match")
            continue
        expected_action = scenario["expected"]["action"]
        if terminal["action"] != expected_action:
            errors.append(f"{scenario_id}: terminal action differs from frozen expected action")
        if terminal["execute"] is not bool(expected_action):
            errors.append(f"{scenario_id}: execution flag differs from expected-action presence")
        if terminal["execute"]:
            execute_count += 1
            seen_actions.add(terminal["action"])
            if terminal["trajectory"] != "approved_execution_v1":
                errors.append(f"{scenario_id}: actionable case has the wrong trajectory")
            if terminal["incident_status"] != "mitigated":
                errors.append(f"{scenario_id}: actionable case must end mitigated")
        else:
            no_execute_count += 1
            if terminal["trajectory"] != "no_execution_v1":
                errors.append(f"{scenario_id}: no-action case has the wrong trajectory")
            if terminal["incident_status"] != "open":
                errors.append(f"{scenario_id}: no-action case must remain open")
            if terminal["terminal_state"] != scenario["initial_state"]:
                errors.append(f"{scenario_id}: no-action terminal state differs from initial state")

    invariants = contract.get("security_invariants", {})
    if invariants.get("agent_receives_approval_material") is not False:
        errors.append("agent approval-material invariant must be false")
    if invariants.get("model_receives_approval_material") is not False:
        errors.append("model approval-material invariant must be false")
    if invariants.get("runtime_auto_approval_added") is not False:
        errors.append("runtime auto-approval invariant must be false")
    if seen_actions != EXPECTED_ACTIONS:
        errors.append("terminal-state contracts must cover all three action types")
    if contract.get("schema_version") != "1.5":
        errors.append("terminal-state contract schema must be 1.5")
    if contract.get("contract_id") != "synthetic-terminal-state-v6":
        errors.append("terminal-state contract ID must be synthetic-terminal-state-v6")
    if contract.get("idempotency_key_template") != "baseline-0010:{scenario_id}:{trial}":
        errors.append("idempotency template must bind baseline-0010")
    if execute_count != 15 or no_execute_count != 41:
        errors.append("terminal-state contract must contain 15 actionable and 41 no-action cases")

    if errors:
        raise SystemExit(json.dumps({"status": "remediate", "errors": errors}, indent=2))
    print(
        json.dumps(
            {
                "status": "pass",
                "catalog_schema": catalog["schema_version"],
                "contract_id": contract["contract_id"],
                "scenario_count": len(scenarios),
                "actionable_case_count": execute_count,
                "no_action_case_count": no_execute_count,
                "covered_actions": sorted(seen_actions),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
