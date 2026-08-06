from __future__ import annotations

from copy import deepcopy

from .errors import PolicyRejected


ACTION_SPECS = {
    "restart_worker": {
        "capability": "synthetic.worker.restart",
        "preconditions": ["worker_healthy == false"],
        "postconditions": ["worker_healthy == true", "restart_count increments by one"],
    },
    "rollback_deployment": {
        "capability": "synthetic.deployment.rollback",
        "preconditions": ["deploy_version != stable_version"],
        "postconditions": ["deploy_version == stable_version", "deployment_healthy == true"],
    },
    "warm_cache": {
        "capability": "synthetic.cache.warm",
        "preconditions": ["cache_warm == false"],
        "postconditions": ["cache_warm == true"],
    },
}


def action_spec(action: str) -> dict:
    if action not in ACTION_SPECS:
        raise PolicyRejected(f"Action is outside the synthetic capability set: {action}")
    return deepcopy(ACTION_SPECS[action])


def validate_proposal(proposal: dict) -> dict:
    spec = action_spec(proposal["action"])
    if proposal.get("capability") != spec["capability"]:
        raise PolicyRejected("Capability does not match the server-side action policy")
    if proposal.get("arguments", {}) != {}:
        raise PolicyRejected("Baseline actions do not accept model-controlled arguments")
    return spec


def apply_action(action: str, state: dict) -> dict:
    updated = deepcopy(state)
    if action == "restart_worker":
        if updated.get("worker_healthy") is not False:
            raise PolicyRejected("restart_worker precondition failed")
        updated["worker_healthy"] = True
        updated["restart_count"] = int(updated.get("restart_count", 0)) + 1
    elif action == "rollback_deployment":
        if updated.get("deploy_version") == updated.get("stable_version") or not updated.get("stable_version"):
            raise PolicyRejected("rollback_deployment precondition failed")
        updated["deploy_version"] = updated["stable_version"]
        updated["deployment_healthy"] = True
    elif action == "warm_cache":
        if updated.get("cache_warm") is not False:
            raise PolicyRejected("warm_cache precondition failed")
        updated["cache_warm"] = True
    else:
        raise PolicyRejected(f"No executor exists for action: {action}")
    return updated


def postconditions_hold(action: str, before: dict, after: dict) -> bool:
    if action == "restart_worker":
        return after.get("worker_healthy") is True and after.get("restart_count") == int(before.get("restart_count", 0)) + 1
    if action == "rollback_deployment":
        return after.get("deploy_version") == before.get("stable_version") and after.get("deployment_healthy") is True
    if action == "warm_cache":
        return after.get("cache_warm") is True
    return False
