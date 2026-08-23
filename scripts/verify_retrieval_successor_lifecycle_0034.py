from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.catalog import load_scenarios  # noqa: E402
from runbook_sentinel import retrieval as runtime_retrieval  # noqa: E402


CONTRACT_PATH = ROOT / "eval/retrieval-successor-lifecycle-contract-0034.json"
IMPLEMENTATION_RESULT_PATH = (
    ROOT
    / "artifacts/verification/baseline-0034-retrieval-successor-bridge-implementation-local.json"
)
PUBLIC_BRIDGE_RECEIPT_PATH = (
    ROOT
    / "artifacts/verification/baseline-0034-retrieval-successor-bridge-public.json"
)
BENCHMARK_RESULT_PATH = ROOT / "artifacts/evaluations/baseline-0034-retriever-benchmark.json"
COMPARISON_RESULT_PATH = ROOT / "artifacts/evaluations/baseline-0034-retrieval-comparison.json"
CONTROL_CONFIGURATION = "freshness-priority-lexical-v3"
REFERENCE_CONFIGURATION = "bounded-trust-tier-lexical-v4"
CANDIDATE_CONFIGURATION = "single-pass-bounded-trust-tier-lexical-v5"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        errors.append(f"{label}_json")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}_object")
        return {}
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _exact(path: Path, record: dict[str, Any]) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == record.get("bytes")
        and _sha256(path) == record.get("sha256")
    )


def _bridge_changed_path_exact(
    root: Path,
    relative: str,
    record: dict[str, Any],
    contract: dict[str, Any],
) -> bool:
    path = root / relative
    if _exact(path, record):
        return True
    correction = contract.get("fixture_phase_correction", {})
    return (
        relative == correction.get("allowed_test_path")
        and _exact(path, correction.get("corrected_test_identity", {}))
    )


def _public_receipt_valid(root: Path, contract: dict[str, Any], errors: list[str]) -> bool:
    receipt_path = root / contract.get("bridge_implementation", {}).get(
        "public_receipt_path", ""
    )
    receipt = _load(receipt_path, errors, "bridge_public_receipt")
    valid = True
    if receipt.get("status") != "pass":
        errors.append("bridge_public_receipt_status")
        valid = False
    if receipt.get("contract_id") != contract.get("contract_id"):
        errors.append("bridge_public_receipt_contract")
        valid = False
    public = receipt.get("public_implementation", {})
    if not HEX40.fullmatch(str(public.get("commit", ""))):
        errors.append("bridge_public_receipt_commit")
        valid = False
    if not HEX40.fullmatch(str(public.get("tree", ""))):
        errors.append("bridge_public_receipt_tree")
        valid = False
    if receipt.get("boundaries", {}).get("runtime_retrieval_changed") is not False:
        errors.append("bridge_public_receipt_runtime_boundary")
        valid = False
    return valid


def _development_equivalence() -> dict[str, Any]:
    scenarios = [
        scenario for scenario in load_scenarios() if scenario.get("split") == "development"
    ]
    reference = runtime_retrieval.LexicalRetriever(REFERENCE_CONFIGURATION)
    candidate = runtime_retrieval.LexicalRetriever(CANDIDATE_CONFIGURATION)
    mismatches: list[dict[str, Any]] = []
    for scenario in scenarios:
        expected = [
            document["id"]
            for document in reference.retrieve(
                scenario["prompt"], scenario["documents"], as_of=scenario["as_of"]
            )
        ]
        actual = [
            document["id"]
            for document in candidate.retrieve(
                scenario["prompt"], scenario["documents"], as_of=scenario["as_of"]
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


def _validate_implementation_result(
    root: Path,
    contract: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    result_path = root / contract.get("bridge_implementation", {}).get(
        "implementation_result_path", ""
    )
    result = _load(result_path, errors, "bridge_implementation_result")
    if result.get("status") != "pass":
        errors.append("bridge_implementation_result_status")
    allowed = set(
        contract.get("bridge_implementation", {}).get("allowed_validator_paths", [])
    ) | set(contract.get("bridge_implementation", {}).get("allowed_test_paths", []))
    changed = result.get("changed_paths", [])
    if not isinstance(changed, list) or not changed:
        errors.append("bridge_implementation_changed_paths")
        return result
    seen: set[str] = set()
    for record in changed:
        if not isinstance(record, dict):
            errors.append("bridge_implementation_changed_path_record")
            continue
        relative = str(record.get("path", ""))
        seen.add(relative)
        if relative not in allowed:
            errors.append("bridge_implementation_path_outside_allowlist")
            continue
        if not _bridge_changed_path_exact(root, relative, record, contract):
            errors.append(f"bridge_implementation_identity:{relative}")
    required = set(
        contract.get("bridge_implementation", {}).get("allowed_validator_paths", [])
    )
    if not required.issubset(seen):
        errors.append("bridge_implementation_validator_coverage")
    return result


def validate(
    root: Path = ROOT,
    contract_path: Path | None = None,
    require_phase: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    contract = _load(
        contract_path or root / "eval/retrieval-successor-lifecycle-contract-0034.json",
        errors,
        "contract",
    )
    if contract.get("schema_version") != "1.2":
        errors.append("schema_version")
    if contract.get("checkpoint") != "baseline-0034":
        errors.append("checkpoint")
    if contract.get("contract_id") != "retrieval-predecessor-successor-lifecycle-v1":
        errors.append("contract_id")
    if contract.get("status") != "frozen_fixture_phase_corrected":
        errors.append("contract_status")
    correction = contract.get("lifecycle_correction", {})
    if any(
        correction.get(key) is not False
        for key in (
            "admissibility_or_selection_rule_changed",
            "historical_release_identity_weakened",
            "product_runtime_changed",
            "security_or_authority_changed",
        )
    ):
        errors.append("lifecycle_correction_boundary")
    fixture_correction = contract.get("fixture_phase_correction", {})
    if fixture_correction.get("retained_failure") != "V5-RELEASE-FIXTURE-PHASE-001":
        errors.append("fixture_phase_retained_failure")
    if fixture_correction.get("allowed_test_path") != "tests/test_release_identity_contract_0033.py":
        errors.append("fixture_phase_allowed_path")
    if fixture_correction.get("released_bridge_test_identity") != {
        "bytes": 6941,
        "sha256": "3000e914733f96d4f9513f53be7296b956ce7fb4979aa29b13b4ccae12427917",
    }:
        errors.append("fixture_phase_released_identity")
    if fixture_correction.get("corrected_test_identity") != {
        "bytes": 6944,
        "sha256": "861d8f346b77a4faffc981c98f18d091b2a1ef9fb3ade288bb4f7abc9b348a09",
    }:
        errors.append("fixture_phase_corrected_identity")
    if fixture_correction.get("exact_replacement") != {
        "from": "result = MODULE.evaluate(Path(directory), phase)",
        "to": "result = MODULE.evaluate(Path(directory), \"frozen\")",
        "required_occurrence_count": 1,
    }:
        errors.append("fixture_phase_replacement")
    if any(
        fixture_correction.get(key) is not False
        for key in (
            "release_identity_verifier_changed",
            "current_tree_bridge_validators_changed",
            "product_runtime_changed",
            "admissibility_or_selection_rule_changed",
            "security_or_authority_changed",
        )
    ):
        errors.append("fixture_phase_boundary")

    public = contract.get("public_preimplementation_sequence", {})
    public_receipt = root / str(public.get("receipt_path", ""))
    if not _exact(
        public_receipt,
        {
            "bytes": public.get("receipt_bytes"),
            "sha256": public.get("receipt_sha256"),
        },
    ):
        errors.append("preimplementation_public_receipt_identity")
    if public.get("record_commit") != "e554cd152466d87575da1ab653429e22007aa8d1":
        errors.append("preimplementation_record_commit")

    lifecycle = contract.get("retrieval_lifecycle", {})
    retrieval_path = root / str(lifecycle.get("path", ""))
    predecessor = lifecycle.get("released_predecessor", {})
    successor = lifecycle.get("exact_experimental_successor", {})
    predecessor_exact = _exact(retrieval_path, predecessor)
    successor_exact = _exact(retrieval_path, successor)
    target_predecessors = contract.get("historical_validator_predecessors", [])
    targets_original = all(
        isinstance(record, dict) and _exact(root / str(record.get("path", "")), record)
        for record in target_predecessors
    )
    implementation_result_present = (
        root
        / contract.get("bridge_implementation", {}).get("implementation_result_path", "")
    ).is_file()
    public_bridge_receipt_present = (
        root / contract.get("bridge_implementation", {}).get("public_receipt_path", "")
    ).is_file()

    development: dict[str, Any] | None = None
    if predecessor_exact:
        if CANDIDATE_CONFIGURATION in runtime_retrieval.RETRIEVAL_CONFIGURATIONS:
            errors.append("candidate_present_with_predecessor_bytes")
        if implementation_result_present:
            _validate_implementation_result(root, contract, errors)
            phase = (
                "bridge_public_predecessor"
                if public_bridge_receipt_present
                else "bridge_implemented_predecessor"
            )
            if public_bridge_receipt_present:
                _public_receipt_valid(root, contract, errors)
        else:
            phase = "bridge_frozen"
            if not targets_original:
                errors.append("historical_validator_changed_before_bridge_result")
            if public_bridge_receipt_present:
                errors.append("bridge_public_receipt_before_implementation")
    elif successor_exact:
        phase = "implementation_sealed_no_result"
        _public_receipt_valid(root, contract, errors)
        if CANDIDATE_CONFIGURATION not in runtime_retrieval.RETRIEVAL_CONFIGURATIONS:
            errors.append("candidate_missing_with_successor_bytes")
        if REFERENCE_CONFIGURATION not in runtime_retrieval.RETRIEVAL_CONFIGURATIONS:
            errors.append("reference_configuration_missing")
        development = _development_equivalence()
        if development["scenario_count"] != 31:
            errors.append("development_scenario_count")
        if development["mismatch_count"] != 0:
            errors.append("development_v4_v5_equivalence")
        if development["held_out_loaded"] is not False:
            errors.append("held_out_bridge_boundary")
        benchmark_present = BENCHMARK_RESULT_PATH.is_file()
        comparison_present = COMPARISON_RESULT_PATH.is_file()
        if benchmark_present or comparison_present:
            phase = "evaluated_unselected"
        if runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION == CANDIDATE_CONFIGURATION:
            phase = "selected"
            if not (benchmark_present and comparison_present):
                errors.append("selection_without_complete_results")
            comparison = _load(COMPARISON_RESULT_PATH, errors, "comparison_result")
            if comparison.get("candidate_selected") is not True:
                errors.append("selection_result_not_selected")
        elif runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION != CONTROL_CONFIGURATION:
            errors.append("unexpected_default_configuration")
    else:
        phase = "unknown_retrieval_identity"
        errors.append("retrieval_identity")

    if phase in {"bridge_frozen", "bridge_implemented_predecessor", "bridge_public_predecessor"}:
        if runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION != CONTROL_CONFIGURATION:
            errors.append("predecessor_default_changed")
        if BENCHMARK_RESULT_PATH.exists() or COMPARISON_RESULT_PATH.exists():
            errors.append("successor_result_present_before_runtime_implementation")
    if require_phase is not None and phase != require_phase:
        errors.append("required_phase")
    boundaries = contract.get("frozen_boundaries", {})
    if not boundaries or any(value is not False for value in boundaries.values()):
        errors.append("frozen_boundary")

    errors = sorted(set(errors))
    return {
        "schema_version": contract.get("schema_version"),
        "checkpoint": contract.get("checkpoint"),
        "contract_id": contract.get("contract_id"),
        "status": "pass" if not errors else "fail",
        "valid": not errors,
        "phase": phase,
        "errors": errors,
        "retrieval_identity": _identity(retrieval_path) if retrieval_path.is_file() else None,
        "targets_original": targets_original,
        "implementation_result_present": implementation_result_present,
        "public_bridge_receipt_present": public_bridge_receipt_present,
        "development_equivalence": development,
        "default_configuration": runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION,
        "benchmark_result_present": BENCHMARK_RESULT_PATH.is_file(),
        "comparison_result_present": COMPARISON_RESULT_PATH.is_file(),
        "held_out_loaded_by_bridge": False,
    }


def successor_runtime_is_allowed(root: Path = ROOT) -> bool:
    result = validate(root=root)
    return result["valid"] and result["phase"] in {
        "implementation_sealed_no_result",
        "evaluated_unselected",
        "selected",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-phase",
        choices=(
            "bridge_frozen",
            "bridge_implemented_predecessor",
            "bridge_public_predecessor",
            "implementation_sealed_no_result",
            "evaluated_unselected",
            "selected",
        ),
    )
    args = parser.parse_args()
    result = validate(require_phase=args.require_phase)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
