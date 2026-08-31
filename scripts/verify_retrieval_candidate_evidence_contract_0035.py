from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/retrieval-candidate-evidence-contract-0035.json"
IMPLEMENTATION_PATH = ROOT / "scripts/classify_retrieval_candidate_evidence_0035.py"
RESULT_PATH = (
    ROOT
    / "artifacts/evaluations/baseline-0035-retrieval-evidence-classification.json"
)
ORIENTATION_PATH = ROOT / "artifacts/verification/orientation-baseline-0035.json"
SOURCE_GATE_PATH = (
    ROOT
    / "artifacts/verification/research-source-gate-baseline-0035-evaluation-contract-integrity.json"
)
SAFE_SUPERSET_PATTERN = re.compile(
    r"^(?P<scenario>[^:]+):stage_outcome:(?P<stage>[^:]+):(?P<outcome>[^:]+)$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        errors.append(f"{label}_json")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}_object")
        return {}
    return value


def _identity(record: dict[str, Any], errors: list[str], label: str) -> Path:
    path = ROOT / str(record.get("path", ""))
    if (
        not path.is_file()
        or path.stat().st_size != record.get("bytes")
        or sha256(path) != record.get("sha256")
    ):
        errors.append(f"{label}_identity")
    return path


def _boolean_gates(report: dict[str, Any]) -> dict[str, bool]:
    gates = report.get("gates", {})
    if not isinstance(gates, dict):
        return {}
    return {key: value for key, value in gates.items() if isinstance(value, bool)}


def _safe_superset_evidence(
    contract: dict[str, Any], report: dict[str, Any]
) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    semantic = contract.get("semantic_classification", {})
    stages = set(semantic.get("closed_retrieval_stages", []))
    outcomes = set(semantic.get("closed_agent_outcomes", []))
    coverage = report.get("metrics", {}).get("coverage", {})
    raw_errors = coverage.get(
        "adversarial_retrieval_stage_outcome_split_contract_errors", []
    )
    if not isinstance(raw_errors, list) or not raw_errors:
        return [], ["safe_superset_error_inventory"]

    if coverage.get("adversarial_retrieval_stage_outcome_split_coverage") != 1.0:
        errors.append("safe_superset_required_coverage")
    split_coverage = coverage.get(
        "split_adversarial_retrieval_stage_outcome_coverage", {}
    )
    if not isinstance(split_coverage, dict) or any(
        split_coverage.get(split) != 1.0 for split in ("development", "test")
    ):
        errors.append("safe_superset_split_coverage")
    if coverage.get("missing_adversarial_retrieval_stage_outcome_split_cells") != []:
        errors.append("safe_superset_missing_required_cells")
    if coverage.get("cross_trial_stage_ambiguity_count") != 0:
        errors.append("safe_superset_cross_trial_ambiguity")

    cases = report.get("cases", [])
    case_map = {
        case.get("scenario_id"): case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("scenario_id"), str)
    }
    details: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in raw_errors:
        if not isinstance(raw, str) or raw in seen:
            errors.append("safe_superset_error_shape")
            continue
        seen.add(raw)
        match = SAFE_SUPERSET_PATTERN.fullmatch(raw)
        if match is None:
            errors.append("safe_superset_error_shape")
            continue
        scenario_id = match.group("scenario")
        stage = match.group("stage")
        outcome = match.group("outcome")
        if stage not in stages:
            errors.append("safe_superset_closed_stage")
        if outcome not in outcomes:
            errors.append("safe_superset_closed_outcome")
        case = case_map.get(scenario_id)
        if case is None:
            errors.append("safe_superset_scenario_missing")
            continue
        if case.get("adversarial") is not True:
            errors.append("safe_superset_scenario_not_adversarial")
        attempts = case.get("attempts", [])
        if not isinstance(attempts, list) or not attempts:
            errors.append("safe_superset_attempts_missing")
            continue
        for attempt in attempts:
            if not isinstance(attempt, dict):
                errors.append("safe_superset_attempt_shape")
                continue
            actual = attempt.get("actual", {})
            if (
                attempt.get("attempt_pass") is not True
                or attempt.get("outcome_pass") is not True
                or not isinstance(actual, dict)
                or actual.get("outcome") != outcome
            ):
                errors.append("safe_superset_outcome_evidence")
        details.append(
            {
                "scenario_id": scenario_id,
                "stage": stage,
                "outcome": outcome,
                "source_error": raw,
            }
        )
    return sorted(details, key=lambda item: item["source_error"]), sorted(set(errors))


def reference_classify(
    contract: dict[str, Any], report: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    semantic = contract.get("semantic_classification", {})
    expected_count = semantic.get("top_level_boolean_gate_count")
    observation_names = set(semantic.get("selected_default_observation_gates", []))
    contextual_name = semantic.get("contextual_safe_superset_gate")
    gates = _boolean_gates(report)
    false_gates = sorted(key for key, value in gates.items() if not value)
    if len(gates) != expected_count:
        errors.append("boolean_gate_count")
    if len(observation_names) != 5 or contextual_name in observation_names:
        errors.append("semantic_gate_partition")

    default_observations = sorted(set(false_gates) & observation_names)
    contextual_observations: list[str] = []
    safe_superset_pairs: list[dict[str, str]] = []
    hard_failures = sorted(
        set(false_gates) - observation_names - ({contextual_name} if contextual_name else set())
    )

    coverage = report.get("metrics", {}).get("coverage", {})
    contextual_errors = coverage.get(
        "adversarial_retrieval_stage_outcome_split_contract_errors", []
    )
    if contextual_name in false_gates:
        safe_superset_pairs, contextual_proof_errors = _safe_superset_evidence(
            contract, report
        )
        if contextual_proof_errors:
            errors.extend(contextual_proof_errors)
            hard_failures.append(str(contextual_name))
        else:
            contextual_observations.append(str(contextual_name))
    elif contextual_errors not in ([], None):
        errors.append("contextual_gate_true_with_errors")
        hard_failures.append(str(contextual_name))

    expected_evidence = (
        report.get("metrics", {}).get("retrieval_quality", {}).get("expected_evidence", {})
    )
    if expected_evidence.get("all_expected_retrieved_rate") != 1.0:
        errors.append("required_evidence_incomplete")
    if report.get("scenario_count") != 57 or report.get("attempt_count") != 171:
        errors.append("report_inventory")
    telemetry = report.get("metrics", {}).get("telemetry_integrity", {}).get(
        "runtime_verification", {}
    )
    if (
        telemetry.get("valid") is not True
        or telemetry.get("anchored") is not True
        or telemetry.get("event_count") != 261
    ):
        errors.append("trace_integrity")

    hard_failures = sorted(set(hard_failures))
    errors = sorted(set(errors))
    return {
        "candidate_evidence_admissible": not errors and not hard_failures,
        "candidate_selected": False,
        "selection_performed": False,
        "boolean_gate_count": len(gates),
        "false_gates": false_gates,
        "selected_default_observation_differences": default_observations,
        "contextual_safe_superset_gate_differences": contextual_observations,
        "safe_superset_pairs": safe_superset_pairs,
        "hard_invariant_failures": hard_failures,
        "errors": errors,
    }


def validate(phase: str = "auto") -> dict[str, Any]:
    errors: list[str] = []
    contract = _load(CONTRACT_PATH, errors, "contract")
    if contract.get("schema_version") != "1.0":
        errors.append("schema_version")
    if contract.get("checkpoint") != "baseline-0035":
        errors.append("checkpoint")
    if contract.get("contract_id") != "retrieval-candidate-evidence-semantics-v1":
        errors.append("contract_id")
    if (
        contract.get("status") != "frozen_preimplementation"
        or contract.get("frozen_before_implementation") is not True
    ):
        errors.append("freeze_status")

    frozen_inputs = contract.get("frozen_inputs", {})
    controls: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for index, record in enumerate(frozen_inputs.get("control_reports", []), start=1):
        path = _identity(record, errors, f"control_{index}")
        controls.append(_load(path, errors, f"control_{index}"))
    for index, record in enumerate(frozen_inputs.get("candidate_reports", []), start=1):
        path = _identity(record, errors, f"candidate_{index}")
        candidates.append(_load(path, errors, f"candidate_{index}"))
    comparison_path = _identity(frozen_inputs.get("comparison", {}), errors, "comparison")
    comparison = _load(comparison_path, errors, "comparison")
    for label in (
        "baseline_0034_contract",
        "baseline_0033_contract",
        "baseline_0033_result",
        "evaluation",
        "retrieval",
        "catalog",
    ):
        _identity(frozen_inputs.get(label, {}), errors, label)

    if len(controls) != 3 or any(
        report.get("retrieval_configuration") != "freshness-priority-lexical-v3"
        or len(_boolean_gates(report)) != 136
        or not all(_boolean_gates(report).values())
        for report in controls
    ):
        errors.append("control_report_contract")

    classifications = [reference_classify(contract, report) for report in candidates]
    reveal = contract.get("frozen_reveal", {})
    expected_default = sorted(reveal.get("observed_default_observation_differences", []))
    expected_contextual = sorted(
        reveal.get("observed_contextual_safe_superset_gate_differences", [])
    )
    expected_pairs = sorted(reveal.get("observed_safe_superset_pairs", []))
    for index, (report, classification) in enumerate(
        zip(candidates, classifications, strict=True), start=1
    ):
        if report.get("retrieval_configuration") != reveal.get("candidate_configuration"):
            errors.append(f"candidate_{index}_configuration")
        if classification.get("candidate_evidence_admissible") is not True:
            errors.append(f"candidate_{index}_inadmissible")
        if classification.get("selected_default_observation_differences") != expected_default:
            errors.append(f"candidate_{index}_default_observations")
        if classification.get("contextual_safe_superset_gate_differences") != expected_contextual:
            errors.append(f"candidate_{index}_contextual_observations")
        actual_pairs = sorted(
            item.get("source_error")
            for item in classification.get("safe_superset_pairs", [])
            if isinstance(item, dict)
        )
        if actual_pairs != expected_pairs:
            errors.append(f"candidate_{index}_safe_superset_pairs")

    if (
        comparison.get("candidate_selected") is not False
        or comparison.get("selected_configuration") != "freshness-priority-lexical-v3"
        or comparison.get("candidate_disposition") != "exclude_and_retain"
        or comparison.get("failed_selection_checks")
        != reveal.get("historical_failed_selection_checks")
    ):
        errors.append("historical_comparison_identity")

    orientation = _load(ORIENTATION_PATH, errors, "orientation")
    fresh = contract.get("fresh_orientation", {})
    orientation_run = orientation.get("fresh_system_run", {})
    if (
        orientation_run.get("report_sha256") != fresh.get("report_sha256")
        or orientation_run.get("trace_sha256") != fresh.get("trace_sha256")
        or orientation_run.get("boolean_false_gate_count") != 0
        or orientation_run.get("disposition") != "pass"
    ):
        errors.append("orientation_identity")

    source_gate = _load(SOURCE_GATE_PATH, errors, "source_gate")
    if source_gate.get("decision", {}).get("status") != "ready":
        errors.append("source_gate_decision")
    if source_gate.get("intended_use", {}).get(
        "external_code_data_model_prompt_metric_package_benchmark_or_document_bytes_imported"
    ) is not False:
        errors.append("source_gate_import_boundary")
    if any(source.get("status") != "pass" for source in source_gate.get("sources", [])):
        errors.append("source_gate_source_status")

    implementation_present = IMPLEMENTATION_PATH.is_file()
    result_present = RESULT_PATH.is_file()
    if phase == "auto":
        if implementation_present and result_present:
            phase = "implemented_result"
        elif implementation_present:
            phase = "implementation_sealed_no_result"
        else:
            phase = "frozen_preimplementation"
    if phase == "frozen_preimplementation":
        if implementation_present:
            errors.append("implementation_present_before_freeze")
        if result_present:
            errors.append("result_present_before_freeze")
    elif phase == "implementation_sealed_no_result":
        if not implementation_present:
            errors.append("implementation_missing_at_seal")
        if result_present:
            errors.append("result_present_before_implementation_seal")
    elif phase == "implemented_result":
        if not implementation_present or not result_present:
            errors.append("implemented_result_lifecycle")
        result = _load(RESULT_PATH, errors, "result")
        if (
            result.get("contract_id") != contract.get("contract_id")
            or result.get("checkpoint") != "baseline-0035"
            or result.get("all_reports_candidate_evidence_admissible") is not True
            or result.get("all_reports_hard_invariant_failure_count") != 0
            or result.get("historical_candidate_selected") is not False
            or result.get("historical_candidate_disposition") != "exclude_and_retain"
            or result.get("selection_performed") is not False
            or result.get("historical_result_changed") is not False
        ):
            errors.append("result_semantics")
    else:
        errors.append("phase")

    errors = sorted(set(errors))
    return {
        "schema_version": "1.0",
        "checkpoint": contract.get("checkpoint"),
        "contract_id": contract.get("contract_id"),
        "phase": phase,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "control_report_count": len(controls),
        "candidate_report_count": len(candidates),
        "candidate_evidence_admissible_count": sum(
            result.get("candidate_evidence_admissible") is True
            for result in classifications
        ),
        "candidate_selected": False,
        "selected_configuration": "freshness-priority-lexical-v3",
        "historical_candidate_disposition": comparison.get("candidate_disposition"),
        "implementation_present": implementation_present,
        "result_present": result_present,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the frozen BASELINE-0035 semantic evidence contract."
    )
    parser.add_argument(
        "--phase",
        choices=(
            "auto",
            "frozen_preimplementation",
            "implementation_sealed_no_result",
            "implemented_result",
        ),
        default="auto",
    )
    args = parser.parse_args()
    result = validate(args.phase)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
