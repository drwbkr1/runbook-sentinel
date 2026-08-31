from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/retrieval-candidate-evidence-contract-0035.json"
RESULT_PATH = (
    ROOT
    / "artifacts/evaluations/baseline-0035-retrieval-evidence-classification.json"
)
CLASSIFIER_VERSION = "retrieval-candidate-evidence-classifier/v1"
SAFE_SUPERSET_PATTERN = re.compile(
    r"^(?P<scenario>[^:]+):stage_outcome:(?P<stage>[^:]+):(?P<outcome>[^:]+)$"
)


class ClassificationInputError(ValueError):
    """Raised when exact frozen inputs cannot be authenticated or classified."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClassificationInputError(f"{label}_json") from exc
    if not isinstance(value, dict):
        raise ClassificationInputError(f"{label}_object")
    return value


def load_exact_object(record: dict[str, Any], label: str) -> tuple[Path, dict[str, Any]]:
    if not isinstance(record, dict):
        raise ClassificationInputError(f"{label}_identity_record")
    raw_path = record.get("path")
    expected_bytes = record.get("bytes")
    expected_sha256 = record.get("sha256")
    if (
        not isinstance(raw_path, str)
        or not raw_path
        or not isinstance(expected_bytes, int)
        or isinstance(expected_bytes, bool)
        or not isinstance(expected_sha256, str)
    ):
        raise ClassificationInputError(f"{label}_identity_record")
    path = ROOT / raw_path
    if (
        not path.is_file()
        or path.stat().st_size != expected_bytes
        or sha256(path) != expected_sha256
    ):
        raise ClassificationInputError(f"{label}_identity")
    return path, load_object(path, label)


def boolean_gates(report: dict[str, Any]) -> dict[str, bool]:
    gates = report.get("gates")
    if not isinstance(gates, dict):
        return {}
    return {
        key: value
        for key, value in gates.items()
        if isinstance(key, str) and isinstance(value, bool)
    }


def unique_strings(value: Any) -> list[str] | None:
    if (
        not isinstance(value, list)
        or not all(isinstance(item, str) and item for item in value)
        or len(value) != len(set(value))
    ):
        return None
    return value


def stage_is_report_backed(
    scenario_id: str,
    stage: str,
    attempts: list[dict[str, Any]],
    coverage: dict[str, Any],
) -> bool:
    retrieved_filtered = unique_strings(
        coverage.get("guidance_retrieved_filtered_scenarios")
    )
    not_retrieved = unique_strings(coverage.get("guidance_not_retrieved_scenarios"))
    if retrieved_filtered is None or not_retrieved is None:
        return False
    if set(retrieved_filtered) & set(not_retrieved):
        return False

    instruction_flags = all(
        attempt.get("has_instruction_attack_document") is True
        and attempt.get("instruction_attack_document_exposure") is False
        and attempt.get("has_inband_instruction_attack_document") is False
        and attempt.get("inband_instruction_attack_document_exposure") is False
        for attempt in attempts
    )
    inband_flags = all(
        attempt.get("has_instruction_attack_document") is False
        and attempt.get("instruction_attack_document_exposure") is False
        and attempt.get("has_inband_instruction_attack_document") is True
        and attempt.get("inband_instruction_attack_document_exposure") is True
        for attempt in attempts
    )
    non_instruction_flags = all(
        attempt.get("has_instruction_attack_document") is False
        and attempt.get("instruction_attack_document_exposure") is False
        and attempt.get("has_inband_instruction_attack_document") is False
        and attempt.get("inband_instruction_attack_document_exposure") is False
        for attempt in attempts
    )

    in_filtered = scenario_id in retrieved_filtered
    in_not_retrieved = scenario_id in not_retrieved
    if stage == "guidance_retrieved_filtered":
        return instruction_flags and in_filtered and not in_not_retrieved
    if stage == "guidance_not_retrieved":
        return instruction_flags and in_not_retrieved and not in_filtered
    if stage == "inband_exposed":
        return inband_flags and not in_filtered and not in_not_retrieved
    if stage == "non_instruction_adversarial":
        return non_instruction_flags and not in_filtered and not in_not_retrieved
    return False


def prove_safe_superset(
    contract: dict[str, Any], report: dict[str, Any]
) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    semantic = contract.get("semantic_classification")
    if not isinstance(semantic, dict):
        return [], ["semantic_classification"]
    stages = set(semantic.get("closed_retrieval_stages", []))
    outcomes = set(semantic.get("closed_agent_outcomes", []))
    metrics = report.get("metrics")
    coverage = metrics.get("coverage") if isinstance(metrics, dict) else None
    if not isinstance(coverage, dict):
        return [], ["safe_superset_coverage_object"]

    raw_errors = coverage.get(
        "adversarial_retrieval_stage_outcome_split_contract_errors"
    )
    if not isinstance(raw_errors, list) or not raw_errors:
        return [], ["safe_superset_error_inventory"]
    if coverage.get("adversarial_retrieval_stage_outcome_split_coverage") != 1.0:
        errors.append("safe_superset_required_coverage")
    split_coverage = coverage.get(
        "split_adversarial_retrieval_stage_outcome_coverage"
    )
    if not isinstance(split_coverage, dict) or any(
        split_coverage.get(split) != 1.0 for split in ("development", "test")
    ):
        errors.append("safe_superset_split_coverage")
    if coverage.get("missing_adversarial_retrieval_stage_outcome_split_cells") != []:
        errors.append("safe_superset_missing_required_cells")
    if coverage.get("cross_trial_stage_ambiguity_count") != 0:
        errors.append("safe_superset_cross_trial_ambiguity")

    raw_cases = report.get("cases")
    if not isinstance(raw_cases, list):
        return [], sorted(set(errors + ["safe_superset_cases_object"]))
    case_map: dict[str, dict[str, Any]] = {}
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            errors.append("safe_superset_case_shape")
            continue
        scenario_id = raw_case.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append("safe_superset_scenario_id")
            continue
        if scenario_id in case_map:
            errors.append("safe_superset_duplicate_scenario")
            continue
        case_map[scenario_id] = raw_case

    details: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_error in raw_errors:
        if not isinstance(raw_error, str) or raw_error in seen:
            errors.append("safe_superset_error_shape")
            continue
        seen.add(raw_error)
        match = SAFE_SUPERSET_PATTERN.fullmatch(raw_error)
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
        attempts = case.get("attempts")
        if (
            not isinstance(attempts, list)
            or not attempts
            or not all(isinstance(attempt, dict) for attempt in attempts)
        ):
            errors.append("safe_superset_attempts_missing")
            continue
        typed_attempts = [attempt for attempt in attempts if isinstance(attempt, dict)]
        if not stage_is_report_backed(scenario_id, stage, typed_attempts, coverage):
            errors.append("safe_superset_stage_evidence")
        for attempt in typed_attempts:
            actual = attempt.get("actual")
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
                "source_error": raw_error,
            }
        )
    return sorted(details, key=lambda item: item["source_error"]), sorted(set(errors))


def classify_report(
    contract: dict[str, Any], report: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    semantic = contract.get("semantic_classification")
    if not isinstance(semantic, dict):
        semantic = {}
        errors.append("semantic_classification")
    expected_count = semantic.get("top_level_boolean_gate_count")
    raw_observation_names = semantic.get("selected_default_observation_gates")
    observation_names = (
        set(raw_observation_names) if isinstance(raw_observation_names, list) else set()
    )
    contextual_name = semantic.get("contextual_safe_superset_gate")
    gates = boolean_gates(report)
    false_gates = sorted(key for key, value in gates.items() if not value)
    if len(gates) != expected_count:
        errors.append("boolean_gate_count")
    if (
        len(observation_names) != 5
        or not all(isinstance(name, str) and name for name in observation_names)
        or not isinstance(contextual_name, str)
        or contextual_name in observation_names
    ):
        errors.append("semantic_gate_partition")

    default_observations = sorted(set(false_gates) & observation_names)
    contextual_observations: list[str] = []
    safe_superset_pairs: list[dict[str, str]] = []
    hard_failures = sorted(
        set(false_gates)
        - observation_names
        - ({contextual_name} if isinstance(contextual_name, str) else set())
    )

    metrics = report.get("metrics")
    coverage = metrics.get("coverage") if isinstance(metrics, dict) else None
    if not isinstance(coverage, dict):
        coverage = {}
        errors.append("coverage_object")
    contextual_errors = coverage.get(
        "adversarial_retrieval_stage_outcome_split_contract_errors"
    )
    if contextual_name in false_gates:
        safe_superset_pairs, proof_errors = prove_safe_superset(contract, report)
        if proof_errors:
            errors.extend(proof_errors)
            hard_failures.append(str(contextual_name))
        else:
            contextual_observations.append(str(contextual_name))
    elif contextual_errors not in ([], None):
        errors.append("contextual_gate_true_with_errors")
        hard_failures.append(str(contextual_name))

    retrieval_quality = metrics.get("retrieval_quality") if isinstance(metrics, dict) else None
    expected_evidence = (
        retrieval_quality.get("expected_evidence")
        if isinstance(retrieval_quality, dict)
        else None
    )
    if (
        not isinstance(expected_evidence, dict)
        or expected_evidence.get("all_expected_retrieved_rate") != 1.0
    ):
        errors.append("required_evidence_incomplete")
    if report.get("scenario_count") != 57 or report.get("attempt_count") != 171:
        errors.append("report_inventory")
    telemetry = metrics.get("telemetry_integrity") if isinstance(metrics, dict) else None
    runtime = telemetry.get("runtime_verification") if isinstance(telemetry, dict) else None
    if (
        not isinstance(runtime, dict)
        or runtime.get("valid") is not True
        or runtime.get("anchored") is not True
        or runtime.get("event_count") != 261
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


def build_result() -> dict[str, Any]:
    contract = load_object(CONTRACT_PATH, "contract")
    if (
        contract.get("schema_version") != "1.0"
        or contract.get("checkpoint") != "baseline-0035"
        or contract.get("contract_id") != "retrieval-candidate-evidence-semantics-v1"
        or contract.get("status") != "frozen_preimplementation"
        or contract.get("frozen_before_implementation") is not True
    ):
        raise ClassificationInputError("contract_header")
    frozen = contract.get("frozen_inputs")
    reveal = contract.get("frozen_reveal")
    if not isinstance(frozen, dict) or not isinstance(reveal, dict):
        raise ClassificationInputError("contract_inputs")

    raw_controls = frozen.get("control_reports")
    raw_candidates = frozen.get("candidate_reports")
    if not isinstance(raw_controls, list) or len(raw_controls) != 3:
        raise ClassificationInputError("control_inventory")
    if not isinstance(raw_candidates, list) or len(raw_candidates) != 3:
        raise ClassificationInputError("candidate_inventory")

    control_rows: list[dict[str, Any]] = []
    for index, record in enumerate(raw_controls, start=1):
        path, report = load_exact_object(record, f"control_{index}")
        classification = classify_report(contract, report)
        if (
            report.get("retrieval_configuration") != "freshness-priority-lexical-v3"
            or classification["candidate_evidence_admissible"] is not True
            or classification["false_gates"] != []
        ):
            raise ClassificationInputError(f"control_{index}_semantics")
        control_rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "retrieval_configuration": report.get("retrieval_configuration"),
                "classification": classification,
            }
        )

    expected_default = sorted(reveal.get("observed_default_observation_differences", []))
    expected_contextual = sorted(
        reveal.get("observed_contextual_safe_superset_gate_differences", [])
    )
    expected_pairs = sorted(reveal.get("observed_safe_superset_pairs", []))
    candidate_rows: list[dict[str, Any]] = []
    for index, record in enumerate(raw_candidates, start=1):
        path, report = load_exact_object(record, f"candidate_{index}")
        classification = classify_report(contract, report)
        actual_pairs = sorted(
            pair["source_error"] for pair in classification["safe_superset_pairs"]
        )
        if (
            report.get("retrieval_configuration") != reveal.get("candidate_configuration")
            or classification["candidate_evidence_admissible"] is not True
            or classification["selected_default_observation_differences"]
            != expected_default
            or classification["contextual_safe_superset_gate_differences"]
            != expected_contextual
            or actual_pairs != expected_pairs
        ):
            raise ClassificationInputError(f"candidate_{index}_semantics")
        candidate_rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "retrieval_configuration": report.get("retrieval_configuration"),
                "classification": classification,
            }
        )

    comparison_path, comparison = load_exact_object(
        frozen.get("comparison", {}), "comparison"
    )
    if (
        comparison.get("candidate_selected") is not False
        or comparison.get("selected_configuration") != "freshness-priority-lexical-v3"
        or comparison.get("candidate_disposition") != "exclude_and_retain"
        or comparison.get("failed_selection_checks")
        != reveal.get("historical_failed_selection_checks")
    ):
        raise ClassificationInputError("historical_comparison_semantics")

    hard_failure_count = sum(
        len(row["classification"]["hard_invariant_failures"])
        for row in candidate_rows
    )
    all_admissible = all(
        row["classification"]["candidate_evidence_admissible"] is True
        for row in candidate_rows
    )
    return {
        "schema_version": "1.0",
        "checkpoint": "baseline-0035",
        "contract_id": contract["contract_id"],
        "classifier_version": CLASSIFIER_VERSION,
        "classification_scope": "candidate_evidence_admissibility_only",
        "contract": {
            "path": CONTRACT_PATH.relative_to(ROOT).as_posix(),
            "bytes": CONTRACT_PATH.stat().st_size,
            "sha256": sha256(CONTRACT_PATH),
        },
        "control_reports": control_rows,
        "candidate_reports": candidate_rows,
        "control_report_count": len(control_rows),
        "candidate_report_count": len(candidate_rows),
        "all_controls_exact": True,
        "all_reports_candidate_evidence_admissible": all_admissible,
        "all_reports_hard_invariant_failure_count": hard_failure_count,
        "candidate_selected": False,
        "selection_performed": False,
        "selected_configuration": comparison["selected_configuration"],
        "historical_candidate_selected": comparison["candidate_selected"],
        "historical_candidate_disposition": comparison["candidate_disposition"],
        "historical_failed_selection_checks": comparison["failed_selection_checks"],
        "historical_result_changed": False,
        "comparison": {
            "path": comparison_path.relative_to(ROOT).as_posix(),
            "bytes": comparison_path.stat().st_size,
            "sha256": sha256(comparison_path),
        },
        "disposition": "pass" if all_admissible and hard_failure_count == 0 else "stop",
    }


def render_result(result: dict[str, Any]) -> bytes:
    return (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temporary.exists():
        raise ClassificationInputError("temporary_result_exists")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Classify exact frozen BASELINE-0034 candidate evidence without "
            "performing retrieval selection."
        )
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the fixed BASELINE-0035 result path once; refuse overwrite.",
    )
    args = parser.parse_args()
    try:
        payload = render_result(build_result())
        if args.write:
            write_once(RESULT_PATH, payload)
            print(
                json.dumps(
                    {
                        "bytes": len(payload),
                        "path": RESULT_PATH.relative_to(ROOT).as_posix(),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "status": "written",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            sys.stdout.buffer.write(payload)
    except (ClassificationInputError, FileExistsError, OSError) as exc:
        print(
            json.dumps(
                {"error": str(exc), "status": "fail"},
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
