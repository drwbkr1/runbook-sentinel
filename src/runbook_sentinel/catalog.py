from __future__ import annotations

import json
from importlib.resources import files


def load_scenarios() -> list[dict]:
    data_path = files("runbook_sentinel").joinpath("data/scenarios.json")
    return json.loads(data_path.read_text(encoding="utf-8"))["scenarios"]


def scenario_by_id(scenario_id: str) -> dict:
    for scenario in load_scenarios():
        if scenario["id"] == scenario_id:
            return scenario
    raise KeyError(scenario_id)
