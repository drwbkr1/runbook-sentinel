from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "runbook-sentinel/release-identity-transition/v1"
RESULT_SHA256 = "6b81820e3942dd9ec4e603147fde0b58d73404effa46984ebc370bd44e5d454f"
RECEIPT_SHA256 = "8b597077247cb4b5b43455d090dd127dd737e1ecec2476fffd7adcb25874bd10"
PACKAGE_V32_SHA256 = "75f1b4de4cefda2f156fa7dbcae931a467a8ae58953992a912bbd1b8557c1079"
CONTAINER_V12_SHA256 = "de0fe568f1d5222731493277ab00d43feb06aa72e63b3b2b1e20ea081311d919"
CONTAINER_RECEIPT_V32_SHA256 = "b1ffc6b22385d2d359e8215a1f498fcefbed171895bd80e9f76bb7a391b0def0"
SOURCE_GATE_SHA256 = "f6317c0a7c4d01041c4676e221dff705475c1e7f171e356c2c344122c8994fc4"
INTAKE_SHA256 = "1172c50f7794ec6cc6f855f8b61fc1cf448df2c76221d7487fc3f03829cdf142"
BASE_REFERENCE = "cgr.dev/chainguard/python@sha256:1f6779775c9f466890da563e411cb677045a6c20b6a65160eefad1deffb5012c"
BASE_PLATFORM_MANIFEST = "sha256:e15765ff7066a0eaf91e1b6fd5000c1bba47d62b9f9731f2da560711d910c4f3"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def exact_path_hash(root: Path, relative: str, expected: str, errors: list[str]) -> None:
    path = root / relative
    expect(path.is_file(), f"missing required path: {relative}", errors)
    if path.is_file():
        expect(sha256(path) == expected, f"path hash mismatch: {relative}", errors)


def source_inventory(root: Path) -> list[str]:
    source_root = root / "src/runbook_sentinel"
    return sorted(
        path.relative_to(root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix in {".py", ".json"}
    )


def verify_runtime_identity(root: Path, contract: dict[str, Any], phase: str, errors: list[str]) -> None:
    runtime = contract.get("runtime_identity", {})
    mechanical = runtime.get("mechanical_paths", {})
    unchanged = runtime.get("unchanged_paths", {})
    expect(isinstance(mechanical, dict) and len(mechanical) == 4, "mechanical runtime identity set mismatch", errors)
    expect(isinstance(unchanged, dict) and len(unchanged) == 20, "unchanged runtime identity set mismatch", errors)
    if not isinstance(mechanical, dict) or not isinstance(unchanged, dict):
        return
    expected_inventory = sorted([*mechanical, *unchanged])
    expect(source_inventory(root) == expected_inventory, "enumerated product runtime inventory changed", errors)
    phase_key = "before_sha256" if phase == "frozen" else "after_sha256"
    for relative, identity in mechanical.items():
        if not isinstance(identity, dict):
            errors.append(f"invalid mechanical identity: {relative}")
            continue
        exact_path_hash(root, relative, str(identity.get(phase_key)), errors)
        replacements = identity.get("replacements")
        expect(
            isinstance(replacements, list)
            and replacements
            and all(isinstance(item, list) and len(item) == 3 and item[2] == 1 for item in replacements),
            f"mechanical replacement inventory mismatch: {relative}",
            errors,
        )
    for relative, expected in unchanged.items():
        exact_path_hash(root, relative, str(expected), errors)


def verify_mechanical_files(root: Path, contract: dict[str, Any], phase: str, errors: list[str]) -> None:
    identities = contract.get("mechanical_file_identities", {})
    expect(isinstance(identities, dict) and len(identities) == 10, "mechanical file identity set mismatch", errors)
    if not isinstance(identities, dict):
        return
    phase_key = "before_sha256" if phase == "frozen" else "after_sha256"
    for relative, identity in identities.items():
        if not isinstance(identity, dict):
            errors.append(f"invalid mechanical file identity: {relative}")
            continue
        exact_path_hash(root, relative, str(identity.get(phase_key)), errors)


def verify_adjudication(root: Path, contract: dict[str, Any], errors: list[str]) -> None:
    adjudication = contract.get("adjudication", {})
    result_path = root / str(adjudication.get("result_path"))
    receipt_path = root / str(adjudication.get("public_receipt_path"))
    exact_path_hash(root, str(adjudication.get("result_path")), RESULT_SHA256, errors)
    exact_path_hash(root, str(adjudication.get("public_receipt_path")), RECEIPT_SHA256, errors)
    if not result_path.is_file() or not receipt_path.is_file():
        return
    result = load_json(result_path)
    receipt = load_json(receipt_path)
    expect(adjudication.get("result_bytes") == 5086, "result byte contract mismatch", errors)
    expect(adjudication.get("result_sha256") == RESULT_SHA256, "result hash contract mismatch", errors)
    expect(adjudication.get("public_receipt_bytes") == 4652, "receipt byte contract mismatch", errors)
    expect(adjudication.get("public_receipt_sha256") == RECEIPT_SHA256, "receipt hash contract mismatch", errors)
    expect(result.get("checkpoint") == "baseline-0033", "result checkpoint mismatch", errors)
    expect(result.get("status") == "complete_candidate_admissible_not_selected", "result status mismatch", errors)
    expect(result.get("candidate_evidence_admissible") is True, "candidate evidence must remain admissible", errors)
    expect(result.get("candidate_selected") is False, "candidate must remain unselected", errors)
    expect(result.get("selected_configuration") == "freshness-priority-lexical-v3", "selected configuration changed", errors)
    expect(result.get("candidate_disposition") == "excluded_latency_noninferior_and_retained", "candidate disposition changed", errors)
    expect(result.get("remaining_failed_selection_checks") == ["median_latency_non_inferior"], "latency failure changed", errors)
    expect(receipt.get("status") == "pass", "public adjudication receipt is not pass", errors)
    expect(receipt.get("verification", {}).get("public_result_sha256") == RESULT_SHA256, "public receipt result hash mismatch", errors)
    boundaries = receipt.get("boundaries", {})
    expect(boundaries.get("candidate_selected") is False, "public receipt selects candidate", errors)
    expect(boundaries.get("v4_promoted") is False, "public receipt promotes v4", errors)
    expect(boundaries.get("runtime_or_default_changed") is False, "public receipt reports runtime change", errors)
    expect(boundaries.get("security_or_authority_changed") is False, "public receipt reports boundary change", errors)


def verify_predecessors(root: Path, contract: dict[str, Any], errors: list[str]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    package = contract.get("package_successor", {})
    container = contract.get("container_successor", {})
    package_path = root / str(package.get("predecessor_path"))
    container_path = root / str(container.get("predecessor_path"))
    exact_path_hash(root, str(package.get("predecessor_path")), PACKAGE_V32_SHA256, errors)
    exact_path_hash(root, str(container.get("predecessor_path")), CONTAINER_V12_SHA256, errors)
    exact_path_hash(root, str(container.get("predecessor_receipt")), CONTAINER_RECEIPT_V32_SHA256, errors)
    exact_path_hash(root, str(container.get("source_gate")), SOURCE_GATE_SHA256, errors)
    exact_path_hash(root, str(container.get("intake_receipt")), INTAKE_SHA256, errors)
    predecessor_package = load_json(package_path) if package_path.is_file() else None
    predecessor_container = load_json(container_path) if container_path.is_file() else None
    if predecessor_package is not None:
        expect(predecessor_package.get("checkpoint") == "baseline-0032", "predecessor package checkpoint mismatch", errors)
        expect(predecessor_package.get("candidate", {}).get("version") == "0.0.32", "predecessor package version mismatch", errors)
        expect(len(predecessor_package.get("entries", [])) == 43, "predecessor package entry count mismatch", errors)
    if predecessor_container is not None:
        expect(predecessor_container.get("contract_id") == "container-runtime-v12", "predecessor container id mismatch", errors)
        expect(predecessor_container.get("checkpoint") == "baseline-0032", "predecessor container checkpoint mismatch", errors)
        expect(predecessor_container.get("base_image", {}).get("reference") == BASE_REFERENCE, "predecessor base reference mismatch", errors)
        expect(
            predecessor_container.get("base_image", {}).get("platform_manifest_digest") == BASE_PLATFORM_MANIFEST,
            "predecessor platform manifest mismatch",
            errors,
        )
    return predecessor_package, predecessor_container


def verify_frozen_phase(root: Path, contract: dict[str, Any], errors: list[str]) -> None:
    package = contract["package_successor"]
    container = contract["container_successor"]
    exact_path_hash(root, str(package["active_path"]), PACKAGE_V32_SHA256, errors)
    exact_path_hash(root, str(container["active_path"]), CONTAINER_V12_SHA256, errors)
    for relative in (package["versioned_path"], container["versioned_path"], package["artifact"], package["checksum_artifact"]):
        expect(not (root / relative).exists(), f"successor artifact exists before public freeze: {relative}", errors)


def verify_implemented_phase(
    root: Path,
    contract: dict[str, Any],
    predecessor_package: dict[str, Any] | None,
    predecessor_container: dict[str, Any] | None,
    errors: list[str],
) -> None:
    package_rule = contract["package_successor"]
    container_rule = contract["container_successor"]
    package_path = root / package_rule["versioned_path"]
    active_package_path = root / package_rule["active_path"]
    container_path = root / container_rule["versioned_path"]
    active_container_path = root / container_rule["active_path"]
    for path in (package_path, active_package_path, container_path, active_container_path):
        expect(path.is_file(), f"missing implemented path: {path.relative_to(root)}", errors)
    if not all(path.is_file() for path in (package_path, active_package_path, container_path, active_container_path)):
        return
    expect(package_path.read_bytes() == active_package_path.read_bytes(), "active and versioned package contracts differ", errors)
    expect(container_path.read_bytes() == active_container_path.read_bytes(), "active and versioned container contracts differ", errors)
    successor_package = load_json(package_path)
    successor_container = load_json(container_path)
    expect(successor_package.get("checkpoint") == "baseline-0033", "successor package checkpoint mismatch", errors)
    expect(successor_package.get("candidate", {}).get("version") == "0.0.33", "successor package version mismatch", errors)
    expect(successor_package.get("candidate", {}).get("artifact") == "dist/runbook-sentinel-0.0.33.pyz", "successor package artifact mismatch", errors)
    expect(successor_package.get("candidate", {}).get("checksum_artifact") == "dist/runbook-sentinel-0.0.33.pyz.sha256", "successor checksum artifact mismatch", errors)
    expect(successor_package.get("package_manifest", {}).get("version") == "0.0.33", "successor package manifest version mismatch", errors)
    expect(successor_package.get("package_manifest", {}).get("checkpoint") == "baseline-0033", "successor package manifest checkpoint mismatch", errors)
    if predecessor_package is not None:
        for key in ("entries", "archive_metadata", "content_exclusions", "held_out_surfaces", "parity_contract", "release_gates", "no_go_boundaries"):
            expect(successor_package.get(key) == predecessor_package.get(key), f"successor package changed inherited field: {key}", errors)
    expect(successor_container.get("contract_id") == "container-runtime-v13", "successor container id mismatch", errors)
    expect(successor_container.get("checkpoint") == "baseline-0033", "successor container checkpoint mismatch", errors)
    expect(successor_container.get("candidate", {}).get("version") == "0.0.33", "successor container version mismatch", errors)
    expect(successor_container.get("candidate", {}).get("package_artifact") == "dist/runbook-sentinel-0.0.33.pyz", "successor container package mismatch", errors)
    inheritance = successor_container.get("inheritance", {})
    expect(inheritance.get("contract") == "eval/container-contract-0032-v12.json", "successor container inheritance path mismatch", errors)
    expect(inheritance.get("contract_id") == "container-runtime-v12", "successor container inheritance id mismatch", errors)
    expect(inheritance.get("contract_sha256") == CONTAINER_V12_SHA256, "successor container inheritance hash mismatch", errors)
    expect(inheritance.get("verified_result") == "artifacts/verification/container-baseline-0032.json", "successor container receipt inheritance mismatch", errors)
    expect(inheritance.get("verified_result_sha256") == CONTAINER_RECEIPT_V32_SHA256, "successor container receipt hash mismatch", errors)
    expect(successor_container.get("base_image", {}).get("reference") == BASE_REFERENCE, "successor base reference changed", errors)
    expect(successor_container.get("base_image", {}).get("platform_manifest_digest") == BASE_PLATFORM_MANIFEST, "successor platform manifest changed", errors)
    expect(successor_container.get("verification_contract", {}).get("receipt") == "artifacts/verification/container-baseline-0033.json", "successor receipt path mismatch", errors)
    candidate = successor_container.get("candidate", {})
    expect(candidate.get("published_image") is False, "successor container publication boundary changed", errors)
    expect(candidate.get("exported_image_archive") is False, "successor container export boundary changed", errors)
    if predecessor_container is not None:
        for key in (
            "dockerfile_contract",
            "dockerignore_contract",
            "event_capture_contract",
            "namespace_security_contract",
            "tmpfs_extraction_contract",
            "source_date_epoch_contract",
            "no_go_boundaries",
        ):
            if key in {"dockerfile_contract", "dockerignore_contract"}:
                continue
            expect(successor_container.get(key) == predecessor_container.get(key), f"successor container changed inherited field: {key}", errors)
        expect(
            successor_container.get("verification_contract", {}).get("required_checks")
            == predecessor_container.get("verification_contract", {}).get("required_checks"),
            "successor container required checks changed",
            errors,
        )


def evaluate(root: Path, phase: str) -> dict[str, Any]:
    errors: list[str] = []
    contract_path = root / "eval/release-identity-contract-0033.json"
    expect(contract_path.is_file(), "release identity contract is missing", errors)
    if errors:
        return {"valid": False, "phase": phase, "errors": errors}
    contract = load_json(contract_path)
    expect(contract.get("schema_version") == SCHEMA, "contract schema mismatch", errors)
    expect(contract.get("checkpoint") == "baseline-0033", "contract checkpoint mismatch", errors)
    expect(contract.get("contract_status") == "frozen_before_successor_identity_implementation", "contract status mismatch", errors)
    starting = contract.get("starting_checkpoint", {})
    expect(starting.get("public_record_commit") == "b125b5ecef4b3b3a406d3dc903a6de5ec4e02952", "starting commit mismatch", errors)
    expect(starting.get("public_record_tree") == "b5250a3ce5e3c4542bc4380b4eba4a45035ddf9a", "starting tree mismatch", errors)
    expect(starting.get("released_tag") == "v0.0.32", "starting release mismatch", errors)
    bounded = contract.get("bounded_change", {})
    expect(bounded.get("functional_product_delta") == [], "functional product delta must remain empty", errors)
    expect(bounded.get("new_project_dependencies") == [], "new project dependency is not allowed", errors)
    expect(bounded.get("new_external_assets") == [], "new external asset is not allowed", errors)
    expect(bounded.get("new_model_or_retrieval_configuration") == [], "new model or retrieval configuration is not allowed", errors)
    expect(contract.get("no_go_boundaries") and all(value is False for value in contract["no_go_boundaries"].values()), "a no-go boundary is asserted true", errors)
    verify_adjudication(root, contract, errors)
    verify_runtime_identity(root, contract, phase, errors)
    verify_mechanical_files(root, contract, phase, errors)
    predecessor_package, predecessor_container = verify_predecessors(root, contract, errors)
    if phase == "frozen":
        verify_frozen_phase(root, contract, errors)
    else:
        verify_implemented_phase(root, contract, predecessor_package, predecessor_container, errors)
    return {
        "valid": not errors,
        "phase": phase,
        "checkpoint": contract.get("checkpoint"),
        "candidate_evidence_admissible": contract.get("adjudication", {}).get("candidate_evidence_admissible"),
        "candidate_selected": contract.get("adjudication", {}).get("candidate_selected"),
        "selected_configuration": contract.get("adjudication", {}).get("selected_configuration"),
        "product_runtime_file_count": len(source_inventory(root)),
        "new_external_asset_count": len(bounded.get("new_external_assets", [])) if isinstance(bounded.get("new_external_assets"), list) else None,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the frozen BASELINE-0033 release-identity transition.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--phase", choices=("frozen", "implemented"), default="frozen")
    args = parser.parse_args()
    result = evaluate(args.root.resolve(), args.phase)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
