from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "eval/container-contract.json"
VERSIONED_CONTRACT = ROOT / "eval/container-contract-0027-v4.json"
SUPERSEDED_V3_CONTRACT = ROOT / "eval/container-contract-0027-v3.json"
EXPECTED_V3_CONTRACT_SHA256 = (
    "1f63fcb6707f129ecc803c05026308680ea9417a6b61c4fdb4d379737d9d6b67"
)
EXPECTED_V3_FAILURE_SHA256 = (
    "ee7e53431a93431e295aea1c6fcca928b1963baefda29d00aeb8102d1496cf1f"
)
EXPECTED_V4_SOURCE_GATE_SHA256 = (
    "75d7ba7def6280dbca4748b1df1c36c536a277842c27dbf05dde8a9d711ac9a7"
)
EXPECTED_REPRODUCIBILITY_SOURCE_GATE_SHA256 = (
    "84368c0cf636e2afaca68e9ba47048f1b936af8205377e9de7604148c5abb1a2"
)
SOURCE_DATE_EPOCH_MANIFEST = (
    ROOT / "artifacts/evaluations/runs/baseline-0027-final-source-attempt-002.manifest.json"
)
EXPECTED_SOURCE_DATE_EPOCH_MANIFEST_SHA256 = (
    "cdc9ced520421f89b87ea04629bbce1b4a80e7f875b4366a6359c987a009f67a"
)
EXPECTED_BASE = (
    "cgr.dev/chainguard/python@"
    "sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5"
)
EXPECTED_PLATFORM_MANIFEST = (
    "sha256:15e66fa35e0b07095bbc4f4f0522718b780944709026687485f4e712cc6d5ae0"
)
EXPECTED_SOURCE_GATE_SHA256 = (
    "effc86d7c30dcbc08cbc7c70eb1271208acea5c1af725cd55b1577019ed24d18"
)
EXPECTED_V3_DOCKERFILE_LINES = [
    f"FROM {EXPECTED_BASE}",
    'LABEL org.opencontainers.image.title="Runbook Sentinel"',
    'LABEL org.opencontainers.image.description="Research-informed synthetic SRE incident-agent preview"',
    'LABEL org.opencontainers.image.version="0.0.27"',
    'LABEL org.opencontainers.image.source="https://github.com/drwbkr1/runbook-sentinel"',
    'LABEL dev.runbook-sentinel.base.digest="sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5"',
    "COPY --chown=65532:65532 dist/runbook-sentinel-0.0.27.pyz /opt/runbook-sentinel/runbook-sentinel.pyz",
    "COPY --chown=65532:65532 artifacts/evaluations/latest.json /opt/runbook-sentinel/evaluation.json",
    "WORKDIR /opt/runbook-sentinel",
    "USER 65532:65532",
    'ENTRYPOINT ["/usr/bin/python", "/opt/runbook-sentinel/runbook-sentinel.pyz"]',
    'CMD ["--help"]',
]
EXPECTED_DOCKERFILE_LINES = [
    *EXPECTED_V3_DOCKERFILE_LINES[:6],
    "COPY --chown=65532:65532 dist/runbook-sentinel-0.0.27.pyz /opt/runbook-sentinel/runbook-sentinel.pyz",
    "COPY --chown=65532:65532 artifacts/evaluations/latest.json /opt/runbook-sentinel/evaluation.json",
    *EXPECTED_V3_DOCKERFILE_LINES[9:],
]
EXPECTED_DOCKERIGNORE_LINES = [
    "**",
    "!dist/",
    "!dist/runbook-sentinel-0.0.27.pyz",
    "!artifacts/",
    "!artifacts/evaluations/",
    "!artifacts/evaluations/latest.json",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_contract(contract: dict, raw: bytes, errors: list[str]) -> None:
    expect(contract.get("schema_version") == "1.0", "schema_version must be 1.0", errors)
    expect(contract.get("contract_id") == "container-runtime-v4", "contract_id mismatch", errors)
    expect(contract.get("checkpoint") == "baseline-0027", "checkpoint mismatch", errors)
    expect(
        contract.get("contract_status")
        == "frozen_after_v3_metadata_validation_failure_before_v4_implementation",
        "contract_status mismatch",
        errors,
    )
    supersedes = contract.get("supersedes", {})
    expect(supersedes.get("contract_id") == "container-runtime-v3", "superseded contract mismatch", errors)
    expect(
        supersedes.get("contract_sha256") == EXPECTED_V3_CONTRACT_SHA256,
        "superseded contract hash mismatch",
        errors,
    )
    expect(
        supersedes.get("reason_receipts")
        == ["artifacts/verification/container-baseline-0027-v3-runtime-validation-failure-001.json"],
        "superseding receipt inventory mismatch",
        errors,
    )
    source = contract.get("source_checkpoint", {})
    expect(source.get("public_version") == "0.0.26", "source public version mismatch", errors)
    expect(
        source.get("public_release_commit") == "74bf5cba93b0697e74163a335c3dbfcc4d5d7418",
        "source public release commit mismatch",
        errors,
    )
    base = contract.get("base_image", {})
    expect(base.get("reference") == EXPECTED_BASE, "base reference mismatch", errors)
    expect(base.get("platform") == "linux/amd64", "base platform mismatch", errors)
    expect(
        base.get("platform_manifest_digest") == EXPECTED_PLATFORM_MANIFEST,
        "base platform manifest mismatch",
        errors,
    )
    expect(base.get("default_user") == "65532", "base default user mismatch", errors)
    expect(base.get("default_workdir") == "/", "base default workdir mismatch", errors)
    expect(base.get("source_gate_sha256") == EXPECTED_SOURCE_GATE_SHA256, "source gate hash mismatch", errors)
    counts = base.get("observed_vulnerability_counts", {})
    for severity in ("critical", "high", "medium", "low"):
        expect(counts.get(severity) == 0, f"base {severity} count must be zero", errors)
    candidate = contract.get("candidate", {})
    expect(candidate.get("version") == "0.0.27", "candidate version mismatch", errors)
    expect(candidate.get("user") == "65532:65532", "candidate user mismatch", errors)
    expect(candidate.get("workdir") == "/", "candidate workdir mismatch", errors)
    expect(candidate.get("published_image") is False, "candidate image publication must be false", errors)
    expect(candidate.get("exported_image_archive") is False, "candidate image export must be false", errors)
    expect(
        contract.get("dockerfile_contract", {}).get("expected_lines") == EXPECTED_DOCKERFILE_LINES,
        "Dockerfile contract lines mismatch",
        errors,
    )
    expect(
        contract.get("dockerignore_contract", {}).get("expected_lines") == EXPECTED_DOCKERIGNORE_LINES,
        ".dockerignore contract lines mismatch",
        errors,
    )
    build = contract.get("build_contract", {})
    v4_gate = build.get("v4_source_gate", {})
    expect(
        v4_gate.get("sha256") == EXPECTED_V4_SOURCE_GATE_SHA256,
        "v4 source gate hash mismatch",
        errors,
    )
    expect(v4_gate.get("status") == "ready", "v4 source gate not ready", errors)
    inherited_gate = build.get("inherited_buildkit_source_gate", {})
    expect(
        inherited_gate.get("sha256") == EXPECTED_REPRODUCIBILITY_SOURCE_GATE_SHA256,
        "inherited BuildKit source gate hash mismatch",
        errors,
    )
    expect(inherited_gate.get("status") == "ready", "inherited BuildKit source gate not ready", errors)
    compatibility = build.get("builder_compatibility", {})
    expect(compatibility.get("docker_engine") == "29.4.3", "Docker Engine compatibility mismatch", errors)
    expect(compatibility.get("docker_buildx") == "0.33.0-desktop.1", "Buildx compatibility mismatch", errors)
    expect(compatibility.get("buildkit") == "0.29.0", "BuildKit compatibility mismatch", errors)
    expect(compatibility.get("driver") == "docker", "builder driver compatibility mismatch", errors)
    expect(build.get("network") == "none", "build network must be none", errors)
    expect(
        build.get("cache") == "disabled for both independent builds and the clean-clone build",
        "build cache contract mismatch",
        errors,
    )
    expect(
        build.get("source_date_epoch")
        == {
            "value": "1786556577",
            "utc": "2026-08-12T17:42:57Z",
            "source": "artifacts/evaluations/runs/baseline-0027-final-source-attempt-002.manifest.json frozen_at_utc",
            "source_sha256": "cdc9ced520421f89b87ea04629bbce1b4a80e7f875b4366a6359c987a009f67a",
            "transport": "Buildx caller environment propagated to the special BuildKit build argument",
        },
        "SOURCE_DATE_EPOCH contract mismatch",
        errors,
    )
    expect(
        build.get("image_exporter")
        == {
            "type": "image",
            "name": "unique local verification tag",
            "rewrite_timestamp": True,
            "unpack": False,
            "store": True,
            "push": False,
            "destination": None,
        },
        "image exporter contract mismatch",
        errors,
    )
    expect(build.get("independent_build_count") == 2, "independent build count must be two", errors)
    expect(build.get("image_ids_must_match") is True, "image IDs must match", errors)
    expect(build.get("added_layer_count") == 2, "added layer count must be two", errors)
    expect(
        build.get("local_image_identity")
        == {
            "repo_digest_required_on_exact_builder": True,
            "repo_digest_content_must_equal_image_id": True,
            "repo_digest_is_publication_evidence": False,
            "required_event_scope": "local",
            "allowed_event_actions": ["create", "tag"],
        },
        "local image identity contract mismatch",
        errors,
    )
    expect(build.get("registry_push_allowed") is False, "registry push must be false", errors)
    runtime = contract.get("runtime_security_contract", {})
    required_runtime = {
        "read_only_rootfs": True,
        "no_new_privileges": True,
        "privileged": False,
        "external_egress": False,
        "real_infrastructure_connected": False,
        "secrets_or_credentials_mounted": False,
        "model_has_credentials_or_execution_authority": False,
        "mcp_has_approval_or_execution_tools": False,
    }
    for key, expected in required_runtime.items():
        expect(runtime.get(key) is expected, f"runtime boundary {key} mismatch", errors)
    expect(runtime.get("cap_drop") == ["ALL"], "runtime must drop ALL capabilities", errors)
    expect(
        runtime.get("api_network")
        == "none; docker exec invokes the actual HTTP surface through container-local loopback and extracts exact dashboard HTML for host rendering",
        "API network verification boundary mismatch",
        errors,
    )
    required_checks = contract.get("verification_contract", {}).get("required_checks", [])
    expect(len(required_checks) == 42, "exactly 42 container checks are required", errors)
    expect(len(required_checks) == len(set(required_checks)), "container check IDs must be unique", errors)
    expect(bool(contract.get("no_go_boundaries")), "no-go boundaries must be nonempty", errors)
    expect(raw.endswith(b"\n"), "contract must end with LF", errors)


def validate_source_gate(contract: dict, errors: list[str]) -> None:
    source_path = ROOT / contract["base_image"]["source_gate"]
    expect(source_path.is_file(), "source gate is missing", errors)
    if not source_path.is_file():
        return
    expect(sha256_file(source_path) == EXPECTED_SOURCE_GATE_SHA256, "source gate bytes changed", errors)
    source_gate = json.loads(source_path.read_text(encoding="utf-8"))
    expect(source_gate.get("decision", {}).get("status") == "ready", "source gate is not ready", errors)
    criteria = source_gate.get("sources", [{}])[0].get("criteria", [])
    expect(len(criteria) == 8, "source gate must contain eight criteria", errors)
    expect(all(item.get("status") == "pass" for item in criteria), "every source criterion must pass", errors)
    expect(
        source_gate.get("sources", [{}])[0].get("locator") == EXPECTED_BASE,
        "source gate admitted a different base",
        errors,
    )
    v4_path = ROOT / contract["build_contract"]["v4_source_gate"]["path"]
    expect(v4_path.is_file(), "v4 source gate is missing", errors)
    if v4_path.is_file():
        expect(sha256_file(v4_path) == EXPECTED_V4_SOURCE_GATE_SHA256, "v4 source gate bytes changed", errors)
        v4_gate = json.loads(v4_path.read_text(encoding="utf-8"))
        expect(v4_gate.get("decision", {}).get("status") == "ready", "v4 source gate is not ready", errors)
        criteria = [
            criterion
            for source in v4_gate.get("sources", [])
            for criterion in source.get("criteria", [])
        ]
        expect(len(criteria) == 8, "v4 source gate must contain eight criteria", errors)
        expect(all(item.get("status") == "pass" for item in criteria), "every v4 source criterion must pass", errors)
    reproducibility_path = ROOT / contract["build_contract"]["inherited_buildkit_source_gate"]["path"]
    expect(reproducibility_path.is_file(), "reproducibility source gate is missing", errors)
    if reproducibility_path.is_file():
        expect(
            sha256_file(reproducibility_path) == EXPECTED_REPRODUCIBILITY_SOURCE_GATE_SHA256,
            "reproducibility source gate bytes changed",
            errors,
        )
        reproducibility_gate = json.loads(reproducibility_path.read_text(encoding="utf-8"))
        expect(
            reproducibility_gate.get("decision", {}).get("status") == "ready",
            "reproducibility source gate is not ready",
            errors,
        )
        criteria = [
            criterion
            for source in reproducibility_gate.get("sources", [])
            for criterion in source.get("criteria", [])
        ]
        expect(len(criteria) == 16, "reproducibility source gate must contain sixteen criteria", errors)
        expect(
            all(item.get("status") == "pass" for item in criteria),
            "every reproducibility source criterion must pass",
            errors,
        )


def validate_reproducibility_inputs(contract: dict, errors: list[str]) -> None:
    expect(SUPERSEDED_V3_CONTRACT.is_file(), "superseded v3 contract is missing", errors)
    if SUPERSEDED_V3_CONTRACT.is_file():
        expect(
            sha256_file(SUPERSEDED_V3_CONTRACT) == EXPECTED_V3_CONTRACT_SHA256,
            "superseded v3 contract bytes changed",
            errors,
        )
    source_date_epoch = contract["build_contract"]["source_date_epoch"]
    expect(SOURCE_DATE_EPOCH_MANIFEST.is_file(), "SOURCE_DATE_EPOCH manifest is missing", errors)
    if SOURCE_DATE_EPOCH_MANIFEST.is_file():
        expect(
            sha256_file(SOURCE_DATE_EPOCH_MANIFEST) == EXPECTED_SOURCE_DATE_EPOCH_MANIFEST_SHA256,
            "SOURCE_DATE_EPOCH manifest bytes changed",
            errors,
        )
        manifest = json.loads(SOURCE_DATE_EPOCH_MANIFEST.read_text(encoding="utf-8"))
        expect(
            manifest.get("frozen_at_utc") == source_date_epoch["utc"],
            "SOURCE_DATE_EPOCH manifest timestamp mismatch",
            errors,
        )
        expect(
            source_date_epoch["source_sha256"] == EXPECTED_SOURCE_DATE_EPOCH_MANIFEST_SHA256,
            "SOURCE_DATE_EPOCH manifest contract hash mismatch",
            errors,
        )
    for receipt in contract["supersedes"]["reason_receipts"]:
        expect((ROOT / receipt).is_file(), f"superseding receipt is missing: {receipt}", errors)
        if (ROOT / receipt).is_file():
            expect(
                sha256_file(ROOT / receipt) == EXPECTED_V3_FAILURE_SHA256,
                "v3 failure receipt bytes changed",
                errors,
            )


def validate_implementation(contract: dict, require: bool, errors: list[str]) -> str:
    dockerfile = ROOT / contract["candidate"]["dockerfile"]
    dockerignore = ROOT / contract["candidate"]["dockerignore"]
    if not dockerfile.exists() and not dockerignore.exists():
        expect(not require, "Dockerfile and .dockerignore are required after implementation", errors)
        return "preimplementation"
    expect(dockerfile.is_file(), "Dockerfile is missing", errors)
    expect(dockerignore.is_file(), ".dockerignore is missing", errors)
    if dockerfile.is_file():
        dockerfile_lines = dockerfile.read_text(encoding="utf-8").splitlines()
        if dockerfile_lines == EXPECTED_DOCKERFILE_LINES:
            phase = "implemented_v4"
        elif dockerfile_lines == EXPECTED_V3_DOCKERFILE_LINES:
            phase = "superseded_v3_implementation"
            expect(not require, "v4 Dockerfile implementation is required", errors)
        else:
            phase = "nonconforming"
            expect(False, "Dockerfile bytes violate the frozen v4 instruction sequence", errors)
    else:
        phase = "missing"
    if dockerignore.is_file():
        expect(
            dockerignore.read_text(encoding="utf-8").splitlines() == EXPECTED_DOCKERIGNORE_LINES,
            ".dockerignore bytes violate the frozen context allowlist",
            errors,
        )
    return phase


def validate_receipt(contract: dict, receipt_path: Path, require: bool, errors: list[str]) -> str:
    if not receipt_path.exists():
        expect(not require, "container verification receipt is required", errors)
        return "absent"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expect(receipt.get("schema_version") == "1.0", "receipt schema mismatch", errors)
    expect(receipt.get("checkpoint") == "baseline-0027", "receipt checkpoint mismatch", errors)
    expect(receipt.get("status") == "pass", "receipt status must pass", errors)
    expect(receipt.get("contract_sha256") == sha256_file(DEFAULT_CONTRACT), "receipt contract hash mismatch", errors)
    expect(receipt.get("source_gate_sha256") == EXPECTED_SOURCE_GATE_SHA256, "receipt source gate hash mismatch", errors)
    expect(receipt.get("base_image", {}).get("reference") == EXPECTED_BASE, "receipt base mismatch", errors)
    expect(
        receipt.get("base_image", {}).get("platform_manifest_digest") == EXPECTED_PLATFORM_MANIFEST,
        "receipt platform manifest mismatch",
        errors,
    )
    image_ids = receipt.get("image", {}).get("independent_image_ids", [])
    expect(len(image_ids) == 2, "receipt must contain two image IDs", errors)
    normalized_ids = [value.removeprefix("sha256:") for value in image_ids if isinstance(value, str)]
    expect(len(normalized_ids) == 2 and all(SHA256_RE.fullmatch(value) for value in normalized_ids), "image IDs invalid", errors)
    expect(len(set(normalized_ids)) == 1, "independent image IDs differ", errors)
    checks = receipt.get("checks", {})
    required_checks = contract["verification_contract"]["required_checks"]
    expect(set(checks) == set(required_checks), "receipt check inventory mismatch", errors)
    expect(all(checks.get(check) is True for check in required_checks), "one or more container checks failed", errors)
    expect(receipt.get("publication", {}).get("image_exported") is False, "receipt exported image", errors)
    expect(receipt.get("publication", {}).get("image_pushed") is False, "receipt pushed image", errors)
    return "present"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the frozen Runbook Sentinel container contract.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--require-implementation", action="store_true")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--require-result", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    contract_path = args.contract.resolve()
    raw = contract_path.read_bytes()
    contract = json.loads(raw)
    validate_contract(contract, raw, errors)
    if contract_path == DEFAULT_CONTRACT.resolve():
        expect(VERSIONED_CONTRACT.read_bytes() == raw, "current and versioned container contracts differ", errors)
    validate_source_gate(contract, errors)
    validate_reproducibility_inputs(contract, errors)
    phase = validate_implementation(contract, args.require_implementation, errors)
    receipt_path = (args.receipt or ROOT / contract["verification_contract"]["receipt"]).resolve()
    receipt_state = validate_receipt(contract, receipt_path, args.require_result, errors)
    result = {
        "status": "pass" if not errors else "fail",
        "checkpoint": contract.get("checkpoint"),
        "contract_id": contract.get("contract_id"),
        "contract_sha256": hashlib.sha256(raw).hexdigest(),
        "implementation_phase": phase,
        "receipt_state": receipt_state,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
