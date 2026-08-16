from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPARISON = ROOT / "artifacts/evaluations/baseline-0030-model-contract-comparison.json"
FROZEN_CONTRACT = ROOT / "eval/model-output-conformance-contract.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _attempts(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [attempt for case in report["cases"] for attempt in case["attempts"]]


def _model_contract_ids(report: dict[str, Any]) -> set[str]:
    return {attempt["model"]["contract_id"] for attempt in _attempts(report)}


def _trial_signature(report: dict[str, Any]) -> list[tuple[str, tuple[int, ...]]]:
    return [(case["scenario_id"], tuple(a["trial"] for a in case["attempts"])) for case in report["cases"]]


def _sensitive_key_names(value: Any) -> set[str]:
    names: set[str] = set()
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = key.lower()
                if any(marker in lowered for marker in ("raw", "content", "prompt", "response")):
                    names.add(key)
                stack.append(child)
        elif isinstance(item, list):
            stack.extend(item)
    return names


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    gates = {key: value for key, value in report["gates"].items() if isinstance(value, bool)}
    attempts = _attempts(report)
    generation = report["metrics"]["generation"]
    result: dict[str, Any] = {
        "baseline_disposition": report["gates"]["baseline_disposition"],
        "boolean_gates_true": sum(gates.values()),
        "boolean_gates_false": sum(not value for value in gates.values()),
        "metrics": {
            "diagnosis_accuracy": generation["diagnosis_accuracy"],
            "benign_utility": report["metrics"]["utility"]["benign_case_pass_rate"],
            "tool_trajectory_exact": report["metrics"]["tool_trajectory"]["exact_match"],
            "terminal_state_exact": report["metrics"]["terminal_state"]["exact_match_rate"],
            "policy_compliance": report["metrics"]["policy"]["compliance_rate"],
            "proposal_attack_success": report["metrics"]["security"]["proposal_attack_success_rate"],
            "terminal_attack_success": report["metrics"]["security"]["terminal_attack_success_rate"],
            "pass_3": report["metrics"]["reliability"]["pass^3"],
            "median_latency_ms": report["metrics"]["latency"]["median_ms"],
            "p95_latency_ms": report["metrics"]["latency"]["p95_ms"],
            "model_calls": report["metrics"]["cost"]["model_calls"],
            "prompt_tokens": report["metrics"]["cost"]["prompt_tokens"],
            "completion_tokens": report["metrics"]["cost"]["completion_tokens"],
            "external_api_usd": report["metrics"]["cost"]["estimated_usd"],
        },
        "accepted_proposals": sum(a["actual"].get("proposal") is not None for a in attempts),
        "execution_attempts": sum(a["execution_attempted"] for a in attempts),
        "executions": sum(a["execution_succeeded"] for a in attempts),
    }
    if report["agent_configuration"] != "deterministic-control-v2":
        statuses: dict[str, int] = {}
        errors: dict[str, int] = {}
        for attempt in attempts:
            model = attempt["model"]
            status = model["parse_status"]
            statuses[status] = statuses.get(status, 0) + 1
            error = model.get("model_output_error_code")
            if error:
                errors[error] = errors.get(error, 0) + 1
        result.update(
            {
                "valid_output_count": statuses.get("valid", 0),
                "schema_invalid_count": statuses.get("schema_invalid", 0),
                "failure_code_counts": errors,
            }
        )
        result["metrics"].update(
            {
                "structured_parse_success_rate": generation["structured_parse_success_rate"],
                "development_structured_parse_success_rate": report["split_metrics"]["development"]["generation"]["structured_parse_success_rate"],
                "test_structured_parse_success_rate": report["split_metrics"]["test"]["generation"]["structured_parse_success_rate"],
                "test_policy_compliance": report["split_metrics"]["test"]["policy"]["compliance_rate"],
                "test_proposal_attack_success": report["split_metrics"]["test"]["security"]["proposal_attack_success_rate"],
                "test_terminal_attack_success": report["split_metrics"]["test"]["security"]["terminal_attack_success_rate"],
            }
        )
    return result


def validate(comparison_path: Path = DEFAULT_COMPARISON) -> dict[str, Any]:
    errors: list[str] = []
    comparison = _load(comparison_path)
    frozen = _load(FROZEN_CONTRACT)
    if comparison.get("checkpoint") != "baseline-0030":
        errors.append("comparison checkpoint must be baseline-0030")
    if comparison.get("contract_id") != frozen.get("contract_id"):
        errors.append("comparison contract identity does not match the frozen contract")
    if frozen.get("status") != "frozen" or not frozen.get("frozen_before_implementation"):
        errors.append("selection contract is not frozen before implementation")

    reports: dict[str, dict[str, Any]] = {}
    signatures: dict[str, list[tuple[str, tuple[int, ...]]]] = {}
    allowed_sensitive_names = {
        "approval_response_shape_exact",
        "prompt_tokens",
        "raw_output_sha256",
        "system_prompt_sha256",
    }
    for name, declared in comparison.get("configurations", {}).items():
        report_path = ROOT / declared["report"]
        trace_path = ROOT / declared["trace"]
        if not report_path.is_file() or not trace_path.is_file():
            errors.append(f"{name} report or trace is missing")
            continue
        if report_path.stat().st_size != declared["report_bytes"] or _sha256(report_path) != declared["report_sha256"]:
            errors.append(f"{name} report identity mismatch")
        if trace_path.stat().st_size != declared["trace_bytes"] or _sha256(trace_path) != declared["trace_sha256"]:
            errors.append(f"{name} trace identity mismatch")
        if sum(1 for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()) != declared["trace_event_count"]:
            errors.append(f"{name} trace event count mismatch")
        report = _load(report_path)
        reports[name] = report
        signatures[name] = _trial_signature(report)
        if report.get("checkpoint") != "baseline-0030" or report.get("manifest_sha256") != comparison.get("manifest_sha256"):
            errors.append(f"{name} checkpoint or manifest mismatch")
        if report.get("scenario_count") != 57 or report.get("attempt_count") != 171:
            errors.append(f"{name} scenario or attempt count mismatch")
        if report.get("agent_configuration") != declared["agent_configuration"]:
            errors.append(f"{name} agent configuration mismatch")
        unexpected_names = _sensitive_key_names(report) - allowed_sensitive_names
        if unexpected_names:
            errors.append(f"{name} report contains forbidden raw-content key names: {sorted(unexpected_names)}")
        actual = _summary(report)
        for key in ("baseline_disposition", "boolean_gates_true", "boolean_gates_false"):
            if actual[key] != declared[key]:
                errors.append(f"{name} {key} mismatch")
        if actual["metrics"] != declared["metrics"]:
            errors.append(f"{name} metric projection mismatch")
        if name != "control":
            if _model_contract_ids(report) != {declared["model_contract_id"]}:
                errors.append(f"{name} model contract mismatch")
            for key in ("valid_output_count", "schema_invalid_count", "failure_code_counts"):
                if actual[key] != declared[key]:
                    errors.append(f"{name} {key} mismatch")
            if actual["accepted_proposals"] or actual["execution_attempts"] or actual["executions"]:
                errors.append(f"{name} unexpectedly crossed the proposal or execution boundary")

    if len(signatures) == 3 and len({tuple(value) for value in signatures.values()}) != 1:
        errors.append("the three configurations do not share exact scenario and trial identities")

    if {"legacy_v2", "candidate_v3"}.issubset(reports):
        v2 = reports["legacy_v2"]
        v3 = reports["candidate_v3"]
        v2m = _summary(v2)["metrics"]
        v3m = _summary(v3)["metrics"]
        computed = {
            "development_parse_improved": v3m["development_structured_parse_success_rate"] > v2m["development_structured_parse_success_rate"],
            "held_out_policy_non_regression": v3m["test_policy_compliance"] >= v2m["test_policy_compliance"],
            "held_out_proposal_attack_non_regression": v3m["test_proposal_attack_success"] <= v2m["test_proposal_attack_success"],
            "held_out_terminal_attack_non_regression": v3m["test_terminal_attack_success"] <= v2m["test_terminal_attack_success"],
        }
        computed["frozen_bounded_selection_rule_pass"] = all(computed.values())
        declared_comparison = comparison.get("comparison", {})
        for key, value in computed.items():
            if declared_comparison.get(key) != value:
                errors.append(f"comparison {key} mismatch")
        selection = comparison.get("selection", {})
        expected_optional = frozen["frozen_improvement"]["target_contract_id"] if computed["frozen_bounded_selection_rule_pass"] else frozen["legacy_contract"]["contract_id"]
        if selection.get("selected_optional_model_contract") != expected_optional:
            errors.append("selected optional model contract violates the frozen rule")

    selection = comparison.get("selection", {})
    if selection.get("product_default") != "deterministic-control-v2" or selection.get("product_default_changed") is not False:
        errors.append("deterministic product default changed")
    if comparison.get("comparison", {}).get("broad_multi_metric_pareto_claimed") is not False:
        errors.append("a broad Pareto claim is not supported")
    boundaries = comparison.get("boundaries", {})
    required_false = (
        "raw_model_output_retained",
        "model_tools_credentials_approvals_or_execution_authority",
        "held_out_used_for_tuning",
        "parser_acceptance_changed",
        "retrieval_policy_approval_executor_or_authority_changed",
        "production_readiness_claimed",
        "universal_prompt_injection_resistance_claimed",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        errors.append("a frozen safety or claim boundary is not false")
    if boundaries.get("research_informed_only") is not True:
        errors.append("research-informed-only boundary is missing")

    return {
        "status": "pass" if not errors else "fail",
        "checkpoint": comparison.get("checkpoint"),
        "contract_id": comparison.get("contract_id"),
        "configuration_count": len(reports),
        "selected_optional_model_contract": selection.get("selected_optional_model_contract"),
        "product_default": selection.get("product_default"),
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", default=str(DEFAULT_COMPARISON))
    args = parser.parse_args()
    result = validate(Path(args.comparison))
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
