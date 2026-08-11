from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
TRANSFORMS = [
    ("dev-api-request-evidence-injection-coverage", "test-api-injection-coverage", "development"),
    ("dev-configuration-conflict-injection-coverage", "test-configuration-conflict", "development"),
    ("dev-database-diagnose-injection-coverage", "test-database-injection-coverage", "development"),
    ("dev-deployment-conflict-injection-coverage", "test-conflicting-deployment-evidence-inband-injection", "development"),
    ("dev-deployment-request-evidence-injection-coverage", "test-stale-deployment-evidence", "development"),
    ("dev-observability-request-evidence-injection-coverage", "test-injection-without-telemetry", "development"),
    ("test-api-diagnose-injection-coverage", "dev-api-injection-coverage", "test"),
    ("test-cache-request-evidence-injection-coverage", "dev-stale-cache-poisoning", "test"),
    ("test-configuration-request-evidence-injection-coverage", "dev-configuration-injection-coverage", "test"),
    ("test-database-conflict-injection-coverage", "dev-conflicting-database-evidence-inband-injection", "test"),
    ("test-database-request-evidence-injection-coverage", "dev-database-injection-coverage", "test"),
    ("test-observability-diagnose-injection-coverage", "dev-observability-injection-coverage", "test"),
]


def indent(value: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line for line in value.splitlines())


def render_terminal_entry(case_id: str, value: dict) -> str:
    lines = json.dumps(value, indent=2, ensure_ascii=False).splitlines()
    rendered = [f'      {json.dumps(case_id)}: {lines[0]}']
    rendered.extend("      " + line for line in lines[1:])
    return "\n".join(rendered)


def expected_scenario(control: dict, case_id: str, split: str) -> dict:
    candidate = copy.deepcopy(control)
    candidate["id"] = case_id
    candidate["split"] = split
    return candidate


def main() -> None:
    raw = CATALOG_PATH.read_text(encoding="utf-8")
    catalog = json.loads(raw)
    scenarios = catalog["scenarios"]
    terminal_states = catalog["terminal_state_contract"]["scenarios"]
    scenarios_by_id = {scenario["id"]: scenario for scenario in scenarios}
    present = [case_id in scenarios_by_id for case_id, _, _ in TRANSFORMS]
    terminal_present = [case_id in terminal_states for case_id, _, _ in TRANSFORMS]
    if any(present) or any(terminal_present):
        if not all(present) or not all(terminal_present):
            raise SystemExit("Partial BASELINE-0025 catalog materialization detected")
        for case_id, control_id, split in TRANSFORMS:
            if scenarios_by_id[case_id] != expected_scenario(
                scenarios_by_id[control_id], case_id, split
            ):
                raise SystemExit(f"Scenario transform mismatch: {case_id}")
            if terminal_states[case_id] != terminal_states[control_id]:
                raise SystemExit(f"Terminal transform mismatch: {case_id}")
        print(json.dumps({"status": "already_exact", "case_count": len(TRANSFORMS)}))
        return

    new_scenarios = []
    new_terminal_states = []
    for case_id, control_id, split in TRANSFORMS:
        control = scenarios_by_id[control_id]
        new_scenarios.append(expected_scenario(control, case_id, split))
        new_terminal_states.append((case_id, copy.deepcopy(terminal_states[control_id])))

    terminal_marker = '\n    }\n  },\n  "scenarios": ['
    if raw.count(terminal_marker) != 1:
        raise SystemExit("Terminal-state insertion marker is not unique")
    terminal_text = ",\n".join(
        render_terminal_entry(case_id, value)
        for case_id, value in new_terminal_states
    )
    raw = raw.replace(
        terminal_marker,
        ",\n" + terminal_text + terminal_marker,
        1,
    )

    scenario_marker = "\n  ]\n}\n"
    if raw.count(scenario_marker) != 1:
        raise SystemExit("Scenario insertion marker is not unique")
    scenario_text = ",\n".join(
        indent(json.dumps(scenario, indent=2, ensure_ascii=False), 4)
        for scenario in new_scenarios
    )
    raw = raw.replace(scenario_marker, ",\n" + scenario_text + scenario_marker, 1)
    CATALOG_PATH.write_text(raw, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "materialized", "case_count": len(TRANSFORMS)}))


if __name__ == "__main__":
    main()
