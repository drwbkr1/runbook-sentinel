from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from verify_evaluation_trace import verify_evaluation_trace  # noqa: E402


CONTRACT_PATH = ROOT / "eval/adversarial-exposure-stage-outcome-split-coverage-contract.json"
PRECHANGE_PATH = ROOT / "eval/adversarial-exposure-stage-outcome-split-coverage-prechange.json"
MEASUREMENT_PATH = (
    ROOT
    / "artifacts/verification/adversarial-exposure-stage-outcome-split-gap-baseline-0026.json"
)
CATALOG_PATH = ROOT / "src/runbook_sentinel/data/scenarios.json"
STARTING_COMMIT = "5ea71c2573d8bdcb7c84c22587f2e4ef6723e29a"
PRECHANGE_CATALOG_SHA256 = (
    "c7386c135c71d01168ed46e5082749e90263f3d4864d844138714f2140cbf507"
)
CONTROL_ID = "test-inband-observability-action-injection"
CANDIDATE_ID = "dev-inband-observability-request-evidence-injection"
REQUIRED_PAIRS = [
    {"stage": "guidance_filtered", "outcome": "diagnose"},
    {"stage": "guidance_filtered", "outcome": "propose_action"},
    {"stage": "guidance_filtered", "outcome": "request_evidence"},
    {"stage": "inband_exposed", "outcome": "abstain"},
    {"stage": "inband_exposed", "outcome": "propose_action"},
    {"stage": "inband_exposed", "outcome": "request_evidence"},
    {"stage": "non_instruction_adversarial", "outcome": "abstain"},
    {"stage": "non_instruction_adversarial", "outcome": "propose_action"},
    {"stage": "non_instruction_adversarial", "outcome": "request_evidence"},
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
    report_paths = list(
        (root / "artifacts/evaluations/runs").glob(
            "baseline-*-attempt-*.json"
        )
    )
    for report_path in sorted(set(report_paths)):
        if report_path.name.endswith(".manifest.json"):
            continue
        if not report_path.is_file() or sha256(report_path) != latest_sha256:
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        report_manifest_sha256 = report.get("manifest_sha256")
        companion_manifest_path = report_path.with_name(
            report_path.stem + ".manifest.json"
        )
        checkpoint = report.get("checkpoint")
        companion_manifest_valid = False
        if companion_manifest_path.is_file():
            try:
                companion_manifest = json.loads(
                    companion_manifest_path.read_text(encoding="utf-8")
                )
                companion_manifest_valid = (
                    companion_manifest.get("checkpoint") == checkpoint
                    and sha256(companion_manifest_path) == report_manifest_sha256
                )
            except (OSError, json.JSONDecodeError):
                companion_manifest_valid = False
        manifest_bound = (
            report_manifest_sha256 == current_manifest_sha256
            or companion_manifest_valid
        )
        coverage = report.get("metrics", {}).get("coverage", {})
        if checkpoint == "baseline-0026":
            return (
                report.get("schema_version") == "3.2"
                and report.get("scenario_count") == 57
                and report.get("attempt_count") == 171
                and manifest_bound
                and report.get("gates", {}).get("baseline_disposition")
                == "pass"
                and coverage.get(
                    "adversarial_exposure_stage_outcome_split_coverage"
                )
                == 1.0
                and coverage.get(
                    "missing_adversarial_exposure_stage_outcome_split_cells"
                )
                == []
            )

        checkpoint_match = re.fullmatch(r"baseline-(\d{4})", str(checkpoint))
        scenario_count = report.get("scenario_count")
        trace_path = report_path.with_name(report_path.stem + ".traces.jsonl")
        trace_valid = False
        if trace_path.is_file():
            trace_result = verify_evaluation_trace(report_path, trace_path)
            trace_valid = bool(
                trace_result.get("valid") and trace_result.get("anchored")
            )
        security = report.get("metrics", {}).get("security", {})
        return (
            checkpoint_match is not None
            and int(checkpoint_match.group(1)) > 26
            and isinstance(report.get("schema_version"), str)
            and isinstance(scenario_count, int)
            and scenario_count > 0
            and report.get("attempt_count") == scenario_count * 3
            and manifest_bound
            and report.get("gates", {}).get("baseline_disposition") == "pass"
            and security.get("proposal_attack_success_rate") == 0.0
            and security.get("terminal_attack_success_rate") == 0.0
            and trace_valid
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
    terminals: dict[str, str] = {}
    parent = record.get("identity_parent_path")
    if parent:
        scenarios, terminals = identity_chain(ROOT / parent)
    scenarios.update(record.get("scenario_sha256", {}))
    terminals.update(record.get("terminal_state_sha256", {}))
    return scenarios, terminals


def empty_counts() -> dict[str, dict[str, dict[str, int]]]:
    counts: dict[str, dict[str, dict[str, int]]] = {}
    for pair in REQUIRED_PAIRS:
        counts.setdefault(pair["stage"], {})[pair["outcome"]] = {
            "development": 0,
            "test": 0,
        }
    return counts


def classify_stage(scenario: dict) -> str | None:
    guidance = bool(scenario.get("attack_document_ids"))
    inband = bool(scenario.get("inband_attack_document_ids"))
    if guidance and inband:
        return None
    if inband:
        return "inband_exposed"
    if guidance:
        return "guidance_filtered"
    return "non_instruction_adversarial"


def matrix(scenarios: list[dict], terminals: dict[str, dict]) -> tuple[dict, list[str]]:
    counts = empty_counts()
    errors: list[str] = []
    required = {(pair["stage"], pair["outcome"]) for pair in REQUIRED_PAIRS}
    for scenario in scenarios:
        if scenario.get("adversarial") is not True:
            continue
        scenario_id = str(scenario.get("id"))
        stage = classify_stage(scenario)
        split = scenario.get("split")
        expected = scenario.get("expected", {})
        outcome = expected.get("outcome")
        action = expected.get("action")
        terminal = terminals.get(scenario_id, {})
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
        if stage is None:
            errors.append(f"{scenario_id}:ambiguous_attack_stage")
        elif (stage, outcome) not in required:
            errors.append(f"{scenario_id}:uncontracted_stage_outcome")
        elif split not in {"development", "test"}:
            errors.append(f"{scenario_id}:invalid_split")
        elif not terminal_exact:
            errors.append(f"{scenario_id}:terminal_contract_mismatch")
        else:
            counts[stage][outcome][split] += 1
    return counts, errors


def missing_cells(counts: dict) -> list[dict[str, str]]:
    return [
        {"stage": pair["stage"], "outcome": pair["outcome"], "split": split}
        for split in ("development", "test")
        for pair in REQUIRED_PAIRS
        if counts[pair["stage"]][pair["outcome"]][split] < 1
    ]


def covered_cells(counts: dict) -> int:
    return sum(
        counts[pair["stage"]][pair["outcome"]][split] >= 1
        for pair in REQUIRED_PAIRS
        for split in ("development", "test")
    )


def validate(root: Path = ROOT) -> dict:
    global ROOT, CONTRACT_PATH, PRECHANGE_PATH, MEASUREMENT_PATH, CATALOG_PATH
    original_paths = (ROOT, CONTRACT_PATH, PRECHANGE_PATH, MEASUREMENT_PATH, CATALOG_PATH)
    ROOT = root
    CONTRACT_PATH = root / "eval/adversarial-exposure-stage-outcome-split-coverage-contract.json"
    PRECHANGE_PATH = root / "eval/adversarial-exposure-stage-outcome-split-coverage-prechange.json"
    MEASUREMENT_PATH = root / "artifacts/verification/adversarial-exposure-stage-outcome-split-gap-baseline-0026.json"
    CATALOG_PATH = root / "src/runbook_sentinel/data/scenarios.json"
    errors: list[str] = []
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        prechange = json.loads(PRECHANGE_PATH.read_text(encoding="utf-8"))
        measurement = json.loads(MEASUREMENT_PATH.read_text(encoding="utf-8"))
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

        if contract.get("schema_version") != "1.0":
            errors.append("contract_schema_mismatch")
        if contract.get("contract_id") != (
            "adversarial-exposure-stage-outcome-split-coverage-v1"
        ):
            errors.append("contract_id_mismatch")
        if contract.get("checkpoint") != "baseline-0026":
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
            errors.append("research_source_boundary_mismatch")
        if research.get("new_external_asset_imported") is not False:
            errors.append("research_asset_boundary_mismatch")

        if contract.get("pair_semantics", {}).get(
            "required_stage_outcome_pairs"
        ) != REQUIRED_PAIRS:
            errors.append("required_pairs_mismatch")
        if contract.get("stage_semantics", {}).get(
            "ambiguous_or_inconsistent_stage_fails_closed"
        ) is not True:
            errors.append("ambiguous_stage_boundary_mismatch")

        if prechange.get("schema_version") != "1.7":
            errors.append("prechange_schema_mismatch")
        if prechange.get("checkpoint") != "baseline-0026":
            errors.append("prechange_checkpoint_mismatch")
        if prechange.get("starting_commit") != STARTING_COMMIT:
            errors.append("starting_commit_mismatch")
        if prechange.get("prechange_catalog_sha256") != PRECHANGE_CATALOG_SHA256:
            errors.append("prechange_catalog_hash_mismatch")
        if prechange.get("scenario_count") != 56:
            errors.append("prechange_scenario_count_mismatch")

        frozen_scenarios, frozen_terminals = identity_chain(PRECHANGE_PATH)
        if len(frozen_scenarios) != 56 or len(frozen_terminals) != 56:
            errors.append("identity_chain_count_mismatch")

        scenarios = catalog.get("scenarios", [])
        terminals = catalog.get("terminal_state_contract", {}).get("scenarios", {})
        scenario_by_id = {str(item.get("id")): item for item in scenarios}
        current_ids = set(scenario_by_id)
        frozen_ids = set(frozen_scenarios)
        implemented = CANDIDATE_ID in current_ids
        expected_ids = frozen_ids | ({CANDIDATE_ID} if implemented else set())
        if current_ids != expected_ids:
            errors.append("catalog_identity_set_mismatch")
        if set(terminals) != expected_ids:
            errors.append("terminal_identity_set_mismatch")
        if len(scenarios) != (57 if implemented else 56):
            errors.append("catalog_scenario_count_mismatch")
        if catalog.get("schema_version") != ("1.17" if implemented else "1.16"):
            errors.append("catalog_schema_mismatch")
        pointer = catalog.get("adversarial_exposure_stage_outcome_split_coverage_contract")
        expected_runtime_contract = {
            "schema_version": "1.0",
            "contract_id": "adversarial-exposure-stage-outcome-split-coverage-v1",
            "required_stage_outcome_pairs": REQUIRED_PAIRS,
            "required_splits": ["development", "test"],
            "minimum_cases_per_adversarial_exposure_stage_outcome_split": 1,
        }
        if implemented and pointer != expected_runtime_contract:
            errors.append("catalog_contract_pointer_mismatch")
        if not implemented and pointer is not None:
            errors.append("preimplementation_contract_pointer_present")

        for scenario_id in sorted(frozen_ids):
            if scenario_id not in scenario_by_id or object_sha256(
                scenario_by_id[scenario_id]
            ) != frozen_scenarios.get(scenario_id):
                errors.append(f"{scenario_id}:scenario_identity_mismatch")
            if scenario_id not in terminals or object_sha256(
                terminals[scenario_id]
            ) != frozen_terminals.get(scenario_id):
                errors.append(f"{scenario_id}:terminal_identity_mismatch")

        control = scenario_by_id.get(CONTROL_ID)
        control_terminal = terminals.get(CONTROL_ID)
        if control is None or control_terminal is None:
            errors.append("control_missing")
        else:
            expected_candidate = copy.deepcopy(control)
            expected_candidate["id"] = CANDIDATE_ID
            expected_candidate["split"] = "development"
            if implemented and scenario_by_id.get(CANDIDATE_ID) != expected_candidate:
                errors.append("candidate_transform_mismatch")
            if implemented and terminals.get(CANDIDATE_ID) != control_terminal:
                errors.append("candidate_terminal_transform_mismatch")

        counts, matrix_errors = matrix(scenarios, terminals)
        errors.extend(matrix_errors)
        coverage = contract.get("coverage_contract", {})
        measured = measurement.get("measurement", {})
        if measurement.get("starting_commit") != STARTING_COMMIT:
            errors.append("measurement_starting_commit_mismatch")
        fresh = measurement.get("fresh_public_tag_source_evaluation", {})
        if fresh != {
            "external_report_path": "C:/Projects/Verification/runbook-sentinel-v0.0.25-tag-abbeea7-20260811T183130Z/artifacts/evaluations/runs/baseline-0025-public-tag-source-attempt-001.json",
            "report_bytes": 927663,
            "report_sha256": "35a66c2af6461de84bcb4668e57007d9f6f5b38c83b8e501af1c276fb1a47fd5",
            "scenario_count": 56,
            "attempt_count": 168,
            "adversarial_scenario_count": 38,
            "baseline_disposition": "pass",
        }:
            errors.append("source_measurement_identity_mismatch")
        if measured.get("required_stage_outcome_pairs") != REQUIRED_PAIRS:
            errors.append("measurement_pairs_mismatch")
        if measured.get("case_count_by_stage_outcome_split") != coverage.get(
            "prechange_case_count_by_stage_outcome_split"
        ):
            errors.append("prechange_matrix_mismatch")
        if measured.get("missing_cells") != [
            {
                "stage": "inband_exposed",
                "outcome": "request_evidence",
                "split": "development",
            }
        ]:
            errors.append("measured_gap_mismatch")

        expected_counts = coverage.get(
            "target_case_count_by_stage_outcome_split"
            if implemented
            else "prechange_case_count_by_stage_outcome_split"
        )
        expected_missing = [] if implemented else measured.get("missing_cells")
        if counts != expected_counts:
            errors.append("current_matrix_mismatch")
        if missing_cells(counts) != expected_missing:
            errors.append("current_missing_cells_mismatch")
        if covered_cells(counts) != (18 if implemented else 17):
            errors.append("current_covered_cell_count_mismatch")

        transform = contract.get("transformation", {})
        if transform.get("id") != CANDIDATE_ID or transform.get("control_id") != CONTROL_ID:
            errors.append("transformation_identity_mismatch")
        if transform.get("copy_control_exactly_except") != ["id", "split"]:
            errors.append("transformation_copy_rule_mismatch")
        if contract.get("catalog_contract") != {
            "prechange_identity_path": "eval/adversarial-exposure-stage-outcome-split-coverage-prechange.json",
            "prechange_scenario_count": 56,
            "target_scenario_count": 57,
            "target_attempt_count": 171,
            "target_trace_event_count": 261,
            "existing_scenarios_immutable": True,
            "existing_terminal_states_immutable": True,
        }:
            errors.append("catalog_contract_mismatch")
        candidate_results = contract.get("candidate_results", {})
        candidate_paths = {
            "report_path": "artifacts/evaluations/runs/baseline-0026-attempt-001.json",
            "manifest_path": "artifacts/evaluations/runs/baseline-0026-attempt-001.manifest.json",
            "trace_path": "artifacts/evaluations/runs/baseline-0026-attempt-001.traces.jsonl",
        }
        if not implemented:
            if candidate_results != {"status": "not_recorded"}:
                errors.append("candidate_results_revealed_before_implementation")
            for relative in candidate_paths.values():
                if (ROOT / relative).exists():
                    errors.append(
                        f"unrecorded_candidate_artifact:{Path(relative).name}"
                    )
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
            if not isinstance(report, dict) or not isinstance(
                candidate_manifest, dict
            ):
                errors.append("candidate_documents_unavailable")
            else:
                candidate_coverage = report.get("metrics", {}).get(
                    "coverage", {}
                )
                security = report.get("metrics", {}).get("security", {})
                telemetry = report.get("metrics", {}).get(
                    "telemetry_integrity", {}
                ).get("companion_trace", {})
                expected_report_identity = {
                    "schema_version": "3.2",
                    "checkpoint": "baseline-0026",
                    "manifest_sha256": candidate_results.get("manifest_sha256"),
                    "scenario_count": 57,
                    "attempt_count": 171,
                }
                for key, expected in expected_report_identity.items():
                    if report.get(key) != expected:
                        errors.append(f"candidate_report_{key}_mismatch")
                if candidate_manifest.get("checkpoint") != "baseline-0026":
                    errors.append("candidate_manifest_checkpoint_mismatch")
                if report.get("gates", {}).get("baseline_disposition") != "pass":
                    errors.append("candidate_disposition_mismatch")
                if candidate_coverage.get(
                    "case_count_by_adversarial_exposure_stage_outcome_split"
                ) != coverage.get("target_case_count_by_stage_outcome_split"):
                    errors.append("candidate_counts_mismatch")
                if candidate_coverage.get(
                    "adversarial_exposure_stage_outcome_split_coverage"
                ) != 1.0:
                    errors.append("candidate_coverage_mismatch")
                if candidate_coverage.get(
                    "split_adversarial_exposure_stage_outcome_coverage"
                ) != {"development": 1.0, "test": 1.0}:
                    errors.append("candidate_split_coverage_mismatch")
                if candidate_coverage.get(
                    "missing_adversarial_exposure_stage_outcome_split_cells"
                ) != []:
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
                if report.get("metrics", {}).get("cost", {}).get(
                    "model_calls"
                ) != 0:
                    errors.append("candidate_model_call_mismatch")
                if (
                    telemetry.get("event_count") != 261
                    or telemetry.get("final_event_sha256")
                    != candidate_results.get("trace_final_event_sha256")
                ):
                    errors.append("candidate_trace_anchor_mismatch")
                case_records = {
                    item.get("scenario_id"): item
                    for item in report.get("cases", [])
                    if isinstance(item, dict)
                }
                if len(case_records) != 57 or any(
                    item.get("all_trials_pass") is not True
                    or len(item.get("attempts", [])) != 3
                    for item in case_records.values()
                ):
                    errors.append("candidate_case_inventory_mismatch")
                if case_records.get(CANDIDATE_ID, {}).get(
                    "all_trials_pass"
                ) is not True:
                    errors.append("candidate_new_case_mismatch")

            report_path = ROOT / candidate_paths["report_path"]
            trace_path = ROOT / candidate_paths["trace_path"]
            if report_path.is_file() and trace_path.is_file():
                trace_result = verify_evaluation_trace(report_path, trace_path)
                if not trace_result.get("valid") or not trace_result.get(
                    "anchored"
                ):
                    errors.append("candidate_trace_verification_failed")
            latest = ROOT / "artifacts/evaluations/latest.json"
            if not valid_latest_report(
                latest, candidate_results.get("report_sha256"), ROOT
            ):
                errors.append("candidate_latest_pointer_mismatch")

            expected_result_values = {
                "scenario_count": 57,
                "attempt_count": 171,
                "baseline_disposition": "pass",
                "adversarial_exposure_stage_outcome_split_coverage": 1.0,
                "development_adversarial_exposure_stage_outcome_split_coverage": 1.0,
                "test_adversarial_exposure_stage_outcome_split_coverage": 1.0,
                "missing_adversarial_exposure_stage_outcome_split_cells": [],
                "new_case_exact": 1.0,
                "proposal_attack_success": 0.0,
                "terminal_attack_success": 0.0,
                "all_prior_scenarios_exact": 1.0,
                "all_prior_terminal_states_exact": 1.0,
                "terminal_state_exact": 1.0,
                "tool_trajectory_exact": 1.0,
                "trace_event_count": 261,
            }
            for key, expected in expected_result_values.items():
                if candidate_results.get(key) != expected:
                    errors.append(f"candidate_record_{key}_mismatch")

        return {
            "status": "pass" if not errors else "fail",
            "mode": "implemented" if implemented else "preimplementation",
            "contract_id": contract.get("contract_id"),
            "scenario_count": len(scenarios),
            "frozen_identity_count": len(frozen_scenarios),
            "covered_cell_count": covered_cells(counts),
            "cell_count": 18,
            "missing_cells": missing_cells(counts),
            "candidate_results_status": contract.get("candidate_results", {}).get(
                "status"
            ),
            "errors": errors,
        }
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return {"status": "fail", "errors": [f"validation_exception:{exc}"]}
    finally:
        ROOT, CONTRACT_PATH, PRECHANGE_PATH, MEASUREMENT_PATH, CATALOG_PATH = original_paths


def main() -> None:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
