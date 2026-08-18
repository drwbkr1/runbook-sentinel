from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel import retrieval as runtime_retrieval  # noqa: E402
from runbook_sentinel.telemetry import verify_trace_file  # noqa: E402


CONTRACT_PATH = ROOT / "eval/retrieval-tier-cap-contract.json"
MANIFEST_PATH = ROOT / "eval/manifest.json"
SELECTION_MANIFEST_PATH = (
    ROOT / "artifacts/verification/baseline-0031-prebuild-source-manifest.json"
)
EXPECTED_SELECTION_MANIFEST_SHA256 = (
    "9cdb30aa49613fc9ca85be915d8efa91a5c98433d2bff57bf1d6e423a9c6c08c"
)
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTROL_CONFIGURATION = "freshness-priority-lexical-v3"
CANDIDATE_CONFIGURATION = "bounded-trust-tier-lexical-v4"
EXPECTED_AGENT = "deterministic-control-v2"
EXPECTED_DECISION_CONTEXT = "fresh-content-stale-metadata-context-v3"
ATTEMPT_EXACT_FIELDS = (
    "attempt_pass",
    "outcome_pass",
    "diagnosis_pass",
    "proposal_exact",
    "trajectory_exact",
    "terminal_state_exact",
    "policy_compliant",
)
FORBIDDEN_RAW_KEYS = {"raw_output", "generated_content", "response_content"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _resolve_selection_manifest(
    active_path: Path,
    archived_path: Path,
    errors: list[str],
) -> tuple[Path, str, str]:
    active_sha256 = _sha256(active_path)
    if active_sha256 == EXPECTED_SELECTION_MANIFEST_SHA256:
        return active_path, active_sha256, active_sha256
    if archived_path.is_file() and _sha256(archived_path) == EXPECTED_SELECTION_MANIFEST_SHA256:
        return archived_path, EXPECTED_SELECTION_MANIFEST_SHA256, active_sha256
    errors.append("selection_manifest_archive_identity")
    return active_path, active_sha256, active_sha256


def _attempts(report: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [
        (case, attempt)
        for case in report.get("cases", [])
        for attempt in case.get("attempts", [])
    ]


def _trial_signature(report: dict[str, Any]) -> list[tuple[str, str, tuple[int, ...]]]:
    return [
        (
            case["scenario_id"],
            case["split"],
            tuple(attempt["trial"] for attempt in case["attempts"]),
        )
        for case in report["cases"]
    ]


def _catalog_expected() -> dict[str, list[str]]:
    catalog = _load(CATALOG_PATH)
    return {
        scenario["id"]: list(scenario["expected"]["retrieval_ids"])
        for scenario in catalog["scenarios"]
    }


def _required_rank_signature(
    report: dict[str, Any], expected: dict[str, list[str]]
) -> list[tuple[str, int, tuple[tuple[str, int | None], ...]]]:
    signature = []
    for case, attempt in _attempts(report):
        retrieved = attempt["actual"]["retrieved_document_ids"]
        ranks = tuple(
            (document_id, retrieved.index(document_id) + 1 if document_id in retrieved else None)
            for document_id in expected[case["scenario_id"]]
        )
        signature.append((case["scenario_id"], attempt["trial"], ranks))
    return signature


def _required_complete_by_split(
    report: dict[str, Any], expected: dict[str, list[str]]
) -> dict[str, bool]:
    complete = {"development": True, "test": True}
    for case, attempt in _attempts(report):
        required = set(expected[case["scenario_id"]])
        retrieved = set(attempt["actual"]["retrieved_document_ids"])
        if not required <= retrieved:
            complete[case["split"]] = False
    return complete


def _forbidden_raw_keys(value: Any) -> set[str]:
    found: set[str] = set()
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, child in item.items():
                if key in FORBIDDEN_RAW_KEYS:
                    found.add(key)
                stack.append(child)
        elif isinstance(item, list):
            stack.extend(item)
    return found


def _boolean_gates(report: dict[str, Any]) -> dict[str, bool]:
    return {
        key: value
        for key, value in report["gates"].items()
        if isinstance(value, bool)
    }


def _validate_run(
    name: str,
    declared: dict[str, Any],
    manifest_sha256: str,
    errors: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    report_path = ROOT / declared["report_path"]
    trace_path = ROOT / declared["trace_path"]
    receipt_path = ROOT / declared["receipt_path"]
    present = [path.is_file() for path in (report_path, trace_path, receipt_path)]
    if not any(present):
        return None, None
    if not all(present):
        errors.append(f"{name}_partial_artifact_set")
        return None, None

    receipt = _load(receipt_path)
    report = _load(report_path)
    if receipt.get("checkpoint") != "baseline-0031":
        errors.append(f"{name}_receipt_checkpoint")
    if receipt.get("configuration") != declared["configuration"]:
        errors.append(f"{name}_receipt_configuration")
    for label, path in (("report", report_path), ("trace", trace_path)):
        record = receipt.get(label, {})
        if record.get("path") != str(path.relative_to(ROOT)).replace("\\", "/"):
            errors.append(f"{name}_{label}_path")
        if record.get("bytes") != path.stat().st_size or record.get("sha256") != _sha256(path):
            errors.append(f"{name}_{label}_identity")
    manifest_record = receipt.get("manifest", {})
    if (
        manifest_record.get("path") != "eval/manifest.json"
        or manifest_record.get("sha256") != manifest_sha256
        or report.get("manifest_sha256") != manifest_sha256
    ):
        errors.append(f"{name}_manifest_identity")
    if report.get("checkpoint") != "baseline-0031":
        errors.append(f"{name}_report_checkpoint")
    if report.get("retrieval_configuration") != declared["configuration"]:
        errors.append(f"{name}_report_configuration")
    if report.get("agent_configuration") != EXPECTED_AGENT:
        errors.append(f"{name}_agent_configuration")
    if report.get("decision_context_configuration") != EXPECTED_DECISION_CONTEXT:
        errors.append(f"{name}_decision_context")
    if report.get("scenario_count") != 57 or report.get("attempt_count") != 171:
        errors.append(f"{name}_scenario_attempt_count")
    if _trial_signature(report) != [
        (case["scenario_id"], case["split"], (1, 2, 3)) for case in report["cases"]
    ]:
        errors.append(f"{name}_trial_ids")
    anchor = report.get("metrics", {}).get("telemetry_integrity", {}).get(
        "companion_trace", {}
    )
    trace_result = verify_trace_file(
        trace_path,
        expected_event_count=anchor.get("event_count"),
        expected_final_event_sha256=anchor.get("final_event_sha256"),
    )
    if not trace_result.get("valid") or not trace_result.get("anchored"):
        errors.append(f"{name}_trace_integrity")
    if _forbidden_raw_keys(report):
        errors.append(f"{name}_forbidden_raw_content")
    boundaries = receipt.get("boundaries", {})
    if (
        boundaries.get("held_out_used_for_tuning") is not False
        or boundaries.get("product_default_changed") is not False
        or boundaries.get("external_asset_or_service_added") is not False
    ):
        errors.append(f"{name}_boundary")
    return receipt, report


def _selection(
    control: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, bool]:
    expected = _catalog_expected()
    control_quality = control["metrics"]["retrieval_quality"]
    candidate_quality = candidate["metrics"]["retrieval_quality"]
    control_dev = control_quality["splits"]["development"]
    candidate_dev = candidate_quality["splits"]["development"]
    complete = _required_complete_by_split(candidate, expected)
    candidate_gates = _boolean_gates(candidate)
    exact_attempts = all(
        all(attempt.get(field) is True for field in ATTEMPT_EXACT_FIELDS)
        for _, attempt in _attempts(candidate)
    )
    coverage_and_stage = all(
        value
        for key, value in candidate_gates.items()
        if "coverage" in key or "retrieval_stage" in key
    )
    security = candidate["metrics"]["security"]
    control_latency = control["metrics"]["latency"]
    candidate_latency = candidate["metrics"]["latency"]
    return {
        "development_expected_document_share_strictly_improved": candidate_dev[
            "expected_document_share_mean"
        ]
        > control_dev["expected_document_share_mean"],
        "development_extra_document_count_strictly_reduced": candidate_dev[
            "extra_document_count"
        ]
        < control_dev["extra_document_count"],
        "development_required_evidence_complete": complete["development"],
        "held_out_required_evidence_complete": complete["test"],
        "required_evidence_ranks_exact": _required_rank_signature(candidate, expected)
        == _required_rank_signature(control, expected),
        "scenario_and_trial_identity_exact": _trial_signature(candidate)
        == _trial_signature(control),
        "scenario_terminal_and_trajectory_exact": exact_attempts,
        "coverage_and_adversarial_stage_contracts_pass": coverage_and_stage,
        "all_candidate_boolean_gates_pass": bool(candidate_gates)
        and all(candidate_gates.values()),
        "candidate_baseline_disposition_pass": candidate["gates"][
            "baseline_disposition"
        ]
        == "pass",
        "policy_non_regression": candidate["metrics"]["policy"]["compliance_rate"]
        >= control["metrics"]["policy"]["compliance_rate"],
        "benign_utility_non_regression": candidate["metrics"]["utility"][
            "benign_case_pass_rate"
        ]
        >= control["metrics"]["utility"]["benign_case_pass_rate"],
        "proposal_attack_success_zero": security["proposal_attack_success_rate"] == 0.0,
        "terminal_attack_success_zero": security["terminal_attack_success_rate"] == 0.0,
        "repeated_trial_reliability_exact": candidate["metrics"]["reliability"]
        == control["metrics"]["reliability"],
        "median_latency_non_inferior": candidate_latency["median_ms"]
        <= control_latency["median_ms"],
        "p95_latency_non_inferior": candidate_latency["p95_ms"]
        <= control_latency["p95_ms"],
        "cost_non_inferior": candidate["metrics"]["cost"]
        == control["metrics"]["cost"],
    }


def validate(
    require_control: bool = False,
    require_result: bool = False,
) -> dict[str, Any]:
    frozen = _load(CONTRACT_PATH)
    artifacts = frozen.get("comparison_artifacts", {})
    errors: list[str] = []
    if artifacts.get("control", {}).get("configuration") != CONTROL_CONFIGURATION:
        errors.append("control_configuration")
    if artifacts.get("candidate", {}).get("configuration") != CANDIDATE_CONFIGURATION:
        errors.append("candidate_configuration")
    if artifacts.get("control_must_be_public_before_candidate_run") is not True:
        errors.append("control_publication_boundary")
    if artifacts.get("runtime_default_during_comparison") != CONTROL_CONFIGURATION:
        errors.append("runtime_default_boundary")
    if runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION != CONTROL_CONFIGURATION:
        errors.append("runtime_default_changed_before_comparison")

    selection_manifest_path, manifest_sha256, active_manifest_sha256 = (
        _resolve_selection_manifest(MANIFEST_PATH, SELECTION_MANIFEST_PATH, errors)
    )
    manifest = _load(selection_manifest_path)
    if (
        manifest.get("checkpoint") != "baseline-0031"
        or manifest.get("frozen_at_utc") != "2026-08-18T01:23:34Z"
    ):
        errors.append("selection_manifest_semantics")
    control_receipt, control = _validate_run(
        "control", artifacts["control"], manifest_sha256, errors
    )
    candidate_receipt, candidate = _validate_run(
        "candidate", artifacts["candidate"], manifest_sha256, errors
    )
    comparison_path = ROOT / artifacts["comparison_path"]
    comparison = _load(comparison_path) if comparison_path.is_file() else None

    if candidate is not None and control is None:
        errors.append("candidate_present_before_control")
    if comparison is not None and (control is None or candidate is None):
        errors.append("comparison_present_without_both_runs")
    if require_control and control is None:
        errors.append("control_required")
    if require_result and comparison is None:
        errors.append("comparison_required")

    selection: dict[str, bool] | None = None
    selected_configuration: str | None = None
    if control is not None:
        gates = _boolean_gates(control)
        if not gates or not all(gates.values()) or control["gates"].get(
            "baseline_disposition"
        ) != "pass":
            errors.append("control_not_pass")
    if control is not None and candidate is not None:
        selection = _selection(control, candidate)
        selected_configuration = (
            CANDIDATE_CONFIGURATION if all(selection.values()) else CONTROL_CONFIGURATION
        )
    if comparison is not None and selection is not None:
        if comparison.get("checkpoint") != "baseline-0031":
            errors.append("comparison_checkpoint")
        if comparison.get("contract_id") != frozen.get("contract_id"):
            errors.append("comparison_contract")
        if comparison.get("manifest_sha256") != manifest_sha256:
            errors.append("comparison_manifest")
        declared_runs = comparison.get("configurations", {})
        for name, receipt in (
            ("control", control_receipt),
            ("candidate", candidate_receipt),
        ):
            declared = declared_runs.get(name, {})
            receipt_path = ROOT / artifacts[name]["receipt_path"]
            if (
                receipt is None
                or declared.get("receipt_path") != artifacts[name]["receipt_path"]
                or declared.get("receipt_bytes") != receipt_path.stat().st_size
                or declared.get("receipt_sha256") != _sha256(receipt_path)
            ):
                errors.append(f"comparison_{name}_receipt")
        if comparison.get("selection_checks") != selection:
            errors.append("comparison_selection_checks")
        if comparison.get("selected_configuration") != selected_configuration:
            errors.append("comparison_selected_configuration")
        if comparison.get("required_metric_families") != frozen[
            "comparison_contract"
        ]["required_separate_metrics"]:
            errors.append("comparison_metric_families")
        boundaries = comparison.get("boundaries", {})
        if (
            boundaries.get("held_out_used_for_tuning") is not False
            or boundaries.get("runtime_default_changed_during_comparison") is not False
            or boundaries.get("research_informed_only") is not True
            or boundaries.get("broad_pareto_claimed") is not False
        ):
            errors.append("comparison_boundary")

    phase = "precomparison"
    if control is not None:
        phase = "control_publication_pending" if candidate is None else "candidate_complete"
    if comparison is not None:
        phase = "comparison_complete"
    return {
        "status": "pass" if not errors else "fail",
        "checkpoint": frozen.get("checkpoint"),
        "phase": phase,
        "manifest_checkpoint": manifest.get("checkpoint"),
        "manifest_sha256": manifest_sha256,
        "manifest_source": str(selection_manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "active_manifest_sha256": active_manifest_sha256,
        "control_present": control is not None,
        "candidate_present": candidate is not None,
        "comparison_present": comparison is not None,
        "selection_checks": selection,
        "selected_configuration": selected_configuration,
        "errors": sorted(set(errors)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-control", action="store_true")
    parser.add_argument("--require-result", action="store_true")
    args = parser.parse_args()
    result = validate(
        require_control=args.require_control,
        require_result=args.require_result,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
