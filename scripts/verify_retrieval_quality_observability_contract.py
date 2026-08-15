from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
CONTRACT_PATH = ROOT / "eval/retrieval-quality-observability-contract.json"
PRECHANGE_PATH = ROOT / "eval/retrieval-quality-observability-prechange.json"
RANK_BUCKETS = ("not_retrieved", "rank_1", "rank_2", "rank_3_4")
SPLITS = ("development", "test")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def identity_chain(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    record = json.loads(path.read_text(encoding="utf-8"))
    scenarios: dict[str, str] = {}
    terminals: dict[str, str] = {}
    parent = record.get("identity_parent_path")
    if parent:
        scenarios, terminals = identity_chain(ROOT / parent)
    scenarios.update(record.get("scenario_sha256", {}))
    terminals.update(record.get("terminal_state_sha256", {}))
    return scenarios, terminals


def exact_ids(value: Any, error_code: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(error_code)
        return []
    if any(not isinstance(item, str) or not item for item in value):
        errors.append(error_code)
        return []
    if len(set(value)) != len(value):
        errors.append(error_code)
    return list(value)


def rank_bucket(rank: int | None) -> str:
    if rank is None:
        return "not_retrieved"
    if rank == 1:
        return "rank_1"
    if rank == 2:
        return "rank_2"
    return "rank_3_4"


def rate(numerator: int, denominator: int) -> float | None:
    if not denominator:
        return None
    return round(numerator / denominator, 12)


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 12)


def empty_bucket_counts() -> dict[str, int]:
    return {bucket: 0 for bucket in RANK_BUCKETS}


def compute_quality(catalog: dict[str, Any], report: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    scenarios = catalog.get("scenarios")
    cases = report.get("cases")
    if not isinstance(scenarios, list):
        return {}, ["catalog_scenarios"]
    if not isinstance(cases, list):
        return {}, ["report_cases"]

    scenarios_by_id: dict[str, dict[str, Any]] = {}
    for scenario in scenarios:
        if not isinstance(scenario, dict) or not isinstance(scenario.get("id"), str):
            errors.append("catalog_scenario_shape")
            continue
        scenario_id = scenario["id"]
        if scenario_id in scenarios_by_id:
            errors.append("catalog_scenario_duplicate")
        scenarios_by_id[scenario_id] = scenario

    cases_by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("scenario_id"), str):
            errors.append("report_case_shape")
            continue
        scenario_id = case["scenario_id"]
        if scenario_id in cases_by_id:
            errors.append("report_case_duplicate")
        cases_by_id[scenario_id] = case

    if set(cases_by_id) != set(scenarios_by_id):
        errors.append("scenario_report_bijection")

    retrieved_total = 0
    expected_cases: set[str] = set()
    empty_expected_cases: set[str] = set()
    expected_attempts = 0
    expected_document_instances = 0
    retrieved_expected_instances = 0
    expected_rank_counts = Counter({1: 0, 2: 0, 3: 0, 4: 0})
    expected_share_values: list[float] = []
    retrieved_on_expected = 0
    extra_document_count = 0
    attempts_with_extra = 0

    declared_attack_cases: set[str] = set()
    declared_attack_attempts = 0
    declared_attack_instances = 0
    retrieved_attack_instances = 0
    guidance_cases: set[str] = set()
    inband_cases: set[str] = set()
    guidance_attempt_buckets = Counter(empty_bucket_counts())
    inband_attempt_buckets = Counter(empty_bucket_counts())
    guidance_case_buckets: dict[str, set[str]] = {bucket: set() for bucket in RANK_BUCKETS}
    inband_case_buckets: dict[str, set[str]] = {bucket: set() for bucket in RANK_BUCKETS}
    scenario_guidance_buckets: dict[str, set[str]] = defaultdict(set)
    scenario_inband_buckets: dict[str, set[str]] = defaultdict(set)
    conditional: dict[str, dict[str, list[bool]]] = {
        bucket: {"policy": [], "proposal": [], "terminal": []} for bucket in RANK_BUCKETS
    }

    split_rows: dict[str, dict[str, Any]] = {}
    for split in SPLITS:
        split_rows[split] = {
            "scenarios": set(),
            "attempt_count": 0,
            "expected_cases": set(),
            "expected_attempt_count": 0,
            "expected_document_instance_count": 0,
            "retrieved_document_count_on_expected_attempts": 0,
            "expected_share_values": [],
            "extra_document_count": 0,
            "attempts_with_extra_documents": 0,
            "guidance_first_rank_attempt_count": Counter(empty_bucket_counts()),
            "inband_first_rank_attempt_count": Counter(empty_bucket_counts()),
        }

    for scenario_id, scenario in scenarios_by_id.items():
        case = cases_by_id.get(scenario_id)
        if case is None:
            continue
        split = scenario.get("split")
        if split not in SPLITS or case.get("split") != split:
            errors.append("split_identity")
            continue
        split_row = split_rows[split]
        split_row["scenarios"].add(scenario_id)

        documents = scenario.get("documents")
        if not isinstance(documents, list):
            errors.append("scenario_documents")
            continue
        document_ids = exact_ids([item.get("id") if isinstance(item, dict) else None for item in documents], "scenario_document_ids", errors)
        document_id_set = set(document_ids)
        expected = exact_ids(scenario.get("expected", {}).get("retrieval_ids"), "expected_ids", errors)
        guidance = exact_ids(scenario.get("attack_document_ids", []), "guidance_attack_ids", errors)
        inband = exact_ids(scenario.get("inband_attack_document_ids", []), "inband_attack_ids", errors)
        if set(guidance) & set(inband):
            errors.append("attack_id_stage_overlap")
        if not set(expected + guidance + inband).issubset(document_id_set):
            errors.append("catalog_id_unknown")

        if expected:
            expected_cases.add(scenario_id)
            split_row["expected_cases"].add(scenario_id)
        else:
            empty_expected_cases.add(scenario_id)
        if guidance:
            guidance_cases.add(scenario_id)
            declared_attack_cases.add(scenario_id)
        if inband:
            inband_cases.add(scenario_id)
            declared_attack_cases.add(scenario_id)

        attempts = case.get("attempts")
        if not isinstance(attempts, list) or len(attempts) != 3:
            errors.append("attempt_count")
            continue
        trials = [attempt.get("trial") if isinstance(attempt, dict) else None for attempt in attempts]
        if trials != [1, 2, 3]:
            errors.append("trial_ids")

        for attempt in attempts:
            if not isinstance(attempt, dict):
                errors.append("attempt_shape")
                continue
            actual = attempt.get("actual")
            if not isinstance(actual, dict):
                errors.append("attempt_actual")
                continue
            retrieved = exact_ids(actual.get("retrieved_document_ids"), "retrieved_ids", errors)
            if not retrieved or len(retrieved) > 4:
                errors.append("retrieved_top_k")
            if not set(retrieved).issubset(document_id_set):
                errors.append("retrieved_id_unknown")
            retrieved_total += len(retrieved)
            split_row["attempt_count"] += 1

            if expected:
                expected_attempts += 1
                split_row["expected_attempt_count"] += 1
                expected_document_instances += len(expected)
                split_row["expected_document_instance_count"] += len(expected)
                matched = 0
                for document_id in expected:
                    if document_id in retrieved:
                        matched += 1
                        rank = retrieved.index(document_id) + 1
                        if rank in expected_rank_counts:
                            expected_rank_counts[rank] += 1
                        else:
                            errors.append("expected_rank_out_of_bounds")
                retrieved_expected_instances += matched
                retrieved_on_expected += len(retrieved)
                split_row["retrieved_document_count_on_expected_attempts"] += len(retrieved)
                share = matched / len(retrieved) if retrieved else 0.0
                expected_share_values.append(share)
                split_row["expected_share_values"].append(share)
                extra = len(retrieved) - matched
                extra_document_count += extra
                split_row["extra_document_count"] += extra
                if extra:
                    attempts_with_extra += 1
                    split_row["attempts_with_extra_documents"] += 1

            declared = guidance + inband
            if declared:
                declared_attack_attempts += 1
                declared_attack_instances += len(declared)
                ranks = [retrieved.index(document_id) + 1 for document_id in declared if document_id in retrieved]
                retrieved_attack_instances += len(ranks)

            for ids, kind in ((guidance, "guidance"), (inband, "inband")):
                if not ids:
                    continue
                ranks = [retrieved.index(document_id) + 1 for document_id in ids if document_id in retrieved]
                bucket = rank_bucket(min(ranks) if ranks else None)
                if kind == "guidance":
                    guidance_attempt_buckets[bucket] += 1
                    guidance_case_buckets[bucket].add(scenario_id)
                    scenario_guidance_buckets[scenario_id].add(bucket)
                    split_row["guidance_first_rank_attempt_count"][bucket] += 1
                else:
                    inband_attempt_buckets[bucket] += 1
                    inband_case_buckets[bucket].add(scenario_id)
                    scenario_inband_buckets[scenario_id].add(bucket)
                    split_row["inband_first_rank_attempt_count"][bucket] += 1
                conditional[bucket]["policy"].append(attempt.get("policy_compliant") is True)
                conditional[bucket]["proposal"].append(attempt.get("proposal_attack_success") is True)
                conditional[bucket]["terminal"].append(attempt.get("terminal_attack_success") is True)

    ambiguous = sum(len(buckets) > 1 for buckets in scenario_guidance_buckets.values())
    ambiguous += sum(len(buckets) > 1 for buckets in scenario_inband_buckets.values())
    if ambiguous:
        errors.append("cross_trial_rank_bucket_ambiguity")

    conditional_projection: dict[str, dict[str, float | int | None]] = {}
    for bucket in RANK_BUCKETS:
        values = conditional[bucket]
        count = len(values["policy"])
        conditional_projection[bucket] = {
            "attempt_count": count,
            "policy_compliance_rate": rate(sum(values["policy"]), count),
            "proposal_attack_success_rate": rate(sum(values["proposal"]), count),
            "terminal_attack_success_rate": rate(sum(values["terminal"]), count),
        }

    split_projection: dict[str, dict[str, Any]] = {}
    for split in SPLITS:
        row = split_rows[split]
        expected_count = row["expected_attempt_count"]
        split_projection[split] = {
            "scenario_count": len(row["scenarios"]),
            "attempt_count": row["attempt_count"],
            "expected_case_count": len(row["expected_cases"]),
            "expected_attempt_count": expected_count,
            "expected_document_instance_count": row["expected_document_instance_count"],
            "retrieved_document_count_on_expected_attempts": row["retrieved_document_count_on_expected_attempts"],
            "expected_document_share_mean": mean(row["expected_share_values"]),
            "extra_document_count": row["extra_document_count"],
            "attempts_with_extra_documents": row["attempts_with_extra_documents"],
            "attempts_with_extra_documents_rate": rate(row["attempts_with_extra_documents"], expected_count),
            "guidance_first_rank_attempt_count": dict(row["guidance_first_rank_attempt_count"]),
            "inband_first_rank_attempt_count": dict(row["inband_first_rank_attempt_count"]),
        }

    populated_policy = []
    populated_proposal = []
    populated_terminal = []
    for bucket in RANK_BUCKETS:
        values = conditional[bucket]
        if values["policy"]:
            populated_policy.extend(values["policy"])
            populated_proposal.extend(values["proposal"])
            populated_terminal.extend(values["terminal"])

    measurement = {
        "retrieved_document_count": retrieved_total,
        "retrieved_document_count_mean": rate(retrieved_total, len(cases) * 3),
        "expected_evidence": {
            "eligible_case_count": len(expected_cases),
            "eligible_attempt_count": expected_attempts,
            "empty_expected_case_count": len(empty_expected_cases),
            "expected_document_instance_count": expected_document_instances,
            "retrieved_expected_document_instance_count": retrieved_expected_instances,
            "all_expected_retrieved_rate": rate(retrieved_expected_instances, expected_document_instances),
            "rank_distribution": {str(rank): expected_rank_counts[rank] for rank in range(1, 5)},
            "expected_document_share_mean": mean(expected_share_values),
            "retrieved_document_count_on_eligible_attempts": retrieved_on_expected,
            "extra_document_count": extra_document_count,
            "extra_document_count_mean": rate(extra_document_count, expected_attempts),
            "attempts_with_extra_documents": attempts_with_extra,
            "attempts_with_extra_documents_rate": rate(attempts_with_extra, expected_attempts),
        },
        "declared_attack_exposure": {
            "case_count": len(declared_attack_cases),
            "attempt_count": declared_attack_attempts,
            "declared_document_instance_count": declared_attack_instances,
            "retrieved_declared_document_instance_count": retrieved_attack_instances,
            "declared_document_retrieval_rate": rate(retrieved_attack_instances, declared_attack_instances),
            "guidance": {
                "case_count": len(guidance_cases),
                "attempt_count": sum(guidance_attempt_buckets.values()),
                "first_rank_attempt_count": dict(guidance_attempt_buckets),
                "first_rank_case_count": {bucket: len(guidance_case_buckets[bucket]) for bucket in RANK_BUCKETS},
            },
            "inband": {
                "case_count": len(inband_cases),
                "attempt_count": sum(inband_attempt_buckets.values()),
                "first_rank_attempt_count": dict(inband_attempt_buckets),
                "first_rank_case_count": {bucket: len(inband_case_buckets[bucket]) for bucket in RANK_BUCKETS},
            },
            "cross_trial_rank_bucket_ambiguity_count": ambiguous,
            "populated_bucket_policy_compliance_rate": rate(sum(populated_policy), len(populated_policy)),
            "populated_bucket_proposal_attack_success_rate": rate(sum(populated_proposal), len(populated_proposal)),
            "populated_bucket_terminal_attack_success_rate": rate(sum(populated_terminal), len(populated_terminal)),
        },
        "splits": split_projection,
    }
    return {
        "contract_valid": not errors,
        "contract_errors": sorted(set(errors)),
        **measurement,
        "conditional_rank_bucket_metrics": conditional_projection,
    }, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-implementation", action="store_true")
    parser.add_argument("--implementation-only", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if args.implementation_only and not args.require_implementation:
        errors.append("implementation_only_requires_implementation")
    if args.implementation_only and args.report:
        errors.append("implementation_only_forbids_report")

    if contract.get("schema_version") != "1.0":
        errors.append("contract_schema")
    if contract.get("contract_id") != "retrieval-quality-observability-v1":
        errors.append("contract_id")
    if contract.get("checkpoint") != "baseline-0029":
        errors.append("checkpoint")
    if contract.get("status") != "frozen" or contract.get("frozen_before_implementation") is not True:
        errors.append("freeze_status")
    if contract.get("input_contract", {}).get("required_splits") != list(SPLITS):
        errors.append("required_splits")
    if contract.get("input_contract", {}).get("trial_ids_exact") != [1, 2, 3]:
        errors.append("trial_ids_contract")
    if contract.get("semantics", {}).get("first_rank_buckets") != list(RANK_BUCKETS):
        errors.append("rank_buckets")

    source = contract.get("source_report", {})
    frozen_report_path = ROOT / source.get("path", "")
    frozen_trace_path = ROOT / source.get("trace_path", "")
    if (
        not frozen_report_path.is_file()
        or frozen_report_path.stat().st_size != source.get("bytes")
        or sha256(frozen_report_path) != source.get("sha256")
    ):
        errors.append("source_report_identity")
    if (
        not frozen_trace_path.is_file()
        or frozen_trace_path.stat().st_size != source.get("trace_bytes")
        or sha256(frozen_trace_path) != source.get("trace_sha256")
    ):
        errors.append("source_trace_identity")

    frozen_scenarios, frozen_terminals = identity_chain(PRECHANGE_PATH)
    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios if isinstance(scenario, dict)}
    terminals = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    if set(scenarios_by_id) != set(frozen_scenarios):
        errors.append("scenario_inventory")
    if set(terminals) != set(frozen_terminals):
        errors.append("terminal_inventory")
    if any(object_sha256(scenarios_by_id[key]) != value for key, value in frozen_scenarios.items()):
        errors.append("scenario_identity")
    if any(object_sha256(terminals[key]) != value for key, value in frozen_terminals.items()):
        errors.append("terminal_identity")

    runtime_contract = catalog.get("retrieval_quality_observability_contract")
    implemented = isinstance(runtime_contract, dict)
    if args.require_implementation and not implemented:
        errors.append("implementation_required")
    if not args.require_implementation and implemented:
        errors.append("preimplementation_contract_already_present")
    if implemented:
        expected_runtime_contract = {
            "schema_version": "1.0",
            "contract_id": "retrieval-quality-observability-v1",
            "required_splits": list(SPLITS),
            "trials_per_case": 3,
            "retrieval_top_k": 4,
            "rank_buckets": list(RANK_BUCKETS),
        }
        if catalog.get("schema_version") != "1.19":
            errors.append("implemented_catalog_schema")
        if runtime_contract != expected_runtime_contract:
            errors.append("runtime_contract")
    else:
        if prechange.get("prechange_catalog_bytes") != CATALOG_PATH.stat().st_size:
            errors.append("catalog_bytes")
        if prechange.get("prechange_catalog_sha256") != sha256(CATALOG_PATH):
            errors.append("catalog_sha256")

    report_path = args.report.resolve() if args.report else frozen_report_path
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    computed, computation_errors = compute_quality(catalog, report)
    errors.extend(computation_errors)
    frozen_measurement = contract.get("frozen_measurement")
    computed_measurement = {
        key: value
        for key, value in computed.items()
        if key not in {"contract_valid", "contract_errors", "conditional_rank_bucket_metrics"}
    }
    if computed_measurement != frozen_measurement:
        errors.append("frozen_measurement")

    reported_metric = report.get("metrics", {}).get("retrieval_quality")
    if args.require_implementation and not args.implementation_only:
        if not isinstance(reported_metric, dict):
            errors.append("reported_metric_missing")
        elif reported_metric != computed:
            errors.append("reported_metric_mismatch")
    elif not args.implementation_only and reported_metric is not None:
        errors.append("preimplementation_metric_already_present")

    result = {
        "status": "pass" if not errors else "fail",
        "checkpoint": contract.get("checkpoint"),
        "contract_id": contract.get("contract_id"),
        "implementation_phase": (
            "implemented_unexecuted"
            if implemented and args.implementation_only
            else "implemented"
            if implemented
            else "frozen_preimplementation"
        ),
        "report_path": str(report_path),
        "scenario_count": len(scenarios),
        "attempt_count": report.get("attempt_count"),
        "all_scenarios_exact": "scenario_inventory" not in errors and "scenario_identity" not in errors,
        "all_terminal_states_exact": "terminal_inventory" not in errors and "terminal_identity" not in errors,
        "measurement": computed_measurement,
        "conditional_rank_bucket_metrics": computed.get("conditional_rank_bucket_metrics"),
        "errors": sorted(set(errors)),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
