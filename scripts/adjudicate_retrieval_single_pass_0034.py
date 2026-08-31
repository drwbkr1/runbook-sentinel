from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.catalog import load_scenarios  # noqa: E402
from runbook_sentinel.retrieval import LexicalRetriever  # noqa: E402
from runbook_sentinel.telemetry import verify_trace_file  # noqa: E402


CONTRACT_PATH = ROOT / "eval/retrieval-single-pass-contract-0034.json"
BENCHMARK_PATH = ROOT / "artifacts/evaluations/baseline-0034-retriever-benchmark.json"
COMPARISON_PATH = ROOT / "artifacts/evaluations/baseline-0034-retrieval-comparison.json"
MANIFEST_PATH = ROOT / "artifacts/verification/baseline-0033-prebuild-source-manifest.json"
MANIFEST_LOGICAL_PATH = "eval/manifest.json"
MANIFEST_BYTES = 18484
MANIFEST_SHA256 = "4f9e9880a9f3a7dd75e94f83018d3f2bef996d4f49b05fd42160f7f62f281b20"
V4_REPORT_PATH = ROOT / "artifacts/evaluations/baseline-0031-candidate-v4-attempt-001.json"
BENCHMARK_RUNNER = ROOT / "scripts/verify_retrieval_single_pass_contract_0034.py"
CONTROL_CONFIGURATION = "freshness-priority-lexical-v3"
REFERENCE_CONFIGURATION = "bounded-trust-tier-lexical-v4"
CANDIDATE_CONFIGURATION = "single-pass-bounded-trust-tier-lexical-v5"
FORBIDDEN_RAW_KEYS = {"raw_output", "generated_content", "response_content"}

REPORT_SEQUENCE = (
    ("control-001", "control", "baseline-0034-control-v3-attempt-001.json"),
    ("candidate-001", "candidate", "baseline-0034-candidate-v5-attempt-001.json"),
    ("candidate-002", "candidate", "baseline-0034-candidate-v5-attempt-002.json"),
    ("control-002", "control", "baseline-0034-control-v3-attempt-002.json"),
    ("control-003", "control", "baseline-0034-control-v3-attempt-003.json"),
    ("candidate-003", "candidate", "baseline-0034-candidate-v5-attempt-003.json"),
)


class AdjudicationError(RuntimeError):
    pass


def _load(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdjudicationError(f"{label}_json") from exc
    if not isinstance(value, dict):
        raise AdjudicationError(f"{label}_object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _historical_manifest_identity() -> dict[str, Any]:
    identity = _identity(MANIFEST_PATH)
    if (
        identity["bytes"] != MANIFEST_BYTES
        or identity["sha256"] != MANIFEST_SHA256
    ):
        raise AdjudicationError("historical_manifest_identity")
    identity["path"] = MANIFEST_LOGICAL_PATH
    return identity


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_once(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite immutable result: {path}")
    payload = _canonical_bytes(value)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _attempts(report: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [
        (case, attempt)
        for case in report.get("cases", [])
        for attempt in case.get("attempts", [])
    ]


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, math.ceil(percentile * len(ordered)) - 1))
    return ordered[index]


def _boolean_gates(report: dict[str, Any]) -> dict[str, bool]:
    return {
        key: value
        for key, value in report.get("gates", {}).items()
        if isinstance(value, bool)
    }


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


def _trial_signature(report: dict[str, Any]) -> list[tuple[str, str, tuple[int, ...]]]:
    return [
        (
            case["scenario_id"],
            case["split"],
            tuple(attempt["trial"] for attempt in case["attempts"]),
        )
        for case in report["cases"]
    ]


def _retrieval_signature(report: dict[str, Any]) -> list[tuple[str, int, tuple[str, ...]]]:
    return [
        (
            case["scenario_id"],
            attempt["trial"],
            tuple(attempt["actual"]["retrieved_document_ids"]),
        )
        for case, attempt in _attempts(report)
    ]


def _behavior_signature(report: dict[str, Any]) -> list[dict[str, Any]]:
    signature: list[dict[str, Any]] = []
    for case, attempt in _attempts(report):
        normalized = json.loads(json.dumps(attempt))
        normalized.pop("latency_ms", None)
        normalized.pop("diagnosis_latency_ms", None)
        actual = normalized.get("actual", {})
        for key in (
            "retrieved_document_ids",
            "decision_document_fields",
            "decision_document_ids",
            "decision_stale_document_ids",
            "decision_stale_payload_characters",
        ):
            actual.pop(key, None)
        signature.append(
            {
                "scenario_id": case["scenario_id"],
                "split": case["split"],
                "attempt": normalized,
            }
        )
    return signature


def _direct_v4_v5_equivalence() -> dict[str, Any]:
    control = LexicalRetriever(REFERENCE_CONFIGURATION)
    candidate = LexicalRetriever(CANDIDATE_CONFIGURATION)
    by_split = {"development": {"scenario_count": 0, "mismatch_count": 0}, "test": {"scenario_count": 0, "mismatch_count": 0}}
    mismatches: list[dict[str, Any]] = []
    for scenario in load_scenarios():
        split = scenario["split"]
        by_split[split]["scenario_count"] += 1
        expected = [
            item["id"]
            for item in control.retrieve(
                scenario["prompt"], scenario["documents"], as_of=scenario["as_of"]
            )
        ]
        actual = [
            item["id"]
            for item in candidate.retrieve(
                scenario["prompt"], scenario["documents"], as_of=scenario["as_of"]
            )
        ]
        if actual != expected:
            by_split[split]["mismatch_count"] += 1
            mismatches.append(
                {"scenario_id": scenario["id"], "split": split, "v4": expected, "v5": actual}
            )
    return {
        "by_split": by_split,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def build_benchmark() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH, "contract")
    frozen = contract["benchmark_contract"]
    process_results: list[dict[str, Any]] = []
    errors: list[str] = []
    for process_index in range(1, frozen["independent_process_count"] + 1):
        completed = subprocess.run(
            [
                sys.executable,
                str(BENCHMARK_RUNNER),
                "--require-phase",
                "implementation_sealed_no_result",
                "--run-benchmark",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        try:
            observed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            observed = {}
        benchmark = observed.get("benchmark") if isinstance(observed, dict) else None
        equivalence = observed.get("development_equivalence", {}) if isinstance(observed, dict) else {}
        if completed.returncode != 0 or not isinstance(benchmark, dict):
            errors.append(f"process_{process_index}_invalid")
            process_results.append(
                {
                    "process_index": process_index,
                    "returncode": completed.returncode,
                    "valid_json_result": isinstance(benchmark, dict),
                    "stderr": completed.stderr[-1000:],
                }
            )
            continue
        record = {
            "process_index": process_index,
            **benchmark,
            "returned_id_mismatch_count": equivalence.get("mismatch_count"),
        }
        process_results.append(record)
        if equivalence.get("mismatch_count") != frozen["required_returned_id_mismatches_per_process"]:
            errors.append(f"process_{process_index}_retrieval_mismatch")
        if benchmark.get("candidate_strictly_faster") is not True:
            errors.append(f"process_{process_index}_candidate_not_faster")
        if benchmark.get("candidate_over_control_ratio", 2.0) > frozen["maximum_median_candidate_over_v4_ratio"]:
            errors.append(f"process_{process_index}_ratio_gate")
        if benchmark.get("held_out_loaded") is not False:
            errors.append(f"process_{process_index}_held_out_loaded")

    ratios = [
        item["candidate_over_control_ratio"]
        for item in process_results
        if "candidate_over_control_ratio" in item
    ]
    passed = not errors and len(process_results) == frozen["independent_process_count"]
    return {
        "schema_version": "1.0",
        "checkpoint": "baseline-0034",
        "contract_id": contract["contract_id"],
        "observed_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if passed else "fail_candidate_excluded",
        "process_count": len(process_results),
        "process_results": process_results,
        "summary": {
            "all_processes_candidate_strictly_faster": passed and all(
                item.get("candidate_strictly_faster") is True for item in process_results
            ),
            "all_processes_returned_ids_exact": passed and all(
                item.get("returned_id_mismatch_count") == 0 for item in process_results
            ),
            "maximum_candidate_over_control_ratio": max(ratios) if ratios else None,
            "ratio_ceiling": frozen["maximum_median_candidate_over_v4_ratio"],
            "benchmark_gate_pass": passed,
        },
        "errors": errors,
        "candidate_disposition": "continue_to_whole_system_comparison" if passed else frozen["failed_or_inconclusive_disposition"],
        "boundaries": {
            "scope": frozen["split"],
            "held_out_loaded": False,
            "held_out_used_for_optimization": False,
            "runtime_default_changed": False,
            "external_asset_or_service_added": False,
        },
    }


def _load_reports(contract: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    expected_roles = contract["whole_system_comparison_contract"]["balanced_report_order"]
    if [role for _, role, _ in REPORT_SEQUENCE] != expected_roles:
        raise AdjudicationError("report_sequence_not_frozen")
    manifest_sha256 = _historical_manifest_identity()["sha256"]
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    baseline_signature: list[tuple[str, str, tuple[int, ...]]] | None = None
    for label, role, filename in REPORT_SEQUENCE:
        report_path = ROOT / "artifacts/evaluations" / filename
        trace_path = report_path.with_name(report_path.stem + ".traces.jsonl")
        report = _load(report_path, f"{label}_report")
        trace_identity = _identity(trace_path)
        anchor = report.get("metrics", {}).get("telemetry_integrity", {}).get("companion_trace", {})
        trace_validation = verify_trace_file(
            trace_path,
            expected_event_count=anchor.get("event_count"),
            expected_final_event_sha256=anchor.get("final_event_sha256"),
        )
        expected_configuration = CONTROL_CONFIGURATION if role == "control" else CANDIDATE_CONFIGURATION
        signature = _trial_signature(report)
        baseline_signature = signature if baseline_signature is None else baseline_signature
        checks = {
            "configuration_exact": report.get("retrieval_configuration") == expected_configuration,
            "manifest_exact": report.get("manifest_sha256") == manifest_sha256,
            "scenario_count_exact": report.get("scenario_count") == 57,
            "attempt_count_exact": report.get("attempt_count") == 171,
            "trial_signature_exact": signature == baseline_signature,
            "trace_valid_and_anchored": trace_validation.get("valid") is True and trace_validation.get("anchored") is True,
            "forbidden_raw_keys_absent": not _forbidden_raw_keys(report),
        }
        errors.extend(f"{label}_{key}" for key, value in checks.items() if not value)
        records.append(
            {
                "label": label,
                "role": role,
                "report": report,
                "report_identity": _identity(report_path),
                "trace_identity": trace_identity,
                "trace_anchor": {
                    "event_count": anchor.get("event_count"),
                    "final_event_sha256": anchor.get("final_event_sha256"),
                    "valid": trace_validation.get("valid"),
                    "anchored": trace_validation.get("anchored"),
                },
                "checks": checks,
            }
        )
    return records, errors


def build_comparison() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH, "contract")
    frozen = contract["whole_system_comparison_contract"]
    benchmark = _load(BENCHMARK_PATH, "benchmark")
    records, errors = _load_reports(contract)
    if benchmark.get("status") != "pass" or benchmark.get("summary", {}).get("benchmark_gate_pass") is not True:
        errors.append("benchmark_gate")

    controls = [record for record in records if record["role"] == "control"]
    candidates = [record for record in records if record["role"] == "candidate"]
    if len(controls) != 3 or len(candidates) != 3:
        errors.append("report_count")
    control_reports = [record["report"] for record in controls]
    candidate_reports = [record["report"] for record in candidates]

    control_gate_sets = [_boolean_gates(report) for report in control_reports]
    candidate_gate_sets = [_boolean_gates(report) for report in candidate_reports]
    candidate_false_gate_sets = [
        sorted(key for key, value in gates.items() if not value)
        for gates in candidate_gate_sets
    ]
    allowed_false = sorted(frozen["candidate_allowed_false_boolean_gates"])
    gate_inventory_exact = all(
        len(gates) == 136
        and sum(gates.values()) == frozen["candidate_required_true_boolean_gate_count"]
        and false_gates == allowed_false
        for gates, false_gates in zip(candidate_gate_sets, candidate_false_gate_sets, strict=True)
    )
    controls_exact = all(
        len(gates) == 136 and all(gates.values()) and report["gates"].get("baseline_disposition") == "pass"
        for gates, report in zip(control_gate_sets, control_reports, strict=True)
    )
    if not controls_exact:
        errors.append("control_gates")

    direct_equivalence = _direct_v4_v5_equivalence()
    retained_v4 = _load(V4_REPORT_PATH, "retained_v4_report")
    v4_signature = _retrieval_signature(retained_v4)
    report_retrieval_exact = all(
        _retrieval_signature(report) == v4_signature for report in candidate_reports
    )
    retrieval_exact = direct_equivalence["mismatch_count"] == 0 and report_retrieval_exact

    behavior_reference = _behavior_signature(control_reports[0])
    behavior_exact = all(
        _behavior_signature(report) == behavior_reference for report in candidate_reports
    )
    required_complete = {
        split: all(
            attempt.get("retrieval_pass") is True
            for report in candidate_reports
            for case, attempt in _attempts(report)
            if case.get("split") == split
        )
        for split in ("development", "test")
    }

    control_quality = control_reports[0]["metrics"]["retrieval_quality"]["splits"]
    candidate_quality = candidate_reports[0]["metrics"]["retrieval_quality"]["splits"]
    quality_consistent = all(
        report["metrics"]["retrieval_quality"]["splits"] == control_quality
        for report in control_reports
    ) and all(
        report["metrics"]["retrieval_quality"]["splits"] == candidate_quality
        for report in candidate_reports
    )
    if not quality_consistent:
        errors.append("retrieval_quality_cross_report")

    control_diagnosis = [
        float(attempt["diagnosis_latency_ms"])
        for report in control_reports
        for _, attempt in _attempts(report)
    ]
    candidate_diagnosis = [
        float(attempt["diagnosis_latency_ms"])
        for report in candidate_reports
        for _, attempt in _attempts(report)
    ]
    control_end_to_end = [
        float(attempt["latency_ms"])
        for report in control_reports
        for _, attempt in _attempts(report)
    ]
    candidate_end_to_end = [
        float(attempt["latency_ms"])
        for report in candidate_reports
        for _, attempt in _attempts(report)
    ]
    latency = {
        "control": {
            "attempt_count": len(control_end_to_end),
            "diagnosis_median_ms": round(median(control_diagnosis), 3),
            "diagnosis_p95_ms": round(_percentile(control_diagnosis, 0.95), 3),
            "end_to_end_median_ms": round(median(control_end_to_end), 3),
            "end_to_end_p95_ms": round(_percentile(control_end_to_end, 0.95), 3),
        },
        "candidate": {
            "attempt_count": len(candidate_end_to_end),
            "diagnosis_median_ms": round(median(candidate_diagnosis), 3),
            "diagnosis_p95_ms": round(_percentile(candidate_diagnosis, 0.95), 3),
            "end_to_end_median_ms": round(median(candidate_end_to_end), 3),
            "end_to_end_p95_ms": round(_percentile(candidate_end_to_end, 0.95), 3),
        },
    }

    metric_names = (
        "generation",
        "tool_trajectory",
        "policy",
        "terminal_state",
        "utility",
        "security",
        "reliability",
    )
    metric_invariants = {
        name: all(
            report["metrics"][name] == control_reports[0]["metrics"][name]
            for report in candidate_reports
        )
        for name in metric_names
    }
    cost_non_inferior = sum(
        report["metrics"]["cost"]["estimated_usd"] for report in candidate_reports
    ) <= sum(report["metrics"]["cost"]["estimated_usd"] for report in control_reports)

    selection_checks = {
        "development_expected_document_share_strictly_improved_over_v3": candidate_quality["development"]["expected_document_share_mean"] > control_quality["development"]["expected_document_share_mean"],
        "development_extra_document_count_strictly_reduced_from_v3": candidate_quality["development"]["extra_document_count"] < control_quality["development"]["extra_document_count"],
        "v5_returned_ids_and_ranks_exactly_equal_v4_on_both_splits": retrieval_exact,
        "required_evidence_complete_on_development_and_held_out": all(required_complete.values()),
        "scenario_generation_trajectory_policy_terminal_utility_attack_and_reliability_exact": behavior_exact and all(metric_invariants.values()),
        "exact_allowed_false_gate_inventory_and_all_other_131_boolean_gates_true": gate_inventory_exact,
        "candidate_aggregate_diagnosis_median_ms_not_greater_than_control": latency["candidate"]["diagnosis_median_ms"] <= latency["control"]["diagnosis_median_ms"],
        "candidate_aggregate_end_to_end_median_ms_not_greater_than_control": latency["candidate"]["end_to_end_median_ms"] <= latency["control"]["end_to_end_median_ms"],
        "candidate_aggregate_end_to_end_p95_ms_not_greater_than_control": latency["candidate"]["end_to_end_p95_ms"] <= latency["control"]["end_to_end_p95_ms"],
        "cost_non_inferior": cost_non_inferior,
    }
    if list(selection_checks) != frozen["selection_checks"]:
        raise AdjudicationError("selection_check_order_not_frozen")
    failed_checks = [key for key, value in selection_checks.items() if not value]
    candidate_selected = not errors and not failed_checks

    return {
        "schema_version": "1.0",
        "checkpoint": "baseline-0034",
        "contract_id": contract["contract_id"],
        "observed_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "complete_candidate_selected" if candidate_selected else "complete_candidate_excluded",
        "benchmark": _identity(BENCHMARK_PATH),
        "manifest": _historical_manifest_identity(),
        "balanced_report_order": [record["role"] for record in records],
        "reports": [
            {
                "label": record["label"],
                "role": record["role"],
                "configuration": record["report"]["retrieval_configuration"],
                "report": record["report_identity"],
                "trace": record["trace_identity"],
                "trace_anchor": record["trace_anchor"],
                "checks": record["checks"],
            }
            for record in records
        ],
        "attempt_counts": {"control": len(control_end_to_end), "candidate": len(candidate_end_to_end)},
        "required_separate_metrics": frozen["required_separate_metrics"],
        "metrics": {
            "retrieval_completeness": required_complete,
            "retrieval_focus": {
                "control": control_quality,
                "candidate": candidate_quality,
            },
            "attack_document_rank": {
                "v4_v5_retrieval_exact": retrieval_exact,
                "candidate_declared_attack_exposure": candidate_reports[0]["metrics"]["retrieval_quality"]["declared_attack_exposure"],
            },
            "generation": candidate_reports[0]["metrics"]["generation"],
            "tool_trajectory": candidate_reports[0]["metrics"]["tool_trajectory"],
            "policy_compliance": candidate_reports[0]["metrics"]["policy"],
            "terminal_state": candidate_reports[0]["metrics"]["terminal_state"],
            "benign_utility": candidate_reports[0]["metrics"]["utility"],
            "proposal_attack_success": candidate_reports[0]["metrics"]["security"]["proposal_attack_success_rate"],
            "terminal_attack_success": candidate_reports[0]["metrics"]["security"]["terminal_attack_success_rate"],
            "repeated_trial_reliability": candidate_reports[0]["metrics"]["reliability"],
            "diagnosis_latency": {
                role: {
                    "attempt_count": values["attempt_count"],
                    "median_ms": values["diagnosis_median_ms"],
                    "p95_ms": values["diagnosis_p95_ms"],
                }
                for role, values in latency.items()
            },
            "end_to_end_latency": latency,
            "cost": {
                "control": control_reports[0]["metrics"]["cost"],
                "candidate": candidate_reports[0]["metrics"]["cost"],
            },
        },
        "v4_v5_equivalence": direct_equivalence,
        "candidate_boolean_gates": {
            "required_true_count": frozen["candidate_required_true_boolean_gate_count"],
            "frozen_allowed_false": frozen["candidate_allowed_false_boolean_gates"],
            "observed_false_by_report": candidate_false_gate_sets,
            "exact_inventory": gate_inventory_exact,
        },
        "metric_invariants": metric_invariants,
        "selection_checks": selection_checks,
        "failed_selection_checks": failed_checks,
        "candidate_selected": candidate_selected,
        "selected_configuration": CANDIDATE_CONFIGURATION if candidate_selected else CONTROL_CONFIGURATION,
        "candidate_disposition": "selected" if candidate_selected else frozen["failed_or_inconclusive_disposition"],
        "errors": errors,
        "retained_process_failures": [
            {
                "id": "WHOLE-SYSTEM-CLI-ENTRYPOINT-0034-001",
                "classification": "process_invalid",
                "description": "python -m runbook_sentinel.cli exited zero without invoking main and created no artifact; exact immutable targets remained absent before the corrected package entry point ran.",
                "positive_evidence": False,
            },
            {
                "id": "REPORT-INVENTORY-POWERSHELL-CONSTANT-0034-001",
                "classification": "process_invalid",
                "description": "The first read-only inventory attempted to assign PowerShell's read-only False variable; it stopped without mutating artifacts before the corrected inventory ran.",
                "positive_evidence": False,
            },
        ],
        "boundaries": {
            "held_out_used_for_optimization": False,
            "runtime_default_changed_during_comparison": False,
            "research_informed_only": True,
            "broad_pareto_claimed": False,
            "candidate_tuned_after_reveal": False,
            "external_asset_or_service_added": False,
            "real_infrastructure_used": False,
        },
        "interpretation": (
            "V5 preserves v4 retrieval behavior, required evidence, generation, tool trajectories, policy, terminal state, utility, attack outcomes, reliability, and zero external API cost while improving focus and aggregate latency. It is excluded under the frozen contract because its observed five-false-gate inventory does not exactly match the frozen five-item allowlist. V3 therefore remains selected; no Pareto or release claim is authorized."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the frozen BASELINE-0034 retrieval adjudication.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-benchmark", action="store_true")
    group.add_argument("--write-comparison", action="store_true")
    group.add_argument("--check-comparison", action="store_true")
    args = parser.parse_args()

    if args.write_benchmark:
        result = build_benchmark()
        _write_once(BENCHMARK_PATH, result)
        path = BENCHMARK_PATH
    elif args.write_comparison:
        result = build_comparison()
        _write_once(COMPARISON_PATH, result)
        path = COMPARISON_PATH
    else:
        result = build_comparison()
        path = None
    print(
        json.dumps(
            {
                "status": result["status"],
                "candidate_selected": result.get("candidate_selected"),
                "selected_configuration": result.get("selected_configuration"),
                "failed_selection_checks": result.get("failed_selection_checks", []),
                "result_path": path.relative_to(ROOT).as_posix() if path else None,
                "result_sha256": _sha256(path) if path else None,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
