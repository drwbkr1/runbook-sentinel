from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/release-identity-contract-0035.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        errors.append(f"{label}_json")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}_object")
        return {}
    return value


def exact_identity(
    root: Path, record: dict[str, Any], errors: list[str], label: str
) -> Path:
    path = root / str(record.get("path", ""))
    if (
        not path.is_file()
        or path.stat().st_size != record.get("bytes")
        or sha256(path) != record.get("sha256")
    ):
        errors.append(f"{label}_identity")
    return path


def source_inventory(root: Path) -> list[str]:
    source = root / "src/runbook_sentinel"
    return sorted(
        path.relative_to(root).as_posix()
        for path in source.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


def verify_result(
    root: Path, contract: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    result_record = contract.get("classification_result", {})
    result_path = exact_identity(root, result_record, errors, "classification_result")
    receipt_record = {
        "path": result_record.get("public_receipt_path"),
        "bytes": result_record.get("public_receipt_bytes"),
        "sha256": result_record.get("public_receipt_sha256"),
    }
    exact_identity(root, receipt_record, errors, "classification_public_receipt")
    result = load_object(result_path, errors, "classification_result")
    expected = {
        "all_reports_candidate_evidence_admissible": True,
        "all_reports_hard_invariant_failure_count": 0,
        "candidate_selected": False,
        "selection_performed": False,
        "selected_configuration": "freshness-priority-lexical-v3",
        "historical_candidate_disposition": "exclude_and_retain",
        "historical_result_changed": False,
    }
    if any(result.get(key) != value for key, value in expected.items()):
        errors.append("classification_result_semantics")
    return result


def verify_runtime(
    root: Path, contract: dict[str, Any], phase: str, errors: list[str]
) -> None:
    runtime = contract.get("runtime_identity", {})
    mechanical = runtime.get("mechanical_paths", {})
    unchanged = runtime.get("unchanged_paths", {})
    expected_inventory = sorted([*mechanical, *unchanged])
    if source_inventory(root) != expected_inventory:
        errors.append("runtime_inventory")
    phase_key = "before_sha256" if phase == "frozen" else "after_sha256"
    for relative, identity in mechanical.items():
        path = root / relative
        if not path.is_file() or sha256(path) != identity.get(phase_key):
            errors.append(f"runtime_identity:{relative}")
    for relative, expected_hash in unchanged.items():
        path = root / relative
        if not path.is_file() or sha256(path) != expected_hash:
            errors.append(f"runtime_unchanged:{relative}")


def verify_frozen(
    root: Path, contract: dict[str, Any], errors: list[str]
) -> None:
    predecessors = contract.get("predecessors", {})
    for label, record in predecessors.items():
        exact_identity(root, record, errors, label)
    successors = contract.get("successors", {})
    for key in ("package_contract", "container_contract", "archive", "checksum"):
        if (root / str(successors.get(key, ""))).exists():
            errors.append(f"successor_present_before_public_freeze:{key}")


def verify_implemented(
    root: Path, contract: dict[str, Any], errors: list[str]
) -> None:
    successors = contract.get("successors", {})
    package_path = root / str(successors.get("package_contract", ""))
    container_path = root / str(successors.get("container_contract", ""))
    active_package = root / "eval/package-contract.json"
    active_container = root / "eval/container-contract.json"
    if not package_path.is_file() or not active_package.is_file():
        errors.append("successor_package_missing")
        package = {}
    else:
        if package_path.read_bytes() != active_package.read_bytes():
            errors.append("successor_package_active_mismatch")
        package = load_object(package_path, errors, "successor_package")
    if not container_path.is_file() or not active_container.is_file():
        errors.append("successor_container_missing")
        container = {}
    else:
        if container_path.read_bytes() != active_container.read_bytes():
            errors.append("successor_container_active_mismatch")
        container = load_object(container_path, errors, "successor_container")

    candidate = package.get("candidate", {})
    manifest = package.get("package_manifest", {})
    if (
        package.get("checkpoint") != "baseline-0035"
        or candidate.get("version") != "0.0.35"
        or candidate.get("artifact") != "dist/runbook-sentinel-0.0.35.pyz"
        or candidate.get("checksum_artifact")
        != "dist/runbook-sentinel-0.0.35.pyz.sha256"
        or manifest.get("checkpoint") != "baseline-0035"
        or manifest.get("version") != "0.0.35"
        or len(package.get("entries", [])) != 43
    ):
        errors.append("successor_package_semantics")

    container_candidate = container.get("candidate", {})
    base = container.get("base_image", {})
    external = contract.get("external_asset_reuse", {})
    if (
        container.get("contract_id") != "container-runtime-v14"
        or container.get("checkpoint") != "baseline-0035"
        or container_candidate.get("version") != "0.0.35"
        or container_candidate.get("package_artifact")
        != "dist/runbook-sentinel-0.0.35.pyz"
        or base.get("reference") != external.get("base_reference")
        or base.get("platform_manifest_digest")
        != external.get("platform_manifest_digest")
        or container_candidate.get("published_image") is not False
        or container_candidate.get("exported_image_archive") is not False
    ):
        errors.append("successor_container_semantics")


def evaluate(root: Path = ROOT, phase: str = "auto") -> dict[str, Any]:
    errors: list[str] = []
    contract = load_object(root / "eval/release-identity-contract-0035.json", errors, "contract")
    if (
        contract.get("schema_version")
        != "runbook-sentinel/release-identity-transition/v1.2"
        or contract.get("checkpoint") != "baseline-0035"
        or contract.get("contract_status")
        != "frozen_before_successor_identity_implementation"
    ):
        errors.append("contract_header")
    bounded = contract.get("bounded_change", {})
    if (
        bounded.get("functional_product_delta") != []
        or bounded.get("new_project_dependencies") != []
        or bounded.get("new_external_assets") != []
        or bounded.get("new_model_or_retrieval_configuration") != []
    ):
        errors.append("bounded_change")
    result = verify_result(root, contract, errors)

    external = contract.get("external_asset_reuse", {})
    exact_identity(root, external.get("source_gate", {}), errors, "base_source_gate")
    exact_identity(root, external.get("intake_receipt", {}), errors, "base_intake")

    successors = contract.get("successors", {})
    if phase == "auto":
        phase = (
            "implemented"
            if (root / str(successors.get("package_contract", ""))).is_file()
            else "frozen"
        )
    if phase not in ("frozen", "implemented"):
        errors.append("phase")
    else:
        verify_runtime(root, contract, phase, errors)
        if phase == "frozen":
            verify_frozen(root, contract, errors)
        else:
            verify_implemented(root, contract, errors)

    errors = sorted(set(errors))
    return {
        "schema_version": "1.0",
        "checkpoint": "baseline-0035",
        "phase": phase,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "product_runtime_file_count": len(source_inventory(root)),
        "candidate_selected": result.get("candidate_selected"),
        "selection_performed": result.get("selection_performed"),
        "selected_configuration": result.get("selected_configuration"),
        "historical_candidate_disposition": result.get(
            "historical_candidate_disposition"
        ),
        "successor_package_present": (
            root / str(successors.get("package_contract", ""))
        ).is_file(),
        "successor_container_present": (
            root / str(successors.get("container_contract", ""))
        ).is_file(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the frozen BASELINE-0035 release-identity transition."
    )
    parser.add_argument("--phase", choices=("auto", "frozen", "implemented"), default="auto")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = evaluate(args.root.resolve(), args.phase)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
