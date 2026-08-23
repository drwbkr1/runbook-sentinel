from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.catalog import load_scenarios  # noqa: E402
from runbook_sentinel.evidence import (  # noqa: E402
    FRESHNESS_SECONDS,
    PROJECT_EVIDENCE_KINDS,
    parse_timestamp,
)
from runbook_sentinel import retrieval as runtime_retrieval  # noqa: E402


CONTRACT_PATH = ROOT / "eval/retrieval-single-pass-contract-0034.json"
SOURCE_GATE_PATH = (
    ROOT
    / "artifacts/verification/research-source-gate-baseline-0034-retrieval-latency.json"
)
ORIENTATION_PATH = ROOT / "artifacts/verification/orientation-baseline-0034.json"
PUBLIC_FREEZE_RECEIPT_PATH = (
    ROOT / "artifacts/verification/baseline-0034-preimplementation-freeze-public.json"
)
BENCHMARK_RESULT_PATH = (
    ROOT / "artifacts/evaluations/baseline-0034-retriever-benchmark.json"
)
COMPARISON_RESULT_PATH = (
    ROOT / "artifacts/evaluations/baseline-0034-retrieval-comparison.json"
)
CONTROL_CONFIGURATION = "freshness-priority-lexical-v3"
REFERENCE_CONFIGURATION = "bounded-trust-tier-lexical-v4"
CANDIDATE_CONFIGURATION = "single-pass-bounded-trust-tier-lexical-v5"
ALLOWED_FALSE_GATES = [
    "guidance_not_retrieved_attempt_count_exact",
    "guidance_retrieved_filtered_attempt_count_exact",
    "retrieval_quality_expected_document_share_exact",
    "retrieval_quality_extra_document_attempt_rate_exact",
    "retrieval_quality_guidance_rank_buckets_exact",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _expect(condition: bool, code: str, errors: list[str]) -> None:
    if not condition:
        errors.append(code)


def reference_candidate(
    query: str,
    documents: list[dict[str, Any]],
    limit: int = 4,
    as_of: str | None = None,
) -> list[dict[str, Any]]:
    """Frozen v5 reference used only for contract validation before implementation."""

    query_tokens = runtime_retrieval._tokens(query)
    ranked: list[tuple[float, str, dict[str, Any]]] = []
    for document in documents:
        document_tokens = runtime_retrieval._tokens(
            document.get("content", "")
        ) | runtime_retrieval._tokens(document.get("title", ""))
        overlap = len(query_tokens & document_tokens)
        coverage = overlap / max(1, len(query_tokens))
        kind_bonus = 0.05 if document.get("kind") == "telemetry" else 0.0
        ranked.append((coverage + kind_bonus, document["id"], document))
    ranked.sort(key=lambda item: (-item[0], item[1]))

    reference_time = parse_timestamp(as_of)
    fresh_project_evidence: list[tuple[float, str, dict[str, Any]]] = []
    stale_project_evidence: list[tuple[float, str, dict[str, Any]]] = []
    untrusted_guidance: list[tuple[float, str, dict[str, Any]]] = []
    for item in ranked:
        if item[0] <= 0:
            continue
        document = item[2]
        if document.get("kind") not in PROJECT_EVIDENCE_KINDS:
            untrusted_guidance.append(item)
            continue
        observed_at = parse_timestamp(document.get("observed_at"))
        if reference_time is not None and observed_at is not None:
            age_seconds = (reference_time - observed_at).total_seconds()
            if 0 <= age_seconds <= FRESHNESS_SECONDS:
                fresh_project_evidence.append(item)
                continue
        stale_project_evidence.append(item)

    prioritized = (
        fresh_project_evidence[:2]
        + stale_project_evidence[:1]
        + untrusted_guidance[:1]
    )
    return [document for _, _, document in prioritized[:limit]]


def _candidate_retrieve() -> Callable[..., list[dict[str, Any]]]:
    if CANDIDATE_CONFIGURATION in runtime_retrieval.RETRIEVAL_CONFIGURATIONS:
        return runtime_retrieval.LexicalRetriever(CANDIDATE_CONFIGURATION).retrieve
    return reference_candidate


def _development_equivalence() -> dict[str, Any]:
    scenarios = [
        scenario for scenario in load_scenarios() if scenario.get("split") == "development"
    ]
    control = runtime_retrieval.LexicalRetriever(REFERENCE_CONFIGURATION)
    candidate = _candidate_retrieve()
    mismatches: list[dict[str, Any]] = []
    for scenario in scenarios:
        expected = [
            document["id"]
            for document in control.retrieve(
                scenario["prompt"],
                scenario["documents"],
                as_of=scenario["as_of"],
            )
        ]
        actual = [
            document["id"]
            for document in candidate(
                scenario["prompt"],
                scenario["documents"],
                as_of=scenario["as_of"],
            )
        ]
        if actual != expected:
            mismatches.append(
                {"scenario_id": scenario["id"], "expected": expected, "actual": actual}
            )
    return {
        "split": "development",
        "scenario_count": len(scenarios),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "held_out_loaded": False,
    }


def run_benchmark(
    warmup_sweeps: int = 100,
    rounds: int = 120,
    scenario_sweeps_per_round: int = 80,
) -> dict[str, Any]:
    scenarios = [
        scenario for scenario in load_scenarios() if scenario.get("split") == "development"
    ]
    control = runtime_retrieval.LexicalRetriever(REFERENCE_CONFIGURATION).retrieve
    candidate = _candidate_retrieve()

    for _ in range(warmup_sweeps):
        for scenario in scenarios:
            control(
                scenario["prompt"],
                scenario["documents"],
                as_of=scenario["as_of"],
            )
            candidate(
                scenario["prompt"],
                scenario["documents"],
                as_of=scenario["as_of"],
            )

    control_ns: list[int] = []
    candidate_ns: list[int] = []
    for round_index in range(rounds):
        order = (
            ((control, control_ns), (candidate, candidate_ns))
            if round_index % 2 == 0
            else ((candidate, candidate_ns), (control, control_ns))
        )
        for retrieve, observations in order:
            started = perf_counter_ns()
            for _ in range(scenario_sweeps_per_round):
                for scenario in scenarios:
                    retrieve(
                        scenario["prompt"],
                        scenario["documents"],
                        as_of=scenario["as_of"],
                    )
            observations.append(perf_counter_ns() - started)

    calls_per_round = scenario_sweeps_per_round * len(scenarios)
    control_per_call = median(control_ns) / calls_per_round
    candidate_per_call = median(candidate_ns) / calls_per_round
    ratio = candidate_per_call / control_per_call
    return {
        "scope": "development",
        "held_out_loaded": False,
        "scenario_count": len(scenarios),
        "warmup_sweeps": warmup_sweeps,
        "round_count": rounds,
        "scenario_sweeps_per_round": scenario_sweeps_per_round,
        "calls_per_round": calls_per_round,
        "clock": "time.perf_counter_ns",
        "control_configuration": REFERENCE_CONFIGURATION,
        "candidate_configuration": CANDIDATE_CONFIGURATION,
        "control_median_ns_per_call": round(control_per_call, 3),
        "candidate_median_ns_per_call": round(candidate_per_call, 3),
        "candidate_over_control_ratio": round(ratio, 6),
        "candidate_reduction_percent": round((1 - ratio) * 100, 3),
        "candidate_strictly_faster": candidate_per_call < control_per_call,
    }


def _phase() -> str:
    implemented = CANDIDATE_CONFIGURATION in runtime_retrieval.RETRIEVAL_CONFIGURATIONS
    selected = runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION == CANDIDATE_CONFIGURATION
    results_present = BENCHMARK_RESULT_PATH.is_file() or COMPARISON_RESULT_PATH.is_file()
    if selected:
        return "selected"
    if results_present:
        return "evaluated_unselected"
    if implemented:
        return "implementation_sealed_no_result"
    return "frozen_preimplementation"


def validate(
    contract_path: Path = CONTRACT_PATH,
    require_phase: str | None = None,
    benchmark: bool = False,
) -> dict[str, Any]:
    contract = _load(contract_path)
    errors: list[str] = []

    _expect(contract.get("schema_version") == "1.0", "schema_version", errors)
    _expect(contract.get("checkpoint") == "baseline-0034", "checkpoint", errors)
    _expect(
        contract.get("contract_id") == "single-pass-bounded-trust-tier-retrieval-v1",
        "contract_id",
        errors,
    )
    _expect(contract.get("frozen_before_implementation") is True, "freeze_order", errors)

    start = contract.get("starting_public_checkpoint", {})
    _expect(
        start.get("public_main") == "d62e7cba675997eade87169f5acba14de6452c9b",
        "starting_public_main",
        errors,
    )
    _expect(start.get("tag") == "v0.0.33", "starting_tag", errors)
    _expect(start.get("release_latest") is True, "starting_release_latest", errors)
    _expect(start.get("deployment_count") == 0, "starting_deployment_count", errors)
    _expect(
        start.get("container_image_published") is False,
        "starting_container_publication_boundary",
        errors,
    )

    control = contract.get("accepted_control", {})
    _expect(control.get("configuration") == CONTROL_CONFIGURATION, "control_configuration", errors)
    _expect(control.get("product_default_at_freeze") is True, "control_default", errors)
    _expect(control.get("extra_document_count") == 123, "control_extra_count", errors)

    retained = contract.get("retained_v4_evidence", {})
    _expect(
        retained.get("configuration") == REFERENCE_CONFIGURATION,
        "reference_configuration",
        errors,
    )
    _expect(retained.get("median_latency_non_inferior") is False, "retained_latency_failure", errors)
    _expect(retained.get("selected") is False, "retained_v4_selection", errors)
    _expect(
        retained.get("disposition") == "excluded_latency_noninferior_and_retained",
        "retained_v4_disposition",
        errors,
    )
    for name in ("control_report", "candidate_report", "comparison", "admissibility_result"):
        declared = retained.get(name, {})
        path = ROOT / declared.get("path", "")
        if not path.is_file():
            errors.append(f"{name}_missing")
            continue
        identity = _identity(path)
        _expect(identity.get("bytes") == declared.get("bytes"), f"{name}_bytes", errors)
        _expect(identity.get("sha256") == declared.get("sha256"), f"{name}_sha256", errors)

    candidate = contract.get("frozen_candidate", {})
    _expect(
        candidate.get("configuration") == CANDIDATE_CONFIGURATION,
        "candidate_configuration",
        errors,
    )
    _expect(
        candidate.get("allowed_runtime_path") == "src/runbook_sentinel/retrieval.py",
        "allowed_runtime_path",
        errors,
    )
    _expect(
        candidate.get("tier_caps")
        == {
            "fresh_project_evidence": 2,
            "stale_project_evidence": 1,
            "untrusted_guidance": 1,
        },
        "tier_caps",
        errors,
    )
    _expect(candidate.get("quota_backfill") is False, "quota_backfill", errors)
    _expect(candidate.get("cross_request_cache_added") is False, "cache_boundary", errors)
    _expect(
        candidate.get("default_configuration_changed_before_selection") is False,
        "premature_default_boundary",
        errors,
    )
    for key in (
        "agent_model_prompt_parser_changed",
        "scenario_expected_terminal_split_or_grader_changed",
        "policy_approval_executor_credential_or_authority_changed",
        "tools_dependencies_services_secrets_or_paid_assets_added",
        "external_code_data_model_prompt_metric_or_benchmark_imported",
        "real_infrastructure_added",
    ):
        _expect(candidate.get(key) is False, f"candidate_boundary_{key}", errors)

    benchmark_contract = contract.get("benchmark_contract", {})
    _expect(benchmark_contract.get("split") == "development", "benchmark_split", errors)
    _expect(benchmark_contract.get("held_out_prohibited") is True, "held_out_benchmark_boundary", errors)
    _expect(benchmark_contract.get("independent_process_count") == 5, "benchmark_process_count", errors)
    _expect(
        benchmark_contract.get("maximum_median_candidate_over_v4_ratio") == 0.95,
        "benchmark_ratio_gate",
        errors,
    )

    comparison = contract.get("whole_system_comparison_contract", {})
    _expect(
        comparison.get("control_configuration") == CONTROL_CONFIGURATION,
        "comparison_control",
        errors,
    )
    _expect(
        comparison.get("candidate_configuration") == CANDIDATE_CONFIGURATION,
        "comparison_candidate",
        errors,
    )
    _expect(
        comparison.get("balanced_report_order")
        == ["control", "candidate", "candidate", "control", "control", "candidate"],
        "comparison_order",
        errors,
    )
    _expect(
        comparison.get("held_out_split_used_for_optimization") is False,
        "held_out_optimization_boundary",
        errors,
    )
    _expect(
        comparison.get("candidate_allowed_false_boolean_gates") == ALLOWED_FALSE_GATES,
        "allowed_false_gate_inventory",
        errors,
    )
    _expect(
        comparison.get("candidate_required_true_boolean_gate_count") == 131,
        "candidate_true_gate_count",
        errors,
    )
    _expect(
        comparison.get("no_default_change_before_complete_comparison") is True,
        "comparison_default_boundary",
        errors,
    )

    _expect(ORIENTATION_PATH.is_file(), "orientation_missing", errors)
    if SOURCE_GATE_PATH.is_file():
        source_gate = _load(SOURCE_GATE_PATH)
        _expect(source_gate.get("status") == "pass", "source_gate_status", errors)
        _expect(
            source_gate.get("decision") == "use_for_narrow_specification_basis_without_import",
            "source_gate_decision",
            errors,
        )
        _expect(
            not any(source_gate.get("imports", {}).values()),
            "source_gate_external_import",
            errors,
        )
    else:
        errors.append("source_gate_missing")

    development = _development_equivalence()
    _expect(development["scenario_count"] == 31, "development_scenario_count", errors)
    _expect(development["mismatch_count"] == 0, "development_v4_v5_equivalence", errors)
    _expect(development["held_out_loaded"] is False, "development_held_out_boundary", errors)

    phase = _phase()
    if require_phase is not None:
        _expect(phase == require_phase, "required_phase", errors)
    if phase == "frozen_preimplementation":
        _expect(
            CANDIDATE_CONFIGURATION not in runtime_retrieval.RETRIEVAL_CONFIGURATIONS,
            "implementation_present_before_freeze",
            errors,
        )
        _expect(not BENCHMARK_RESULT_PATH.exists(), "benchmark_present_before_freeze", errors)
        _expect(not COMPARISON_RESULT_PATH.exists(), "comparison_present_before_freeze", errors)
    else:
        _expect(PUBLIC_FREEZE_RECEIPT_PATH.is_file(), "public_freeze_receipt_missing", errors)
    if phase != "selected":
        _expect(
            runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION == CONTROL_CONFIGURATION,
            "default_changed_before_selection",
            errors,
        )

    benchmark_result = run_benchmark() if benchmark else None
    if benchmark_result is not None:
        _expect(benchmark_result["held_out_loaded"] is False, "benchmark_held_out_loaded", errors)
        _expect(benchmark_result["candidate_strictly_faster"] is True, "benchmark_not_faster", errors)

    return {
        "schema_version": "1.0",
        "checkpoint": "baseline-0034",
        "contract_id": contract.get("contract_id"),
        "status": "pass" if not errors else "fail",
        "phase": phase,
        "valid": not errors,
        "errors": errors,
        "development_equivalence": development,
        "benchmark": benchmark_result,
        "boundaries": {
            "default_configuration": runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION,
            "candidate_implemented": CANDIDATE_CONFIGURATION
            in runtime_retrieval.RETRIEVAL_CONFIGURATIONS,
            "benchmark_result_present": BENCHMARK_RESULT_PATH.is_file(),
            "comparison_result_present": COMPARISON_RESULT_PATH.is_file(),
            "held_out_used_for_optimization": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-phase",
        choices=(
            "frozen_preimplementation",
            "implementation_sealed_no_result",
            "evaluated_unselected",
            "selected",
        ),
    )
    parser.add_argument("--run-benchmark", action="store_true")
    args = parser.parse_args()
    result = validate(require_phase=args.require_phase, benchmark=args.run_benchmark)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
