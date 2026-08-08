from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from runbook_sentinel.telemetry import verify_trace_file


ROOT = Path(__file__).resolve().parents[1]
COMPARISON_PATH = ROOT / "artifacts/evaluations/baseline-0018-model-comparison.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _attempts(report: dict) -> list[dict]:
    return [attempt for case in report["cases"] for attempt in case["attempts"]]


def _metric_projection(report: dict, candidate: bool) -> dict:
    generation = report["metrics"]["generation"]
    metrics = {
        "outcome_accuracy": generation["outcome_accuracy"],
        "diagnosis_accuracy": generation["diagnosis_accuracy"],
        "structured_parse_success_rate": generation["structured_parse_success_rate"],
        "schema_invalid_classification_rate": generation[
            "schema_invalid_classification_rate"
        ],
        "unclassified_schema_invalid_count": generation[
            "unclassified_schema_invalid_count"
        ],
        "proposal_exact": report["metrics"]["proposal"]["exact_match"],
        "tool_trajectory_exact": report["metrics"]["tool_trajectory"]["exact_match"],
        "terminal_state_exact": report["metrics"]["terminal_state"]["exact_match_rate"],
        "policy_compliance": report["metrics"]["policy"]["compliance_rate"],
        "benign_utility": report["metrics"]["utility"]["benign_case_pass_rate"],
        "proposal_attack_success": report["metrics"]["security"][
            "proposal_attack_success_rate"
        ],
        "terminal_attack_success": report["metrics"]["security"][
            "terminal_attack_success_rate"
        ],
        "pass_3": report["metrics"]["reliability"]["pass^3"],
        "median_latency_ms": report["metrics"]["latency"]["median_ms"],
        "p95_latency_ms": report["metrics"]["latency"]["p95_ms"],
        "model_calls": report["metrics"]["cost"]["model_calls"],
        "prompt_tokens": report["metrics"]["cost"]["prompt_tokens"],
        "completion_tokens": report["metrics"]["cost"]["completion_tokens"],
        "external_api_usd": report["metrics"]["cost"]["estimated_usd"],
    }
    if candidate:
        metrics.update(
            {
                "development_structured_parse_success_rate": report["split_metrics"][
                    "development"
                ]["generation"]["structured_parse_success_rate"],
                "test_structured_parse_success_rate": report["split_metrics"]["test"][
                    "generation"
                ]["structured_parse_success_rate"],
                "local_hardware_and_energy_cost_estimated": False,
            }
        )
    return metrics


def _forbidden_raw_keys(value: object) -> set[str]:
    forbidden = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"raw_output", "generated_content", "response_content"}:
                forbidden.add(key)
            forbidden.update(_forbidden_raw_keys(item))
    elif isinstance(value, list):
        for item in value:
            forbidden.update(_forbidden_raw_keys(item))
    return forbidden


def main() -> None:
    comparison = json.loads(COMPARISON_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    reports = {}
    for side in ("control", "candidate"):
        record = comparison[side]
        report_path = ROOT / record["report"]
        trace_path = report_path.with_name(report_path.stem + ".traces.jsonl")
        manifest_path = ROOT / record["manifest"]
        if not report_path.is_file() or not trace_path.is_file() or not manifest_path.is_file():
            errors.append(f"{side}_artifact_missing")
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        reports[side] = report
        if report_path.stat().st_size != record["report_bytes"]:
            errors.append(f"{side}_report_size_mismatch")
        if _sha256(report_path) != record["report_sha256"]:
            errors.append(f"{side}_report_sha256_mismatch")
        if trace_path.stat().st_size != record["trace_bytes"]:
            errors.append(f"{side}_trace_size_mismatch")
        if _sha256(trace_path) != record["trace_sha256"]:
            errors.append(f"{side}_trace_sha256_mismatch")
        if _sha256(manifest_path) != comparison["manifest_sha256"]:
            errors.append(f"{side}_manifest_sha256_mismatch")
        if report.get("manifest_sha256") != comparison["manifest_sha256"]:
            errors.append(f"{side}_report_manifest_mismatch")
        anchor = report.get("metrics", {}).get("telemetry_integrity", {}).get(
            "companion_trace", {}
        )
        trace_verification = verify_trace_file(
            trace_path,
            expected_event_count=anchor.get("event_count"),
            expected_final_event_sha256=anchor.get("final_event_sha256"),
        )
        if not trace_verification.get("valid") or not trace_verification.get("anchored"):
            errors.append(f"{side}_trace_invalid")
        if anchor.get("event_count") != record["trace_event_count"]:
            errors.append(f"{side}_trace_event_count_mismatch")
        if report.get("scenario_count") != 28 or report.get("attempt_count") != 84:
            errors.append(f"{side}_frozen_count_mismatch")
        if _metric_projection(report, side == "candidate") != record["metrics"]:
            errors.append(f"{side}_metric_projection_mismatch")
        if _forbidden_raw_keys(report):
            errors.append(f"{side}_raw_content_key_present")

    if set(reports) == {"control", "candidate"}:
        control = reports["control"]
        candidate = reports["candidate"]
        attempts = _attempts(candidate)
        parse_counts = Counter(attempt["model"]["parse_status"] for attempt in attempts)
        failure_counts = Counter(
            attempt["model"]["model_output_error_code"]
            for attempt in attempts
            if attempt["model"]["model_output_error_code"] is not None
        )
        candidate_record = comparison["candidate"]
        if dict(parse_counts) != candidate_record["parse_status_counts"]:
            errors.append("candidate_parse_status_counts_mismatch")
        if dict(failure_counts) != candidate_record["failure_code_counts"]:
            errors.append("candidate_failure_code_counts_mismatch")
        accepted_proposals = sum(
            attempt["validated_output"]["proposal"] is not None for attempt in attempts
        )
        if accepted_proposals != candidate_record["accepted_action_proposals"] or accepted_proposals != 0:
            errors.append("candidate_accepted_proposal_present")
        executed_actions = sum(attempt["execution_succeeded"] for attempt in attempts)
        if executed_actions != candidate_record["executed_actions"] or executed_actions != 0:
            errors.append("candidate_execution_present")
        if len(
            {
                attempt["model"]["raw_output_sha256"]
                for attempt in attempts
                if attempt["model"]["raw_output_sha256"] is not None
            }
        ) != candidate_record["unique_raw_output_digests"]:
            errors.append("candidate_unique_digest_count_mismatch")
        if control["gates"]["baseline_disposition"] != "pass":
            errors.append("control_not_pass")
        if candidate["gates"]["baseline_disposition"] != "remediate":
            errors.append("candidate_not_remediate")
        if comparison["control"]["disposition"] != "pass":
            errors.append("control_record_disposition_mismatch")
        if candidate_record["disposition"] != "exclude":
            errors.append("candidate_record_disposition_mismatch")
        if control.get("agent_configuration") != comparison["control"]["configuration"]:
            errors.append("control_configuration_mismatch")
        if candidate.get("agent_configuration") != candidate_record["configuration"]:
            errors.append("candidate_configuration_mismatch")
        model_identities = {
            (
                attempt["model"]["runtime_version"],
                attempt["model"]["model_manifest_sha256"],
                attempt["model"]["contract_id"],
            )
            for attempt in attempts
        }
        if model_identities != {
            (
                candidate_record["runtime_version"],
                candidate_record["model_manifest_sha256"],
                comparison["model_contract_id"],
            )
        }:
            errors.append("candidate_model_identity_mismatch")
        selection = comparison["selection"]
        ratio = round(
            candidate["metrics"]["latency"]["median_ms"]
            / control["metrics"]["latency"]["median_ms"],
            3,
        )
        if ratio != selection["median_latency_ratio_candidate_over_control"]:
            errors.append("latency_ratio_mismatch")
        if selection != {
            **selection,
            "pareto_improvement": False,
            "selected_configuration": "deterministic-control-v2",
            "default_changed": False,
            "candidate_disposition": "exclude",
        }:
            errors.append("selection_mismatch")

    result = {
        "checkpoint": comparison.get("checkpoint"),
        "comparison": str(COMPARISON_PATH.relative_to(ROOT)),
        "errors": sorted(errors),
        "manifest_sha256": comparison.get("manifest_sha256"),
        "selected_configuration": comparison.get("selection", {}).get(
            "selected_configuration"
        ),
        "status": "pass" if not errors else "fail",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
