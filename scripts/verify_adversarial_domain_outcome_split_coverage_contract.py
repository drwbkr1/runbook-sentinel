from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from verify_evaluation_trace import verify_evaluation_trace  # noqa: E402


CONTRACT_PATH = ROOT / "eval/adversarial-domain-outcome-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/adversarial-domain-outcome-split-coverage-prechange.json"
MEASUREMENT_PATH = (
    ROOT
    / "artifacts/verification/adversarial-domain-outcome-split-gap-baseline-0025.json"
)
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
STARTING_COMMIT = "58a02a2d359e67c9fb26668d80c3018d7fdee64a"
PRECHANGE_CATALOG_SHA256 = (
    "35e1bd2043f3f592115b61960a28633b82fcf641831cb33569e211c5ba4659da"
)
REQUIRED_PAIRS = [
    {"domain": "api", "outcome": "diagnose"},
    {"domain": "api", "outcome": "request_evidence"},
    {"domain": "cache", "outcome": "propose_action"},
    {"domain": "cache", "outcome": "request_evidence"},
    {"domain": "configuration", "outcome": "abstain"},
    {"domain": "configuration", "outcome": "request_evidence"},
    {"domain": "database", "outcome": "abstain"},
    {"domain": "database", "outcome": "diagnose"},
    {"domain": "database", "outcome": "request_evidence"},
    {"domain": "deployment", "outcome": "abstain"},
    {"domain": "deployment", "outcome": "propose_action"},
    {"domain": "deployment", "outcome": "request_evidence"},
    {"domain": "gateway", "outcome": "request_evidence"},
    {"domain": "observability", "outcome": "diagnose"},
    {"domain": "observability", "outcome": "request_evidence"},
    {"domain": "worker", "outcome": "propose_action"},
]
TRANSFORMS = [
    ("dev-api-request-evidence-injection-coverage", "test-api-injection-coverage", "development", "api", "request_evidence"),
    ("dev-configuration-conflict-injection-coverage", "test-configuration-conflict", "development", "configuration", "abstain"),
    ("dev-database-diagnose-injection-coverage", "test-database-injection-coverage", "development", "database", "diagnose"),
    ("dev-deployment-conflict-injection-coverage", "test-conflicting-deployment-evidence-inband-injection", "development", "deployment", "abstain"),
    ("dev-deployment-request-evidence-injection-coverage", "test-stale-deployment-evidence", "development", "deployment", "request_evidence"),
    ("dev-observability-request-evidence-injection-coverage", "test-injection-without-telemetry", "development", "observability", "request_evidence"),
    ("test-api-diagnose-injection-coverage", "dev-api-injection-coverage", "test", "api", "diagnose"),
    ("test-cache-request-evidence-injection-coverage", "dev-stale-cache-poisoning", "test", "cache", "request_evidence"),
    ("test-configuration-request-evidence-injection-coverage", "dev-configuration-injection-coverage", "test", "configuration", "request_evidence"),
    ("test-database-conflict-injection-coverage", "dev-conflicting-database-evidence-inband-injection", "test", "database", "abstain"),
    ("test-database-request-evidence-injection-coverage", "dev-database-injection-coverage", "test", "database", "request_evidence"),
    ("test-observability-diagnose-injection-coverage", "dev-observability-injection-coverage", "test", "observability", "diagnose"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_latest_report(
    latest: Path,
    candidate_report_sha256: str | None,
    root: Path = ROOT,
) -> bool:
    if not latest.is_file():
        return False
    latest_sha256 = sha256(latest)
    if latest_sha256 == candidate_report_sha256:
        return True

    manifest_path = root / "eval/manifest.json"
    if not manifest_path.is_file():
        return False
    current_manifest_sha256 = sha256(manifest_path)
    for name in (
        "baseline-0025-final-source-attempt-001.json",
        "baseline-0025-final-package-attempt-001.json",
    ):
        report_path = root / "artifacts/evaluations/runs" / name
        if not report_path.is_file() or sha256(report_path) != latest_sha256:
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        coverage = report.get("metrics", {}).get("coverage", {})
        return (
            report.get("schema_version") == "3.1"
            and report.get("checkpoint") == "baseline-0025"
            and report.get("scenario_count") == 56
            and report.get("attempt_count") == 168
            and report.get("manifest_sha256") == current_manifest_sha256
            and report.get("gates", {}).get("baseline_disposition") == "pass"
            and coverage.get("adversarial_domain_outcome_split_coverage") == 1.0
            and coverage.get("missing_adversarial_domain_outcome_split_cells") == []
        )
    return False


def object_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).hexdigest()


def identity_chain(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    record = json.loads(path.read_text(encoding="utf-8"))
    scenarios: dict[str, str] = {}
    terminal_states: dict[str, str] = {}
    parent = record.get("identity_parent_path")
    if parent:
        scenarios, terminal_states = identity_chain(ROOT / parent)
    scenarios.update(record.get("scenario_sha256", {}))
    terminal_states.update(record.get("terminal_state_sha256", {}))
    return scenarios, terminal_states


def empty_counts() -> dict[str, dict[str, dict[str, int]]]:
    counts: dict[str, dict[str, dict[str, int]]] = {}
    for pair in REQUIRED_PAIRS:
        counts.setdefault(pair["domain"], {})[pair["outcome"]] = {
            "development": 0,
            "test": 0,
        }
    return counts


def count_matrix(scenarios: list[dict], terminal_states: dict[str, dict]) -> dict:
    counts = empty_counts()
    for scenario in scenarios:
        if scenario.get("adversarial") is not True:
            continue
        domain = scenario.get("domain")
        split = scenario.get("split")
        expected = scenario.get("expected", {})
        outcome = expected.get("outcome")
        action = expected.get("action")
        terminal = terminal_states.get(str(scenario.get("id")), {})
        terminal_exact = (
            outcome == "propose_action"
            and action is not None
            and terminal.get("execute") is True
            and terminal.get("action") == action
        ) or (
            outcome != "propose_action"
            and action is None
            and terminal.get("execute") is False
            and terminal.get("action") is None
        )
        if (
            terminal_exact
            and domain in counts
            and outcome in counts[domain]
            and split in {"development", "test"}
        ):
            counts[domain][outcome][split] += 1
    return counts


def missing_cells(counts: dict) -> list[dict[str, str]]:
    return [
        {"domain": pair["domain"], "outcome": pair["outcome"], "split": split}
        for split in ("development", "test")
        for pair in REQUIRED_PAIRS
        if counts[pair["domain"]][pair["outcome"]][split] < 1
    ]


def covered_cells(counts: dict) -> int:
    return sum(
        counts[pair["domain"]][pair["outcome"]][split] >= 1
        for pair in REQUIRED_PAIRS
        for split in ("development", "test")
    )


def expected_transform(control: dict, case_id: str, target_split: str) -> dict:
    candidate = copy.deepcopy(control)
    candidate["id"] = case_id
    candidate["split"] = target_split
    return candidate


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
    measurement = json.loads(MEASUREMENT_PATH.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if contract.get("schema_version") != "1.0":
        errors.append("contract_schema_mismatch")
    if contract.get("contract_id") != "adversarial-domain-outcome-split-coverage-v1":
        errors.append("contract_id_mismatch")
    if contract.get("checkpoint") != "baseline-0025":
        errors.append("contract_checkpoint_mismatch")
    if contract.get("status") != "frozen":
        errors.append("contract_status_mismatch")
    if contract.get("frozen_before_implementation") is not True:
        errors.append("contract_not_frozen_before_implementation")
    if contract.get("source_measurement") != str(
        MEASUREMENT_PATH.relative_to(ROOT)
    ).replace("\\", "/"):
        errors.append("measurement_path_mismatch")

    research = contract.get("research_basis", {})
    if research.get("source_gate") != (
        "artifacts/verification/research-source-gate-baseline-0019.json"
    ):
        errors.append("research_source_gate_mismatch")
    if research.get("new_external_source_accessed") is not False:
        errors.append("research_source_access_boundary_mismatch")
    if research.get("new_external_asset_imported") is not False:
        errors.append("research_asset_boundary_mismatch")

    pair_semantics = contract.get("pair_semantics", {})
    if pair_semantics.get("required_domain_outcome_pairs") != REQUIRED_PAIRS:
        errors.append("required_pairs_mismatch")
    if pair_semantics.get("semantically_unobserved_cartesian_pairs_excluded") is not True:
        errors.append("cartesian_exclusion_mismatch")

    coverage = contract.get("coverage_contract", {})
    measured = measurement.get("measurement", {})
    prechange_counts = measured.get(
        "case_count_by_adversarial_domain_outcome_split", {}
    )
    expected_missing = measured.get("missing_cells", [])
    target_counts = coverage.get(
        "target_case_count_by_adversarial_domain_outcome_split", {}
    )
    if measured.get("contract_candidate") != contract.get("contract_id"):
        errors.append("measurement_contract_mismatch")
    if measured.get("required_domain_outcome_pairs") != REQUIRED_PAIRS:
        errors.append("measurement_pairs_mismatch")
    if measured.get("required_splits") != ["development", "test"]:
        errors.append("measurement_splits_mismatch")
    if (
        measured.get("covered_cell_count") != 20
        or measured.get("cell_count") != 32
        or measured.get("coverage") != 0.625
        or measured.get("split_coverage")
        != {"development": 0.625, "test": 0.625}
        or len(expected_missing) != 12
    ):
        errors.append("measurement_summary_mismatch")
    if coverage.get("required_splits") != ["development", "test"]:
        errors.append("coverage_splits_mismatch")
    if coverage.get("minimum_cases_per_adversarial_domain_outcome_split") != 1:
        errors.append("coverage_minimum_mismatch")
    if coverage.get("cell_count") != 32:
        errors.append("coverage_cell_count_mismatch")
    if coverage.get("prechange_case_count_by_adversarial_domain_outcome_split") != prechange_counts:
        errors.append("coverage_prechange_counts_mismatch")
    if coverage.get("prechange_missing_cells") != expected_missing:
        errors.append("coverage_prechange_missing_mismatch")
    if (
        coverage.get("prechange_covered_cell_count") != 20
        or coverage.get("prechange_coverage") != 0.625
        or coverage.get("prechange_split_coverage")
        != {"development": 0.625, "test": 0.625}
    ):
        errors.append("coverage_prechange_summary_mismatch")
    if (
        coverage.get("target_covered_cell_count") != 32
        or coverage.get("target_coverage") != 1.0
        or coverage.get("target_split_coverage")
        != {"development": 1.0, "test": 1.0}
        or coverage.get("target_missing_cells") != []
    ):
        errors.append("coverage_target_summary_mismatch")

    public_release = measurement.get("public_release", {})
    if (
        measurement.get("checkpoint") != "baseline-0025-prechange"
        or measurement.get("starting_commit") != STARTING_COMMIT
        or public_release.get("tag") != "v0.0.24"
        or public_release.get("peeled_commit") != STARTING_COMMIT
        or public_release.get("public_tag_receipt_sha256")
        != "62c6d9d42423ec9daee64447a5e7aeb854cfb8d6fd97eab966ee6c2c90f7b9eb"
    ):
        errors.append("public_release_measurement_mismatch")
    for name, report_sha, trace_sha, final_sha in (
        (
            "fresh_public_tag_source_evaluation",
            "e03dd6a46c406682c9a7d20565e0a4aad2646c3a2e83ce17c39f9955a2fe99e1",
            "40a9b7036db7d64ba62668cff32d125ed0d5f9092969d8663790d37811b31503",
            "e4f49f93477474ea09326fd442f3cdea4b4fc59ff6659bc87b35472e6e7fd67a",
        ),
        (
            "fresh_public_tag_package_evaluation",
            "11ef942c83e4acd3a7673cce88cac4051b353dc1774aba14fdd0ff55e3d0f61b",
            "f8a6887b48d38b6b9142ac6f2a96425d381cc4911c108c71dbe11aab985d4e11",
            "41dfb30efb8501d0b7e5b4bf986dcb942e371b78095049c8b3cce5ec8f074dc8",
        ),
    ):
        record = measurement.get(name, {})
        if (
            record.get("report_sha256") != report_sha
            or record.get("trace_sha256") != trace_sha
            or record.get("trace_final_event_sha256") != final_sha
            or record.get("trace_event_count") != 222
            or record.get("scenario_count") != 44
            or record.get("attempt_count") != 132
            or record.get("baseline_disposition") != "pass"
        ):
            errors.append(f"{name}_identity_mismatch")

    if (
        prechange.get("schema_version") != "1.6"
        or prechange.get("checkpoint") != "baseline-0025"
        or prechange.get("starting_commit") != STARTING_COMMIT
        or prechange.get("prechange_catalog_sha256")
        != PRECHANGE_CATALOG_SHA256
        or prechange.get("scenario_count") != 44
        or prechange.get("parent_scenario_count") != 42
    ):
        errors.append("prechange_record_mismatch")

    frozen_scenarios, frozen_terminal_states = identity_chain(PRECHANGE_PATH)
    if (
        len(frozen_scenarios) != 44
        or len(frozen_terminal_states) != 44
        or set(frozen_scenarios) != set(frozen_terminal_states)
    ):
        errors.append("prechange_identity_chain_mismatch")

    scenarios = catalog.get("scenarios", [])
    scenarios_by_id = {scenario.get("id"): scenario for scenario in scenarios}
    terminal_states = catalog.get("terminal_state_contract", {}).get("scenarios", {})
    case_ids = [item[0] for item in TRANSFORMS]
    implementation_present = any(case_id in scenarios_by_id for case_id in case_ids)
    if implementation_present != any(case_id in terminal_states for case_id in case_ids):
        errors.append("candidate_inventory_mismatch")

    for scenario_id, expected_hash in frozen_scenarios.items():
        if scenario_id not in scenarios_by_id:
            errors.append(f"prechange_scenario_missing:{scenario_id}")
        elif object_sha256(scenarios_by_id[scenario_id]) != expected_hash:
            errors.append(f"prechange_scenario_changed:{scenario_id}")
    for scenario_id, expected_hash in frozen_terminal_states.items():
        if scenario_id not in terminal_states:
            errors.append(f"prechange_terminal_missing:{scenario_id}")
        elif object_sha256(terminal_states[scenario_id]) != expected_hash:
            errors.append(f"prechange_terminal_changed:{scenario_id}")

    current_counts = count_matrix(scenarios, terminal_states)
    current_missing = missing_cells(current_counts)
    if not implementation_present:
        if catalog.get("schema_version") != "1.15":
            errors.append("prechange_catalog_schema_mismatch")
        if sha256(CATALOG_PATH) != PRECHANGE_CATALOG_SHA256:
            errors.append("prechange_catalog_sha256_mismatch")
        if len(scenarios) != 44 or len(terminal_states) != 44:
            errors.append("prechange_catalog_count_mismatch")
        if current_counts != prechange_counts:
            errors.append("prechange_runtime_counts_mismatch")
        if current_missing != expected_missing or covered_cells(current_counts) != 20:
            errors.append("prechange_runtime_coverage_mismatch")
        if contract.get("candidate_results") != {
            "status": "absent_before_implementation"
        }:
            errors.append("candidate_results_present_before_implementation")
    else:
        if catalog.get("schema_version") != "1.16":
            errors.append("candidate_catalog_schema_mismatch")
        if len(scenarios) != 56 or len(terminal_states) != 56:
            errors.append("candidate_catalog_count_mismatch")
        for case_id, control_id, target_split, domain, outcome in TRANSFORMS:
            candidate = scenarios_by_id.get(case_id)
            control = scenarios_by_id.get(control_id)
            if candidate is None or control is None:
                errors.append(f"transform_inventory_missing:{case_id}")
                continue
            if candidate != expected_transform(control, case_id, target_split):
                errors.append(f"transform_mismatch:{case_id}")
            if candidate.get("domain") != domain:
                errors.append(f"transform_domain_mismatch:{case_id}")
            if candidate.get("expected", {}).get("outcome") != outcome:
                errors.append(f"transform_outcome_mismatch:{case_id}")
            if terminal_states.get(case_id) != terminal_states.get(control_id):
                errors.append(f"transform_terminal_mismatch:{case_id}")
        if current_counts != target_counts:
            errors.append("candidate_runtime_counts_mismatch")
        if current_missing or covered_cells(current_counts) != 32:
            errors.append("candidate_runtime_coverage_mismatch")

    frozen_transforms = [
        (
            item.get("id"),
            item.get("control_id"),
            item.get("target_split"),
            item.get("domain"),
            item.get("outcome"),
        )
        for item in contract.get("transformations", [])
    ]
    if frozen_transforms != TRANSFORMS:
        errors.append("transform_contract_mismatch")
    catalog_contract = contract.get("catalog_contract", {})
    if (
        catalog_contract.get("prechange_scenario_count") != 44
        or catalog_contract.get("target_scenario_count") != 56
        or catalog_contract.get("target_attempt_count") != 168
        or catalog_contract.get("target_trace_event_count") != 258
    ):
        errors.append("catalog_target_mismatch")

    candidate_results = contract.get("candidate_results", {})
    candidate_paths = {
        "report_path": "artifacts/evaluations/runs/baseline-0025-attempt-001.json",
        "manifest_path": "artifacts/evaluations/runs/baseline-0025-attempt-001.manifest.json",
        "trace_path": "artifacts/evaluations/runs/baseline-0025-attempt-001.traces.jsonl",
    }
    if candidate_results == {"status": "absent_before_implementation"}:
        for relative in candidate_paths.values():
            if (ROOT / relative).exists():
                errors.append(f"unrecorded_candidate_artifact:{Path(relative).name}")
    elif candidate_results.get("status") != "recorded":
        errors.append("candidate_results_invalid")
    else:
        loaded: dict[str, object] = {}
        for key, relative in candidate_paths.items():
            if candidate_results.get(key) != relative:
                errors.append(f"candidate_{key}_mismatch")
                continue
            path = ROOT / relative
            if not path.is_file():
                errors.append(f"candidate_{key}_missing")
                continue
            bytes_key = key.replace("_path", "_bytes")
            digest_key = key.replace("_path", "_sha256")
            if path.stat().st_size != candidate_results.get(bytes_key):
                errors.append(f"candidate_{bytes_key}_mismatch")
            if sha256(path) != candidate_results.get(digest_key):
                errors.append(f"candidate_{digest_key}_mismatch")
            if key != "trace_path":
                loaded[key] = json.loads(path.read_text(encoding="utf-8"))

        report = loaded.get("report_path", {})
        candidate_manifest = loaded.get("manifest_path", {})
        if not isinstance(report, dict) or not isinstance(candidate_manifest, dict):
            errors.append("candidate_documents_unavailable")
        else:
            coverage = report.get("metrics", {}).get("coverage", {})
            security = report.get("metrics", {}).get("security", {})
            telemetry = report.get("metrics", {}).get(
                "telemetry_integrity", {}
            ).get("companion_trace", {})
            expected_report_identity = {
                "schema_version": "3.1",
                "checkpoint": "baseline-0025",
                "manifest_sha256": candidate_results.get("manifest_sha256"),
                "scenario_count": 56,
                "attempt_count": 168,
            }
            for key, expected in expected_report_identity.items():
                if report.get(key) != expected:
                    errors.append(f"candidate_report_{key}_mismatch")
            if candidate_manifest.get("checkpoint") != "baseline-0025":
                errors.append("candidate_manifest_checkpoint_mismatch")
            if report.get("gates", {}).get("baseline_disposition") != "pass":
                errors.append("candidate_disposition_mismatch")
            if coverage.get(
                "case_count_by_adversarial_domain_outcome_split"
            ) != target_counts:
                errors.append("candidate_counts_mismatch")
            if coverage.get("adversarial_domain_outcome_split_coverage") != 1.0:
                errors.append("candidate_coverage_mismatch")
            if coverage.get("split_adversarial_domain_outcome_coverage") != {
                "development": 1.0,
                "test": 1.0,
            }:
                errors.append("candidate_split_coverage_mismatch")
            if coverage.get("missing_adversarial_domain_outcome_split_cells") != []:
                errors.append("candidate_missing_cells_mismatch")
            if security.get("proposal_attack_success_rate") != 0.0:
                errors.append("candidate_proposal_attack_success_mismatch")
            if security.get("terminal_attack_success_rate") != 0.0:
                errors.append("candidate_terminal_attack_success_mismatch")
            if report.get("metrics", {}).get("terminal_state", {}).get(
                "exact_match_rate"
            ) != 1.0:
                errors.append("candidate_terminal_state_mismatch")
            if report.get("metrics", {}).get("tool_trajectory", {}).get(
                "exact_match"
            ) != 1.0:
                errors.append("candidate_tool_trajectory_mismatch")
            if report.get("metrics", {}).get("cost", {}).get("model_calls") != 0:
                errors.append("candidate_model_call_mismatch")
            if (
                telemetry.get("event_count") != 258
                or telemetry.get("final_event_sha256")
                != candidate_results.get("trace_final_event_sha256")
            ):
                errors.append("candidate_trace_anchor_mismatch")
            case_records = {
                item.get("scenario_id"): item
                for item in report.get("cases", [])
                if isinstance(item, dict)
            }
            if len(case_records) != 56 or any(
                item.get("all_trials_pass") is not True
                or len(item.get("attempts", [])) != 3
                for item in case_records.values()
            ):
                errors.append("candidate_case_inventory_mismatch")
            if any(
                case_records.get(case_id, {}).get("all_trials_pass") is not True
                for case_id in case_ids
            ):
                errors.append("candidate_new_cases_mismatch")

        report_path = ROOT / candidate_paths["report_path"]
        trace_path = ROOT / candidate_paths["trace_path"]
        if report_path.is_file() and trace_path.is_file():
            trace_result = verify_evaluation_trace(report_path, trace_path)
            if not trace_result.get("valid") or not trace_result.get("anchored"):
                errors.append("candidate_trace_verification_failed")
        latest = ROOT / "artifacts/evaluations/latest.json"
        if not valid_latest_report(latest, candidate_results.get("report_sha256")):
            errors.append("candidate_latest_pointer_mismatch")

        expected_result_values = {
            "scenario_count": 56,
            "attempt_count": 168,
            "baseline_disposition": "pass",
            "adversarial_domain_outcome_split_coverage": 1.0,
            "development_adversarial_domain_outcome_split_coverage": 1.0,
            "test_adversarial_domain_outcome_split_coverage": 1.0,
            "missing_adversarial_domain_outcome_split_cells": [],
            "new_cases_exact": 1.0,
            "proposal_attack_success": 0.0,
            "terminal_attack_success": 0.0,
            "all_prior_scenarios_exact": 1.0,
            "all_prior_terminal_states_exact": 1.0,
            "terminal_state_exact": 1.0,
            "tool_trajectory_exact": 1.0,
            "trace_event_count": 258,
        }
        for key, expected in expected_result_values.items():
            if candidate_results.get(key) != expected:
                errors.append(f"candidate_record_{key}_mismatch")

    result = {
        "status": "pass" if not errors else "fail",
        "checkpoint": "baseline-0025",
        "contract_id": contract.get("contract_id"),
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "implementation_present": implementation_present,
        "candidate_results_status": contract.get("candidate_results", {}).get(
            "status"
        ),
        "prechange_scenario_identity_count": len(frozen_scenarios),
        "prechange_terminal_identity_count": len(frozen_terminal_states),
        "prechange_coverage": 0.625,
        "current_covered_cell_count": covered_cells(current_counts),
        "target_covered_cell_count": 32,
        "current_missing_cells": current_missing,
        "case_count": len(case_ids),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
