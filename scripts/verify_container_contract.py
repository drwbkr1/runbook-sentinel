from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "eval/container-contract.json"
VERSIONED_CONTRACT = ROOT / "eval/container-contract-0028-v8.json"
SUPERSEDED_V7_CONTRACT = ROOT / "eval/container-contract-0027-v7.json"
SUPERSEDED_V6_CONTRACT = ROOT / "eval/container-contract-0027-v6.json"
SUPERSEDED_V5_CONTRACT = ROOT / "eval/container-contract-0027-v5.json"
SUPERSEDED_V4_CONTRACT = ROOT / "eval/container-contract-0027-v4.json"
SUPERSEDED_V3_CONTRACT = ROOT / "eval/container-contract-0027-v3.json"
EXPECTED_V4_CONTRACT_SHA256 = (
    "ab822c1500ef09f0eff52759c7665536a5e9caa823f6c4ce2afa61614b5caacb"
)
EXPECTED_V4_EVENT_FAILURE_SHA256 = (
    "674760339e9b975b61cd496b4430ee946fa483861d918fb85b7bdbdc8f57b9f1"
)
EXPECTED_V5_SOURCE_GATE_SHA256 = (
    "8a318d1f943937a44772dccc4176d689015062cd6929094deb4a2caf15c5ab87"
)
EXPECTED_V5_CONTRACT_SHA256 = (
    "e71817e465dd8f25c183427389f7c1d1aaeefadbf318506e566e6eb0c842b30a"
)
EXPECTED_V5_RUNTIME_FAILURE_SHA256 = (
    "b340fcc5526a73f5730e48fccedbf0dc29c20aca6a09f6c8e553470594e2a0cd"
)
EXPECTED_V6_SOURCE_GATE_SHA256 = (
    "88a9448c8716c33bed7059ef5b60ef00cb3a466057fc9a8a6aec78824d2f4f07"
)
EXPECTED_V6_CONTRACT_SHA256 = (
    "76ca2b7dad77710a1a98ba0227847fffdb926a4e7610d0e7beded2aa8f5b27ae"
)
EXPECTED_V6_EXTRACTION_FAILURE_SHA256 = (
    "ba8f8210cfece3b6657d62aebc9314fc8aa39ed94ac952cee58f0d28c8434f70"
)
EXPECTED_V7_SOURCE_GATE_SHA256 = (
    "cc860f90ae5b04718790ab9f6ced70751a5df0f2e30b88f9aa72d6599021dd29"
)
EXPECTED_V7_CONTRACT_SHA256 = (
    "b4c078b1e2a836ddf23ab0644c9a1810bfe9e0fdf40997256396f3de439643c0"
)
EXPECTED_V7_RECEIPT_SHA256 = (
    "fd1c6952c42acf2703e88c365852605c00f112039e9aba26216287463a439949"
)
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
EXPECTED_V8_DOCKERFILE_LINES = list(EXPECTED_DOCKERFILE_LINES)
EXPECTED_V8_DOCKERFILE_LINES[3] = 'LABEL org.opencontainers.image.version="0.0.28"'
EXPECTED_V8_DOCKERFILE_LINES[6] = "COPY --chown=65532:65532 dist/runbook-sentinel-0.0.28.pyz /opt/runbook-sentinel/runbook-sentinel.pyz"
EXPECTED_V8_DOCKERIGNORE_LINES = list(EXPECTED_DOCKERIGNORE_LINES)
EXPECTED_V8_DOCKERIGNORE_LINES[2] = "!dist/runbook-sentinel-0.0.28.pyz"
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


def validate_v4_contract(contract: dict, raw: bytes, errors: list[str]) -> None:
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


def validate_v5_contract(contract: dict, raw: bytes, errors: list[str]) -> None:
    expect(contract.get("schema_version") == "1.0", "schema_version must be 1.0", errors)
    expect(contract.get("contract_id") == "container-runtime-v5", "contract_id mismatch", errors)
    expect(contract.get("checkpoint") == "baseline-0027", "checkpoint mismatch", errors)
    expect(
        contract.get("contract_status")
        == "frozen_after_v4_event_window_failure_before_v5_implementation",
        "contract_status mismatch",
        errors,
    )
    supersedes = contract.get("supersedes", {})
    expect(supersedes.get("contract") == "eval/container-contract-0027-v4.json", "superseded contract path mismatch", errors)
    expect(supersedes.get("contract_id") == "container-runtime-v4", "superseded contract ID mismatch", errors)
    expect(supersedes.get("contract_sha256") == EXPECTED_V4_CONTRACT_SHA256, "superseded v4 contract hash mismatch", errors)
    expect(
        supersedes.get("reason_receipt")
        == "artifacts/verification/container-baseline-0027-v4-event-window-failure-001.json",
        "v4 failure receipt path mismatch",
        errors,
    )
    expect(supersedes.get("reason_receipt_sha256") == EXPECTED_V4_EVENT_FAILURE_SHA256, "v4 failure receipt hash mismatch", errors)
    source = contract.get("source_checkpoint", {})
    expect(source.get("public_version") == "0.0.26", "source public version mismatch", errors)
    expect(source.get("public_v4_payload_commit") == "56fe0c1ac13f5ab2ce375e50e8882d44bfe4c90e", "public v4 payload commit mismatch", errors)
    expect(source.get("v4_image_ids_equal") is True, "v4 image identity evidence mismatch", errors)
    expect(source.get("v4_runtime_started") is False, "v4 runtime must remain unstarted", errors)
    inheritance = contract.get("inheritance", {})
    expect(inheritance.get("contract") == "eval/container-contract-0027-v4.json", "v4 inheritance path mismatch", errors)
    expect(inheritance.get("contract_sha256") == EXPECTED_V4_CONTRACT_SHA256, "v4 inheritance hash mismatch", errors)
    expect(len(inheritance.get("unchanged_surfaces", [])) == 7, "unchanged surface inventory mismatch", errors)
    gate = contract.get("v5_source_gate", {})
    expect(gate.get("path") == "artifacts/verification/research-source-gate-baseline-0027-container-v5-events.json", "v5 source gate path mismatch", errors)
    expect(gate.get("sha256") == EXPECTED_V5_SOURCE_GATE_SHA256, "v5 source gate hash mismatch", errors)
    expect(gate.get("status") == "ready", "v5 source gate not ready", errors)
    event = contract.get("event_capture_contract", {})
    expect(
        event
        == {
            "clock": "time.time_ns",
            "timestamp_format": "Unix seconds.nanoseconds with exactly nine fractional digits",
            "start_grace_nanoseconds": 1000000000,
            "completion_grace_nanoseconds": 1000000000,
            "query_filter": "type=image",
            "format": "Docker JSON Lines",
            "expected_tags": "both unique tags generated for the current verifier run",
            "expected_image_id": "the exact shared ID returned by both independent builds",
            "required_scope": "local",
            "allowed_actions": ["create", "tag"],
            "push_event_rejected": True,
            "remote_scope_rejected": True,
            "missing_tag_rejected": True,
            "unrelated_image_events_ignored": True,
            "claim_boundary": "The bounded future until value completes capture of the final event second; it does not weaken tag, image-ID, scope, action, exporter, or publication checks.",
        },
        "event capture contract mismatch",
        errors,
    )
    pre = contract.get("preimplementation_identity", {})
    expect(pre.get("runtime_verifier_v4_sha256") == "ed71ad8cbe8b379598c3e9442ecef2312992bae588cb2251a074c0dd1bc22712", "v4 runtime verifier identity mismatch", errors)
    expect(pre.get("tests_v4_sha256") == "67e0f54a9f3a70302595e04da0b01c8df9d8a5dbaab593c98441cf16f07a45db", "v4 tests identity mismatch", errors)
    required_checks = contract.get("verification_contract", {}).get("required_checks", [])
    expect(len(required_checks) == 42, "exactly 42 container checks are required", errors)
    expect(len(required_checks) == len(set(required_checks)), "container check IDs must be unique", errors)
    expect(bool(contract.get("no_go_boundaries")), "no-go boundaries must be nonempty", errors)
    expect(raw.endswith(b"\n"), "contract must end with LF", errors)


def validate_v6_contract(contract: dict, raw: bytes, errors: list[str]) -> None:
    expect(contract.get("schema_version") == "1.0", "schema_version must be 1.0", errors)
    expect(contract.get("contract_id") == "container-runtime-v6", "contract_id mismatch", errors)
    expect(contract.get("checkpoint") == "baseline-0027", "checkpoint mismatch", errors)
    expect(
        contract.get("contract_status")
        == "frozen_after_v5_private_ipc_validation_failure_before_v6_implementation",
        "contract_status mismatch",
        errors,
    )
    supersedes = contract.get("supersedes", {})
    expect(supersedes.get("contract") == "eval/container-contract-0027-v5.json", "superseded contract path mismatch", errors)
    expect(supersedes.get("contract_id") == "container-runtime-v5", "superseded contract ID mismatch", errors)
    expect(supersedes.get("contract_sha256") == EXPECTED_V5_CONTRACT_SHA256, "superseded v5 contract hash mismatch", errors)
    expect(
        supersedes.get("reason_receipt")
        == "artifacts/verification/container-baseline-0027-v5-runtime-security-failure-001.json",
        "v5 failure receipt path mismatch",
        errors,
    )
    expect(
        supersedes.get("reason_receipt_sha256") == EXPECTED_V5_RUNTIME_FAILURE_SHA256,
        "v5 failure receipt hash mismatch",
        errors,
    )
    source = contract.get("source_checkpoint", {})
    expect(source.get("public_version") == "0.0.26", "source public version mismatch", errors)
    expect(source.get("public_v5_payload_commit") == "a284c60c44972664294c67e4727f3075ac8a361d", "public v5 payload commit mismatch", errors)
    expect(source.get("v5_image_ids_equal") is True, "v5 image identity evidence mismatch", errors)
    expect(source.get("v5_event_window_passed") is True, "v5 event-window evidence mismatch", errors)
    expect(source.get("v5_product_runtime_started") is False, "v5 product runtime must remain unstarted", errors)
    inheritance = contract.get("inheritance", {})
    expect(inheritance.get("contract") == "eval/container-contract-0027-v5.json", "v5 inheritance path mismatch", errors)
    expect(inheritance.get("contract_sha256") == EXPECTED_V5_CONTRACT_SHA256, "v5 inheritance hash mismatch", errors)
    expect(len(inheritance.get("unchanged_surfaces", [])) == 7, "unchanged surface inventory mismatch", errors)
    gate = contract.get("v6_source_gate", {})
    expect(gate.get("path") == "artifacts/verification/research-source-gate-baseline-0027-container-v6-namespaces.json", "v6 source gate path mismatch", errors)
    expect(gate.get("sha256") == EXPECTED_V6_SOURCE_GATE_SHA256, "v6 source gate hash mismatch", errors)
    expect(gate.get("status") == "ready", "v6 source gate not ready", errors)
    expect(
        contract.get("event_capture_contract")
        == {
            "clock": "time.time_ns",
            "timestamp_format": "Unix seconds.nanoseconds with exactly nine fractional digits",
            "start_grace_nanoseconds": 1000000000,
            "completion_grace_nanoseconds": 1000000000,
            "query_filter": "type=image",
            "format": "Docker JSON Lines",
            "expected_tags": "both unique tags generated for the current verifier run",
            "expected_image_id": "the exact shared ID returned by both independent builds",
            "required_scope": "local",
            "allowed_actions": ["create", "tag"],
            "push_event_rejected": True,
            "remote_scope_rejected": True,
            "missing_tag_rejected": True,
            "unrelated_image_events_ignored": True,
            "claim_boundary": "The bounded future until value completes capture of the final event second; it does not weaken tag, image-ID, scope, action, exporter, or publication checks.",
        },
        "event capture contract mismatch",
        errors,
    )
    namespace = contract.get("namespace_security_contract", {})
    expect(namespace.get("builder_scope") == "Docker Engine 29.4.3, Docker Desktop 4.74.0, linux/amd64", "namespace builder scope mismatch", errors)
    expect(namespace.get("pid_mode") == "", "PID namespace mode mismatch", errors)
    expect(namespace.get("ipc_mode") == "private", "IPC namespace mode mismatch", errors)
    expect(namespace.get("uts_mode") == "", "UTS namespace mode mismatch", errors)
    expect(namespace.get("userns_mode") == "", "user namespace mode mismatch", errors)
    expect(len(namespace.get("reject", [])) == 4, "namespace rejection inventory mismatch", errors)
    pre = contract.get("preimplementation_identity", {})
    expect(pre.get("runtime_verifier_v5_sha256") == "1eca1d240f786891fc0412d4eb7b9c59b25cfab042e710169120d581fd0d1f06", "v5 runtime verifier identity mismatch", errors)
    expect(pre.get("tests_v5_sha256") == "bbe58a67924d7296682d99ce940b7db5eafe684dc125201a204970a71d153cae", "v5 tests identity mismatch", errors)
    required_checks = contract.get("verification_contract", {}).get("required_checks", [])
    expect(len(required_checks) == 42, "exactly 42 container checks are required", errors)
    expect(len(required_checks) == len(set(required_checks)), "container check IDs must be unique", errors)
    expect(bool(contract.get("no_go_boundaries")), "no-go boundaries must be nonempty", errors)
    expect(raw.endswith(b"\n"), "contract must end with LF", errors)


def validate_v7_contract(contract: dict, raw: bytes, errors: list[str]) -> None:
    expect(contract.get("schema_version") == "1.0", "schema_version must be 1.0", errors)
    expect(contract.get("contract_id") == "container-runtime-v7", "contract_id mismatch", errors)
    expect(contract.get("checkpoint") == "baseline-0027", "checkpoint mismatch", errors)
    expect(
        contract.get("contract_status")
        == "frozen_after_v6_tmpfs_extraction_failure_before_v7_implementation",
        "contract_status mismatch",
        errors,
    )
    supersedes = contract.get("supersedes", {})
    expect(supersedes.get("contract") == "eval/container-contract-0027-v6.json", "superseded contract path mismatch", errors)
    expect(supersedes.get("contract_id") == "container-runtime-v6", "superseded contract ID mismatch", errors)
    expect(supersedes.get("contract_sha256") == EXPECTED_V6_CONTRACT_SHA256, "superseded v6 contract hash mismatch", errors)
    expect(
        supersedes.get("reason_receipt")
        == "artifacts/verification/container-baseline-0027-v6-tmpfs-extraction-failure-001.json",
        "v6 failure receipt path mismatch",
        errors,
    )
    expect(
        supersedes.get("reason_receipt_sha256") == EXPECTED_V6_EXTRACTION_FAILURE_SHA256,
        "v6 failure receipt hash mismatch",
        errors,
    )
    source = contract.get("source_checkpoint", {})
    expect(source.get("public_version") == "0.0.26", "source public version mismatch", errors)
    expect(source.get("public_v6_payload_commit") == "6245be0b9241d789347ac3bb7ebf869561aaa5f4", "public v6 payload commit mismatch", errors)
    expect(source.get("v6_image_ids_equal") is True, "v6 image identity evidence mismatch", errors)
    expect(source.get("v6_event_window_passed") is True, "v6 event-window evidence mismatch", errors)
    expect(source.get("v6_runtime_security_passed") is True, "v6 runtime-security evidence mismatch", errors)
    expect(source.get("v6_cli_help_passed") is True, "v6 CLI evidence mismatch", errors)
    expect(source.get("v6_evaluation_exit_code") == 0, "v6 evaluation exit-code evidence mismatch", errors)
    expect(source.get("v6_artifact_extraction_passed") is False, "v6 extraction failure must remain explicit", errors)
    inheritance = contract.get("inheritance", {})
    expect(inheritance.get("contract") == "eval/container-contract-0027-v6.json", "v6 inheritance path mismatch", errors)
    expect(inheritance.get("contract_sha256") == EXPECTED_V6_CONTRACT_SHA256, "v6 inheritance hash mismatch", errors)
    expect(len(inheritance.get("unchanged_surfaces", [])) == 8, "unchanged surface inventory mismatch", errors)
    gate = contract.get("v7_source_gate", {})
    expect(gate.get("path") == "artifacts/verification/research-source-gate-baseline-0027-container-v7-extraction.json", "v7 source gate path mismatch", errors)
    expect(gate.get("sha256") == EXPECTED_V7_SOURCE_GATE_SHA256, "v7 source gate hash mismatch", errors)
    expect(gate.get("status") == "ready", "v7 source gate not ready", errors)
    expect(
        contract.get("event_capture_contract")
        == json.loads(SUPERSEDED_V6_CONTRACT.read_text(encoding="utf-8")).get("event_capture_contract"),
        "event capture contract mismatch",
        errors,
    )
    expect(
        contract.get("namespace_security_contract")
        == json.loads(SUPERSEDED_V6_CONTRACT.read_text(encoding="utf-8")).get("namespace_security_contract"),
        "namespace security contract mismatch",
        errors,
    )
    extraction = contract.get("tmpfs_extraction_contract", {})
    expected_sources = [
        "/state/container-evaluation.json",
        "/state/container-evaluation.traces.jsonl",
        "/state/mcp-traces.jsonl",
        "/state/mcp-traces.jsonl.anchor.json",
        "/state/dashboard.html",
        "/state/api.db",
        "/state/api-traces.jsonl",
        "/state/api-traces.jsonl.anchor.json",
    ]
    expect(extraction.get("allowed_sources") == expected_sources, "tmpfs extraction source allowlist mismatch", errors)
    expect(extraction.get("executable") == "/usr/bin/python", "tmpfs extraction executable mismatch", errors)
    expect(extraction.get("header_fields") == ["source", "bytes", "sha256"], "tmpfs extraction header mismatch", errors)
    expect(extraction.get("header_max_bytes") == 1024, "tmpfs extraction header bound mismatch", errors)
    expect(extraction.get("source_max_bytes") == 4 * 1024 * 1024, "tmpfs extraction size bound mismatch", errors)
    for key in (
        "stderr_must_be_empty",
        "exec_exit_code_must_be_zero",
        "destination_must_not_exist",
        "host_length_and_sha256_must_match_header",
        "host_postwrite_length_and_sha256_must_match",
    ):
        expect(extraction.get(key) is True, f"tmpfs extraction boundary {key} mismatch", errors)
    pre = contract.get("preimplementation_identity", {})
    expect(pre.get("runtime_verifier_v6_sha256") == "83a77bfbfa4178d8b5f05c836771c29e840f9191daaef6d2f91870983b3dca6d", "v6 runtime verifier identity mismatch", errors)
    expect(pre.get("tests_v6_sha256") == "55b49e5f1910c441be42de2bab043e30cfdb9ed42d4179b7618db84e762e1209", "v6 tests identity mismatch", errors)
    expect(pre.get("contract_verifier_v6_sha256") == "17b7adf9c20f7657761fa32235b5bd9b67de71579e049123543f1823817fe419", "v6 contract verifier identity mismatch", errors)
    required_checks = contract.get("verification_contract", {}).get("required_checks", [])
    expect(len(required_checks) == 43, "exactly 43 container checks are required", errors)
    expect("container_tmpfs_artifact_extraction_verified" in required_checks, "tmpfs extraction check is required", errors)
    expect(len(required_checks) == len(set(required_checks)), "container check IDs must be unique", errors)
    expect(bool(contract.get("no_go_boundaries")), "no-go boundaries must be nonempty", errors)
    expect(raw.endswith(b"\n"), "contract must end with LF", errors)


def validate_contract(contract: dict, raw: bytes, errors: list[str]) -> None:
    expect(contract.get("schema_version") == "1.0", "schema_version must be 1.0", errors)
    expect(contract.get("contract_id") == "container-runtime-v8", "contract_id mismatch", errors)
    expect(contract.get("checkpoint") == "baseline-0028", "checkpoint mismatch", errors)
    expect(
        contract.get("contract_status")
        == "frozen_before_v8_identity_implementation_and_any_v0.0.28_image_build",
        "contract_status mismatch",
        errors,
    )
    source = contract.get("source_checkpoint", {})
    expect(source.get("public_version") == "0.0.27", "source public version mismatch", errors)
    expect(
        source.get("source_candidate_commit")
        == "2b992bba676f30ab1ef0cc015ed8a812a2eba423",
        "source candidate commit mismatch",
        errors,
    )
    expect(
        source.get("source_candidate_report_sha256")
        == "4fb4b38e90a9a3094dbfdf63b3b15950b25030723176e543265136257e9cb79e",
        "source candidate report mismatch",
        errors,
    )
    expect(
        source.get("source_candidate_manifest_sha256")
        == "5bbd08327b569aba4381f7ea7a0dd01e0c05fc07e0861dcd7e35788bee763a9a",
        "source candidate manifest mismatch",
        errors,
    )
    inheritance = contract.get("inheritance", {})
    expect(inheritance.get("contract") == "eval/container-contract-0027-v7.json", "v7 inheritance path mismatch", errors)
    expect(inheritance.get("contract_id") == "container-runtime-v7", "v7 inheritance ID mismatch", errors)
    expect(inheritance.get("contract_sha256") == EXPECTED_V7_CONTRACT_SHA256, "v7 inheritance hash mismatch", errors)
    expect(inheritance.get("verified_result_sha256") == EXPECTED_V7_RECEIPT_SHA256, "v7 receipt hash mismatch", errors)
    candidate = contract.get("candidate", {})
    expect(candidate.get("version") == "0.0.28", "candidate version mismatch", errors)
    expect(candidate.get("package_artifact") == "dist/runbook-sentinel-0.0.28.pyz", "candidate package mismatch", errors)
    expect(candidate.get("published_image") is False, "candidate image publication must be false", errors)
    expect(candidate.get("exported_image_archive") is False, "candidate image export must be false", errors)
    base = contract.get("base_image", {})
    expect(base.get("reference") == EXPECTED_BASE, "base reference mismatch", errors)
    expect(base.get("platform_manifest_digest") == EXPECTED_PLATFORM_MANIFEST, "base platform manifest mismatch", errors)
    expect(base.get("source_gate_sha256") == EXPECTED_SOURCE_GATE_SHA256, "source gate hash mismatch", errors)
    expect(contract.get("dockerfile_contract", {}).get("expected_lines") == EXPECTED_V8_DOCKERFILE_LINES, "Dockerfile contract lines mismatch", errors)
    expect(contract.get("dockerignore_contract", {}).get("expected_lines") == EXPECTED_V8_DOCKERIGNORE_LINES, ".dockerignore contract lines mismatch", errors)
    v7 = json.loads(SUPERSEDED_V7_CONTRACT.read_text(encoding="utf-8")) if SUPERSEDED_V7_CONTRACT.is_file() else {}
    for key in ("event_capture_contract", "namespace_security_contract", "tmpfs_extraction_contract"):
        expect(contract.get(key) == v7.get(key), f"{key.replace('_', ' ')} mismatch", errors)
    pre = contract.get("preimplementation_identity", {})
    expect(pre.get("runtime_verifier_v7_sha256") == "fecf7160c14131ecaff592255cf4445d6ed100dc559218aeb3e01ecee16387c6", "v7 runtime verifier identity mismatch", errors)
    expect(pre.get("tests_v7_sha256") == "5f6dcbe1716fed2df6ea4e73a78c77f9c4d11885b62577ce930c8ee92cdc5ba9", "v7 tests identity mismatch", errors)
    expect(pre.get("contract_verifier_v7_sha256") == "bb4feabe13639b1cb704719b8bf631d94540709a535b24c8f89aba40d62e37d6", "v7 contract verifier identity mismatch", errors)
    required_checks = contract.get("verification_contract", {}).get("required_checks", [])
    expect(len(required_checks) == 44, "exactly 44 container checks are required", errors)
    expect("container_retrieval_stage_metric_exact" in required_checks, "retrieval-stage metric check is required", errors)
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


def validate_v5_source_gate(contract: dict, errors: list[str]) -> None:
    gate_path = ROOT / contract["v5_source_gate"]["path"]
    expect(gate_path.is_file(), "v5 source gate is missing", errors)
    if not gate_path.is_file():
        return
    expect(sha256_file(gate_path) == EXPECTED_V5_SOURCE_GATE_SHA256, "v5 source gate bytes changed", errors)
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    expect(gate.get("decision", {}).get("status") == "ready", "v5 source gate is not ready", errors)
    criteria = [
        criterion
        for source in gate.get("sources", [])
        for criterion in source.get("criteria", [])
    ]
    expect(len(criteria) == 8, "v5 source gate must contain eight criteria", errors)
    expect(all(item.get("status") == "pass" for item in criteria), "every v5 source criterion must pass", errors)


def validate_v6_source_gate(contract: dict, errors: list[str]) -> None:
    gate_path = ROOT / contract["v6_source_gate"]["path"]
    expect(gate_path.is_file(), "v6 source gate is missing", errors)
    if not gate_path.is_file():
        return
    expect(sha256_file(gate_path) == EXPECTED_V6_SOURCE_GATE_SHA256, "v6 source gate bytes changed", errors)
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    expect(gate.get("decision", {}).get("status") == "ready", "v6 source gate is not ready", errors)
    criteria = [
        criterion
        for source in gate.get("sources", [])
        for criterion in source.get("criteria", [])
    ]
    expect(len(criteria) == 8, "v6 source gate must contain eight criteria", errors)
    expect(all(item.get("status") == "pass" for item in criteria), "every v6 source criterion must pass", errors)


def validate_v7_source_gate(contract: dict, errors: list[str]) -> None:
    gate_path = ROOT / contract["v7_source_gate"]["path"]
    expect(gate_path.is_file(), "v7 source gate is missing", errors)
    if not gate_path.is_file():
        return
    expect(sha256_file(gate_path) == EXPECTED_V7_SOURCE_GATE_SHA256, "v7 source gate bytes changed", errors)
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    expect(gate.get("decision", {}).get("status") == "ready", "v7 source gate is not ready", errors)
    criteria = [
        criterion
        for source in gate.get("sources", [])
        for criterion in source.get("criteria", [])
    ]
    expect(len(criteria) == 16, "v7 source gate must contain sixteen criteria", errors)
    expect(all(item.get("status") == "pass" for item in criteria), "every v7 source criterion must pass", errors)


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


def validate_v5_implementation(require: bool, errors: list[str]) -> str:
    runtime_path = ROOT / "scripts/verify_container_runtime.py"
    tests_path = ROOT / "tests/test_baseline.py"
    expect(runtime_path.is_file(), "container runtime verifier is missing", errors)
    expect(tests_path.is_file(), "container tests are missing", errors)
    if not runtime_path.is_file() or not tests_path.is_file():
        return "missing"
    runtime_hash = sha256_file(runtime_path)
    tests_hash = sha256_file(tests_path)
    v4_exact = (
        runtime_hash == "ed71ad8cbe8b379598c3e9442ecef2312992bae588cb2251a074c0dd1bc22712"
        and tests_hash == "67e0f54a9f3a70302595e04da0b01c8df9d8a5dbaab593c98441cf16f07a45db"
    )
    runtime_text = runtime_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")
    v5_markers = [
        "EVENT_WINDOW_GRACE_NANOSECONDS = 1_000_000_000",
        "def format_unix_nanoseconds(value: int) -> str:",
        "build_started_at_ns = time.time_ns() - EVENT_WINDOW_GRACE_NANOSECONDS",
        "build_finished_at_ns = time.time_ns() + EVENT_WINDOW_GRACE_NANOSECONDS",
        "image_events(build_started_at_ns, build_finished_at_ns)",
    ]
    v5_exact = all(marker in runtime_text for marker in v5_markers) and all(
        marker in tests_text
        for marker in (
            "test_container_v5_event_time_bounds_are_nanosecond_complete",
            "format_unix_nanoseconds",
        )
    )
    if v5_exact:
        return "implemented_v5"
    if v4_exact:
        expect(not require, "v5 event-window implementation is required", errors)
        return "frozen_v4_preimplementation"
    expect(False, "container verifier or tests do not match frozen v4 or required v5 implementation", errors)
    return "nonconforming"


def validate_v6_implementation(require: bool, errors: list[str]) -> str:
    runtime_path = ROOT / "scripts/verify_container_runtime.py"
    tests_path = ROOT / "tests/test_baseline.py"
    expect(runtime_path.is_file(), "container runtime verifier is missing", errors)
    expect(tests_path.is_file(), "container tests are missing", errors)
    if not runtime_path.is_file() or not tests_path.is_file():
        return "missing"
    runtime_hash = sha256_file(runtime_path)
    tests_hash = sha256_file(tests_path)
    v5_exact = (
        runtime_hash == "1eca1d240f786891fc0412d4eb7b9c59b25cfab042e710169120d581fd0d1f06"
        and tests_hash == "bbe58a67924d7296682d99ce940b7db5eafe684dc125201a204970a71d153cae"
    )
    runtime_text = runtime_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")
    v6_markers = [
        '"pid_mode_empty": host.get("PidMode") == ""',
        '"ipc_mode_private": host.get("IpcMode") == "private"',
        '"uts_mode_empty": host.get("UTSMode") == ""',
        '"userns_mode_empty": host.get("UsernsMode") == ""',
    ]
    v6_exact = all(marker in runtime_text for marker in v6_markers) and all(
        marker in tests_text
        for marker in (
            "test_container_v6_namespace_modes_fail_closed",
            "namespace_security_checks",
        )
    )
    if v6_exact:
        return "implemented_v6"
    if v5_exact:
        expect(not require, "v6 namespace-mode implementation is required", errors)
        return "frozen_v5_preimplementation"
    expect(False, "container verifier or tests do not match frozen v5 or required v6 implementation", errors)
    return "nonconforming"


def validate_v7_implementation(require: bool, errors: list[str]) -> str:
    runtime_path = ROOT / "scripts/verify_container_runtime.py"
    tests_path = ROOT / "tests/test_baseline.py"
    expect(runtime_path.is_file(), "container runtime verifier is missing", errors)
    expect(tests_path.is_file(), "container tests are missing", errors)
    if not runtime_path.is_file() or not tests_path.is_file():
        return "missing"
    runtime_hash = sha256_file(runtime_path)
    tests_hash = sha256_file(tests_path)
    v6_exact = (
        runtime_hash == "83a77bfbfa4178d8b5f05c836771c29e840f9191daaef6d2f91870983b3dca6d"
        and tests_hash == "55b49e5f1910c441be42de2bab043e30cfdb9ed42d4179b7618db84e762e1209"
    )
    runtime_text = runtime_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")
    v7_markers = [
        "ALLOWED_TMPFS_EXTRACTION_SOURCES",
        "def decode_tmpfs_extraction_stream(",
        "def extract_tmpfs_file(",
        '"container_tmpfs_artifact_extraction_verified"',
    ]
    v7_exact = all(marker in runtime_text for marker in v7_markers) and all(
        marker in tests_text
        for marker in (
            "test_container_v7_tmpfs_extraction_stream_fails_closed",
            "decode_tmpfs_extraction_stream",
        )
    )
    if v7_exact:
        return "implemented_v7"
    if v6_exact:
        expect(not require, "v7 tmpfs extraction implementation is required", errors)
        return "frozen_v6_preimplementation"
    expect(False, "container verifier or tests do not match frozen v6 or required v7 implementation", errors)
    return "nonconforming"


def validate_v8_implementation(require: bool, errors: list[str]) -> str:
    runtime_path = ROOT / "scripts/verify_container_runtime.py"
    tests_path = ROOT / "tests/test_baseline.py"
    expect(runtime_path.is_file(), "container runtime verifier is missing", errors)
    expect(tests_path.is_file(), "container tests are missing", errors)
    if not runtime_path.is_file() or not tests_path.is_file():
        return "missing"
    runtime_hash = sha256_file(runtime_path)
    tests_hash = sha256_file(tests_path)
    v7_exact = (
        runtime_hash == "fecf7160c14131ecaff592255cf4445d6ed100dc559218aeb3e01ecee16387c6"
        and tests_hash == "5f6dcbe1716fed2df6ea4e73a78c77f9c4d11885b62577ce930c8ee92cdc5ba9"
    )
    runtime_text = runtime_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")
    markers = [
        'PACKAGE_PATH = ROOT / "dist/runbook-sentinel-0.0.28.pyz"',
        '"org.opencontainers.image.version": "0.0.28"',
        'contract_validation.get("implementation_phase") == "implemented_v8"',
        '"container_retrieval_stage_metric_exact"',
        '"checkpoint": "baseline-0028"',
    ]
    v8_exact = all(marker in runtime_text for marker in markers) and all(
        marker in tests_text
        for marker in (
            "test_container_v8_prerequisite_requires_current_implementation_phase",
            '"container_retrieval_stage_metric_exact"',
        )
    )
    dockerfile_exact = (ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines() == EXPECTED_V8_DOCKERFILE_LINES
    dockerignore_exact = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines() == EXPECTED_V8_DOCKERIGNORE_LINES
    v8_exact = v8_exact and dockerfile_exact and dockerignore_exact
    if v8_exact:
        return "implemented_v8"
    if v7_exact:
        expect(not require, "v8 identity implementation is required", errors)
        return "frozen_v7_preimplementation"
    expect(False, "container verifier or tests do not match frozen v7 or required v8 implementation", errors)
    return "nonconforming"


def validate_receipt(contract: dict, receipt_path: Path, require: bool, errors: list[str]) -> str:
    if not receipt_path.exists():
        expect(not require, "container verification receipt is required", errors)
        return "absent"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expect(receipt.get("schema_version") == "1.0", "receipt schema mismatch", errors)
    expect(receipt.get("checkpoint") == "baseline-0028", "receipt checkpoint mismatch", errors)
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
    expect(SUPERSEDED_V7_CONTRACT.is_file(), "superseded v7 contract is missing", errors)
    v7_raw = SUPERSEDED_V7_CONTRACT.read_bytes() if SUPERSEDED_V7_CONTRACT.is_file() else b"{}\n"
    expect(hashlib.sha256(v7_raw).hexdigest() == EXPECTED_V7_CONTRACT_SHA256, "superseded v7 contract bytes changed", errors)
    v7_contract = json.loads(v7_raw)
    validate_v7_contract(v7_contract, v7_raw, errors)
    expect(SUPERSEDED_V6_CONTRACT.is_file(), "superseded v6 contract is missing", errors)
    v6_raw = SUPERSEDED_V6_CONTRACT.read_bytes() if SUPERSEDED_V6_CONTRACT.is_file() else b"{}\n"
    expect(hashlib.sha256(v6_raw).hexdigest() == EXPECTED_V6_CONTRACT_SHA256, "superseded v6 contract bytes changed", errors)
    v6_contract = json.loads(v6_raw)
    validate_v6_contract(v6_contract, v6_raw, errors)
    expect(SUPERSEDED_V5_CONTRACT.is_file(), "superseded v5 contract is missing", errors)
    v5_raw = SUPERSEDED_V5_CONTRACT.read_bytes() if SUPERSEDED_V5_CONTRACT.is_file() else b"{}\n"
    expect(hashlib.sha256(v5_raw).hexdigest() == EXPECTED_V5_CONTRACT_SHA256, "superseded v5 contract bytes changed", errors)
    v5_contract = json.loads(v5_raw)
    validate_v5_contract(v5_contract, v5_raw, errors)
    expect(SUPERSEDED_V4_CONTRACT.is_file(), "superseded v4 contract is missing", errors)
    v4_raw = SUPERSEDED_V4_CONTRACT.read_bytes() if SUPERSEDED_V4_CONTRACT.is_file() else b"{}\n"
    expect(hashlib.sha256(v4_raw).hexdigest() == EXPECTED_V4_CONTRACT_SHA256, "superseded v4 contract bytes changed", errors)
    v4_contract = json.loads(v4_raw)
    validate_v4_contract(v4_contract, v4_raw, errors)
    validate_source_gate(v4_contract, errors)
    validate_v5_source_gate(v5_contract, errors)
    validate_v6_source_gate(v6_contract, errors)
    validate_v7_source_gate(v7_contract, errors)
    validate_reproducibility_inputs(v4_contract, errors)
    validate_v5_implementation(True, errors)
    validate_v6_implementation(True, errors)
    validate_v7_implementation(True, errors)
    phase = validate_v8_implementation(args.require_implementation, errors)
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
