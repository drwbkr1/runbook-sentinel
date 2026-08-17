from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/model-output-conformance-contract.json"
MODEL_CONTRACT_PATH = ROOT / "eval/model-contract.json"
SOURCE_GATE_PATH = (
    ROOT
    / "artifacts/verification/research-source-gate-baseline-0030-model-output-conformance.json"
)
EXPECTED_PATTERN = r"^[a-z][a-z0-9_]{0,79}$"
EXPECTED_REQUIRED_METRICS = [
    "retrieval",
    "generation",
    "tool_trajectory",
    "policy_compliance",
    "benign_utility",
    "proposal_attack_success",
    "terminal_attack_success",
    "repeated_trial_reliability",
    "latency",
    "cost",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def target_contract(legacy: dict[str, Any], frozen: dict[str, Any]) -> dict[str, Any]:
    target = copy.deepcopy(legacy)
    change = frozen["frozen_improvement"]
    target["schema_version"] = change["target_schema_version"]
    target["checkpoint"] = change["target_checkpoint"]
    target["contract_id"] = change["target_contract_id"]
    target["output_schema"]["properties"]["diagnosis_code"] = copy.deepcopy(
        change["target_diagnosis_code_schema"]
    )
    return target


def changed_paths(before: Any, after: Any, prefix: str = "$") -> list[str]:
    if type(before) is not type(after):
        return [prefix]
    if isinstance(before, dict):
        paths: list[str] = []
        for key in sorted(set(before) | set(after)):
            path = f"{prefix}.{key}"
            if key not in before or key not in after:
                paths.append(path)
            else:
                paths.extend(changed_paths(before[key], after[key], path))
        return paths
    if isinstance(before, list):
        if len(before) != len(after):
            return [prefix]
        paths = []
        for index, (left, right) in enumerate(zip(before, after)):
            paths.extend(changed_paths(left, right, f"{prefix}[{index}]"))
        return paths
    return [] if before == after else [prefix]


def validate(require_implementation: bool = False) -> dict[str, Any]:
    frozen = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    current = json.loads(MODEL_CONTRACT_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if frozen.get("schema_version") != "1.0":
        errors.append("contract_schema_version")
    if frozen.get("checkpoint") != "baseline-0030":
        errors.append("checkpoint")
    if frozen.get("contract_id") != "model-output-static-schema-conformance-v1":
        errors.append("contract_id")
    if frozen.get("status") != "frozen" or frozen.get("frozen_before_implementation") is not True:
        errors.append("freeze_status")

    public = frozen.get("starting_public_checkpoint", {})
    receipt_path = ROOT / public.get("public_receipt_path", "")
    if (
        not receipt_path.is_file()
        or receipt_path.stat().st_size != public.get("public_receipt_bytes")
        or sha256(receipt_path) != public.get("public_receipt_sha256")
    ):
        errors.append("public_receipt_identity")
    if public.get("main_commit") != "cc07fa2a0790a49b04b4352a004deb913bb12a60":
        errors.append("starting_main_identity")

    legacy_record = frozen.get("legacy_contract", {})
    archive_path = ROOT / legacy_record.get("archive_path", "")
    if (
        not archive_path.is_file()
        or archive_path.stat().st_size != legacy_record.get("bytes")
        or sha256(archive_path) != legacy_record.get("sha256")
    ):
        errors.append("legacy_archive_identity")
        legacy: dict[str, Any] = {}
    else:
        legacy = json.loads(archive_path.read_text(encoding="utf-8"))
    if legacy.get("contract_id") != legacy_record.get("contract_id"):
        errors.append("legacy_contract_id")
    if (
        legacy.get("output_schema", {}).get("properties", {}).get("diagnosis_code")
        != legacy_record.get("diagnosis_code_schema")
    ):
        errors.append("legacy_diagnosis_schema")

    measured = frozen.get("measured_failure", {})
    comparison_path = ROOT / measured.get("comparison_path", "")
    if (
        not comparison_path.is_file()
        or comparison_path.stat().st_size != measured.get("comparison_bytes")
        or sha256(comparison_path) != measured.get("comparison_sha256")
    ):
        errors.append("comparison_identity")
    else:
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        candidate = comparison.get("candidate", {})
        counts = candidate.get("failure_code_counts", {})
        metrics = candidate.get("metrics", {})
        expected_observations = {
            "attempt_count": comparison.get("frozen_comparison", {}).get(
                "attempt_count_per_configuration"
            ),
            "valid_output_count": candidate.get("parse_status_counts", {}).get("valid"),
            "schema_invalid_count": candidate.get("parse_status_counts", {}).get(
                "schema_invalid"
            ),
            "diagnosis_code_invalid_count": counts.get("diagnosis_code_invalid"),
            "proposal_arguments_invalid_count": counts.get("proposal_arguments_invalid"),
            "evidence_id_out_of_context_count": counts.get("evidence_id_out_of_context"),
            "structured_parse_success_rate": metrics.get("structured_parse_success_rate"),
            "diagnosis_accuracy": metrics.get("diagnosis_accuracy"),
            "benign_utility": metrics.get("benign_utility"),
            "pass_3": metrics.get("pass_3"),
            "policy_compliance": metrics.get("policy_compliance"),
            "proposal_attack_success": metrics.get("proposal_attack_success"),
            "terminal_attack_success": metrics.get("terminal_attack_success"),
        }
        for field, actual in expected_observations.items():
            if measured.get(field) != actual:
                errors.append(f"measured_{field}")

    parser = frozen.get("external_parser", {})
    parser_path = ROOT / parser.get("path", "")
    if (
        not parser_path.is_file()
        or parser_path.stat().st_size != parser.get("bytes")
        or sha256(parser_path) != parser.get("sha256")
    ):
        errors.append("parser_identity")
    else:
        parser_text = parser_path.read_text(encoding="utf-8")
        if f'DIAGNOSIS_CODE_RE = re.compile(r"{EXPECTED_PATTERN}")' not in parser_text:
            errors.append("parser_pattern")
    if parser.get("diagnosis_code_pattern") != EXPECTED_PATTERN:
        errors.append("frozen_parser_pattern")

    for name in ("agent", "policy"):
        boundaries = frozen.get("frozen_static_boundaries", {})
        path = ROOT / boundaries.get(f"{name}_path", "")
        if not path.is_file() or sha256(path) != boundaries.get(f"{name}_sha256"):
            errors.append(f"{name}_identity")
    boundaries = frozen.get("frozen_static_boundaries", {})
    catalog_path = ROOT / boundaries.get("catalog_path", "")
    if (
        not catalog_path.is_file()
        or catalog_path.stat().st_size != boundaries.get("catalog_bytes")
        or sha256(catalog_path) != boundaries.get("catalog_sha256")
    ):
        errors.append("catalog_identity")
    else:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        scenarios = catalog.get("scenarios", [])
        if len(scenarios) != boundaries.get("scenario_count"):
            errors.append("scenario_count")
        for split, field in (("development", "development_count"), ("test", "test_count")):
            if sum(item.get("split") == split for item in scenarios) != boundaries.get(field):
                errors.append(field)

    gate = json.loads(SOURCE_GATE_PATH.read_text(encoding="utf-8"))
    if gate.get("decision", {}).get("status") != "ready":
        errors.append("source_gate_not_ready")
    sources = gate.get("sources", [])
    criteria = [criterion for source in sources for criterion in source.get("criteria", [])]
    if len(sources) != 2 or len(criteria) != 16:
        errors.append("source_gate_inventory")
    if any(item.get("status") != "pass" for item in criteria):
        errors.append("source_gate_criteria")

    improvement = frozen.get("frozen_improvement", {})
    if improvement.get("target_diagnosis_code_schema", {}).get("pattern") != EXPECTED_PATTERN:
        errors.append("target_pattern")
    expected = target_contract(legacy, frozen) if legacy else {}
    expected_changes = [
        "$.checkpoint",
        "$.contract_id",
        "$.output_schema.properties.diagnosis_code.pattern",
        "$.schema_version",
    ]
    if changed_paths(legacy, expected) != expected_changes:
        errors.append("target_change_set")
    if any(
        improvement.get(field) is not False
        for field in (
            "system_prompt_changed",
            "user_template_changed",
            "runtime_or_model_changed",
            "parser_acceptance_changed",
            "retrieval_or_decision_context_changed",
            "scenario_or_terminal_state_changed",
            "policy_approval_executor_or_authority_changed",
            "tools_credentials_or_secrets_added",
            "external_asset_or_service_added",
        )
    ):
        errors.append("boundary_declaration")

    comparison_contract = frozen.get("comparison_contract", {})
    if comparison_contract.get("required_separate_metrics") != EXPECTED_REQUIRED_METRICS:
        errors.append("comparison_metric_inventory")
    if comparison_contract.get("test_split_used_for_optimization") is not False:
        errors.append("held_out_boundary")
    if comparison_contract.get("raw_output_storage") != (
        "sha256 digest and stable failure code only; no raw model content"
    ):
        errors.append("raw_output_boundary")

    phase = "implemented" if require_implementation else "frozen_preimplementation"
    if require_implementation:
        if current != expected:
            errors.append("implementation_projection")
        if frozen.get("implementation_result") is not None:
            result = frozen["implementation_result"]
            if result.get("contract_object_sha256") != object_sha256(current):
                errors.append("implementation_result_identity")
    else:
        if current != legacy:
            errors.append("implementation_present_before_public_freeze")
        if frozen.get("implementation_result") is not None:
            errors.append("implementation_result_present")

    result = {
        "status": "pass" if not errors else "fail",
        "checkpoint": frozen.get("checkpoint"),
        "contract_id": frozen.get("contract_id"),
        "implementation_phase": phase,
        "legacy_contract_sha256": sha256(archive_path) if archive_path.is_file() else None,
        "current_contract_object_sha256": object_sha256(current),
        "expected_target_object_sha256": object_sha256(expected) if expected else None,
        "permitted_changed_paths": expected_changes,
        "scenario_count": boundaries.get("scenario_count"),
        "attempt_count_per_model_contract": boundaries.get(
            "attempt_count_per_model_contract"
        ),
        "source_gate_ready": gate.get("decision", {}).get("status") == "ready",
        "errors": sorted(set(errors)),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-implementation", action="store_true")
    args = parser.parse_args()
    result = validate(require_implementation=args.require_implementation)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
