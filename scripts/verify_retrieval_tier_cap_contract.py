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
from runbook_sentinel.evidence import (  # noqa: E402
    PROJECT_EVIDENCE_KINDS,
    is_fresh_project_evidence,
)


CONTRACT_PATH = ROOT / "eval/retrieval-tier-cap-contract.json"
CANDIDATE_CONFIGURATION = "bounded-trust-tier-lexical-v4"
CONTROL_CONFIGURATION = "freshness-priority-lexical-v3"
EXPECTED_METRICS = [
    "retrieval_completeness",
    "retrieval_focus",
    "attack_document_rank",
    "generation",
    "tool_trajectory",
    "policy_compliance",
    "terminal_state",
    "benign_utility",
    "proposal_attack_success",
    "terminal_attack_success",
    "repeated_trial_reliability",
    "latency",
    "cost",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _score(query: str, document: dict[str, Any]) -> float:
    query_tokens = runtime_retrieval._tokens(query)
    document_tokens = runtime_retrieval._tokens(
        document.get("content", "")
    ) | runtime_retrieval._tokens(document.get("title", ""))
    overlap = len(query_tokens & document_tokens)
    coverage = overlap / max(1, len(query_tokens))
    return coverage + (0.05 if document.get("kind") == "telemetry" else 0.0)


def reference_candidate(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = [
        (_score(scenario["prompt"], document), document["id"], document)
        for document in scenario["documents"]
    ]
    ranked = [item for item in ranked if item[0] > 0]
    ranked.sort(key=lambda item: (-item[0], item[1]))
    fresh: list[tuple[float, str, dict[str, Any]]] = []
    stale: list[tuple[float, str, dict[str, Any]]] = []
    guidance: list[tuple[float, str, dict[str, Any]]] = []
    for item in ranked:
        document = item[2]
        if document.get("kind") not in PROJECT_EVIDENCE_KINDS:
            guidance.append(item)
        elif is_fresh_project_evidence(document, scenario["as_of"]):
            fresh.append(item)
        else:
            stale.append(item)
    selected = fresh[:2] + stale[:1] + guidance[:1]
    return [document for _, _, document in selected]


def summarize(
    scenarios: list[dict[str, Any]],
    retrieve: Any,
) -> dict[str, Any]:
    shares: list[float] = []
    extra_document_count = 0
    attempts_with_extra = 0
    complete = 0
    expected_instances = 0
    rank_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    retrieved_count_distribution = {1: 0, 2: 0, 3: 0, 4: 0}
    eligible = 0
    for scenario in scenarios:
        documents = retrieve(scenario)
        retrieved_ids = [document["id"] for document in documents]
        retrieved_count_distribution[len(retrieved_ids)] += 1
        expected = set(scenario["expected"]["retrieval_ids"])
        if not expected:
            continue
        eligible += 1
        expected_instances += len(expected)
        selected = set(retrieved_ids)
        complete += expected <= selected
        extras = selected - expected
        extra_document_count += len(extras)
        attempts_with_extra += bool(extras)
        shares.append(len(expected & selected) / len(retrieved_ids))
        for document_id in expected:
            if document_id in retrieved_ids:
                rank_counts[retrieved_ids.index(document_id) + 1] += 1
    trials = 3
    return {
        "eligible_case_count": eligible,
        "eligible_attempt_count": eligible * trials,
        "expected_document_instance_count_per_trial_set": expected_instances,
        "all_expected_retrieved_rate": complete / max(1, eligible),
        "expected_document_share_mean": sum(shares) / max(1, len(shares)),
        "extra_document_count_per_trial_set": extra_document_count,
        "extra_document_count": extra_document_count * trials,
        "attempts_with_extra_documents": attempts_with_extra * trials,
        "expected_rank_1_count": rank_counts[1] * trials,
        "expected_rank_2_count": rank_counts[2] * trials,
        "retrieved_document_count_distribution": {
            str(key): value * trials
            for key, value in retrieved_count_distribution.items()
        },
    }


def _expect_identity(record: dict[str, Any], errors: list[str], prefix: str) -> None:
    path = ROOT / record.get(f"{prefix}_path", "")
    if not path.is_file() or sha256(path) != record.get(f"{prefix}_sha256"):
        errors.append(f"{prefix}_identity")


def validate(
    require_implementation: bool = False,
    require_selection: bool = False,
) -> dict[str, Any]:
    frozen = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if frozen.get("schema_version") != "1.0":
        errors.append("schema_version")
    if frozen.get("checkpoint") != "baseline-0031":
        errors.append("checkpoint")
    if frozen.get("contract_id") != "bounded-trust-tier-retrieval-v1":
        errors.append("contract_id")
    if frozen.get("status") != "frozen" or frozen.get("frozen_before_implementation") is not True:
        errors.append("freeze_status")

    public = frozen.get("starting_public_checkpoint", {})
    receipt = ROOT / public.get("public_receipt_path", "")
    if (
        not receipt.is_file()
        or receipt.stat().st_size != public.get("public_receipt_bytes")
        or sha256(receipt) != public.get("public_receipt_sha256")
    ):
        errors.append("public_receipt_identity")
    if public.get("main_commit") != "4d62ecf930130b938594a9b7bc70675f9d8122e1":
        errors.append("starting_main_identity")

    control = frozen.get("accepted_control", {})
    report_path = ROOT / control.get("evaluation_path", "")
    if (
        not report_path.is_file()
        or report_path.stat().st_size != control.get("evaluation_bytes")
        or sha256(report_path) != control.get("evaluation_sha256")
    ):
        errors.append("control_evaluation_identity")
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        quality = report.get("metrics", {}).get("retrieval_quality", {}).get(
            "expected_evidence", {}
        )
        observations = {
            "configuration": report.get("retrieval_configuration"),
            "manifest_sha256": report.get("manifest_sha256"),
            "scenario_count": report.get("scenario_count"),
            "attempt_count": report.get("attempt_count"),
            "all_expected_retrieved_rate": quality.get("all_expected_retrieved_rate"),
            "expected_document_share_mean": quality.get("expected_document_share_mean"),
            "extra_document_count": quality.get("extra_document_count"),
            "attempts_with_extra_documents": quality.get("attempts_with_extra_documents"),
            "attempts_with_extra_documents_rate": quality.get(
                "attempts_with_extra_documents_rate"
            ),
            "policy_compliance": report.get("metrics", {})
            .get("policy", {})
            .get("compliance_rate"),
            "proposal_attack_success": report.get("metrics", {})
            .get("security", {})
            .get("proposal_attack_success_rate"),
            "terminal_attack_success": report.get("metrics", {})
            .get("security", {})
            .get("terminal_attack_success_rate"),
        }
        for field, actual in observations.items():
            if control.get(field) != actual:
                errors.append(f"control_{field}")

    boundaries = frozen.get("frozen_static_boundaries", {})
    for prefix in ("service", "agent", "policy"):
        _expect_identity(boundaries, errors, prefix)
    catalog_path = ROOT / boundaries.get("catalog_path", "")
    if (
        not catalog_path.is_file()
        or catalog_path.stat().st_size != boundaries.get("catalog_bytes")
        or sha256(catalog_path) != boundaries.get("catalog_sha256")
    ):
        errors.append("catalog_identity")
        scenarios: list[dict[str, Any]] = []
    else:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        scenarios = catalog.get("scenarios", [])
        if len(scenarios) != boundaries.get("scenario_count"):
            errors.append("scenario_count")
        if sum(item.get("split") == "development" for item in scenarios) != boundaries.get(
            "development_count"
        ):
            errors.append("development_count")
        if sum(item.get("split") == "test" for item in scenarios) != boundaries.get(
            "held_out_count"
        ):
            errors.append("held_out_count")

    basis = frozen.get("research_basis", {})
    gate_path = ROOT / basis.get("source_gate_path", "")
    if (
        not gate_path.is_file()
        or gate_path.stat().st_size != basis.get("source_gate_bytes")
        or sha256(gate_path) != basis.get("source_gate_sha256")
    ):
        errors.append("source_gate_identity")
    else:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        if gate.get("decision", {}).get("status") != "ready":
            errors.append("source_gate_not_ready")

    candidate = frozen.get("frozen_candidate", {})
    if candidate.get("configuration") != CANDIDATE_CONFIGURATION:
        errors.append("candidate_configuration")
    if candidate.get("tier_caps") != {
        "fresh_project_evidence": 2,
        "stale_project_evidence": 1,
        "untrusted_guidance": 1,
    }:
        errors.append("tier_caps")
    if candidate.get("quota_backfill") is not False:
        errors.append("quota_backfill")
    if candidate.get("maximum_total_documents") != 4:
        errors.append("maximum_total_documents")
    for field in (
        "decision_context_projection_changed",
        "default_configuration_changed_before_selection",
        "agent_model_prompt_parser_changed",
        "scenario_expected_terminal_or_split_changed",
        "policy_approval_executor_or_authority_changed",
        "tools_credentials_secrets_dependencies_or_services_added",
        "external_asset_or_real_infrastructure_added",
    ):
        if candidate.get(field) is not False:
            errors.append(field)

    development = [item for item in scenarios if item.get("split") == "development"]
    if scenarios:
        control_retriever = runtime_retrieval.LexicalRetriever(CONTROL_CONFIGURATION)
        control_summary = summarize(
            development,
            lambda scenario: control_retriever.retrieve(
                scenario["prompt"], scenario["documents"], 4, scenario["as_of"]
            ),
        )
        candidate_summary = summarize(development, reference_candidate)
        preflight = frozen.get("development_only_preflight", {})
        expected_control = dict(preflight.get("control", {}))
        expected_candidate = dict(preflight.get("reference_candidate", {}))
        common = {
            "eligible_case_count": preflight.get("eligible_case_count"),
            "eligible_attempt_count": preflight.get("eligible_attempt_count"),
            "expected_document_instance_count_per_trial_set": preflight.get(
                "expected_document_instance_count_per_trial_set"
            ),
        }
        for key, value in common.items():
            expected_control[key] = value
            expected_candidate[key] = value
        expected_control.pop("retrieved_document_count_distribution", None)
        for key, value in expected_control.items():
            if control_summary.get(key) != value:
                errors.append(f"development_control_{key}")
        for key, value in expected_candidate.items():
            if candidate_summary.get(key) != value:
                errors.append(f"development_candidate_{key}")
        if preflight.get("held_out_results_inspected_or_used") is not False:
            errors.append("held_out_preflight_boundary")

    comparison = frozen.get("comparison_contract", {})
    if comparison.get("control_configuration") != CONTROL_CONFIGURATION:
        errors.append("comparison_control")
    if comparison.get("candidate_configuration") != CANDIDATE_CONFIGURATION:
        errors.append("comparison_candidate")
    if comparison.get("required_separate_metrics") != EXPECTED_METRICS:
        errors.append("comparison_metrics")
    if comparison.get("held_out_split_used_for_optimization") is not False:
        errors.append("held_out_optimization_boundary")
    if comparison.get("no_default_change_before_complete_comparison") is not True:
        errors.append("default_selection_boundary")

    implemented = CANDIDATE_CONFIGURATION in runtime_retrieval.RETRIEVAL_CONFIGURATIONS
    selected = runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION == CANDIDATE_CONFIGURATION
    retrieval_path = ROOT / boundaries.get("retrieval_path", "")
    if not implemented:
        phase = "frozen_preimplementation"
        if (
            not retrieval_path.is_file()
            or retrieval_path.stat().st_size != boundaries.get("retrieval_bytes")
            or sha256(retrieval_path) != boundaries.get("retrieval_sha256")
        ):
            errors.append("preimplementation_retrieval_identity")
        if frozen.get("implementation_result") is not None:
            errors.append("implementation_result_present")
    else:
        phase = "selected" if selected else "implemented_experimental"
        runtime_candidate = runtime_retrieval.LexicalRetriever(CANDIDATE_CONFIGURATION)
        for scenario in development:
            expected_ids = [item["id"] for item in reference_candidate(scenario)]
            actual_ids = [
                item["id"]
                for item in runtime_candidate.retrieve(
                    scenario["prompt"], scenario["documents"], 4, scenario["as_of"]
                )
            ]
            if actual_ids != expected_ids:
                errors.append("runtime_candidate_development_projection")
                break
        result = frozen.get("implementation_result")
        if not isinstance(result, dict):
            errors.append("implementation_result_missing")
        elif sha256(retrieval_path) != result.get("retrieval_sha256"):
            errors.append("implementation_result_identity")
        if not selected and runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION != CONTROL_CONFIGURATION:
            errors.append("default_changed_before_selection")

    if require_selection and not selected:
        errors.append("selection_required")
    if require_implementation and not implemented:
        errors.append("implementation_required")
    if not require_implementation and not require_selection and implemented:
        errors.append("implementation_present_before_public_freeze")

    return {
        "status": "pass" if not errors else "fail",
        "checkpoint": frozen.get("checkpoint"),
        "contract_id": frozen.get("contract_id"),
        "implementation_phase": phase,
        "control_configuration": CONTROL_CONFIGURATION,
        "candidate_configuration": CANDIDATE_CONFIGURATION,
        "candidate_implemented": implemented,
        "candidate_selected": selected,
        "development_control": control_summary if scenarios else None,
        "development_reference_candidate": candidate_summary if scenarios else None,
        "source_gate_ready": bool(gate_path.is_file()) and "source_gate_not_ready" not in errors,
        "errors": sorted(set(errors)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-implementation", action="store_true")
    parser.add_argument("--require-selection", action="store_true")
    args = parser.parse_args()
    result = validate(
        require_implementation=args.require_implementation,
        require_selection=args.require_selection,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
