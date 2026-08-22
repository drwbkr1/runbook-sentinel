from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


OLD_DIGEST = "sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5"
NEW_DIGEST = "sha256:1f6779775c9f466890da563e411cb677045a6c20b6a65160eefad1deffb5012c"
NEW_MANIFEST = "sha256:e15765ff7066a0eaf91e1b6fd5000c1bba47d62b9f9731f2da560711d910c4f3"
START_COMMIT = "e12e638b98b1deacb4c5058ecb9d7c8652c96985"
SCAN_RECEIPT_SHA256 = "8c4436f7a886cd0b271ee20ffbbf3a5a537c120da635ced8095b3bfb897d5996"
AUDIT_RECEIPT_SHA256 = "f3c7191c36831e9e05b9dafb3a80dc5a1fde534ef820dfd2d2cb8234f17ac2f4"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def evaluate(root: Path, phase: str) -> dict[str, Any]:
    errors: list[str] = []
    contract_path = root / "eval/container-base-security-refresh-contract-0032.json"
    gate_path = root / "artifacts/verification/container-source-gate-baseline-0032-chainguard-python.json"
    scan_path = root / "artifacts/verification/container-scout-critical-high-baseline-0031-final-audit-failure-001.json"
    audit_path = root / "artifacts/verification/release-audit-baseline-0031-attempt-001-blocked.json"
    dockerfile_path = root / "Dockerfile"

    for path in (contract_path, gate_path, scan_path, audit_path, dockerfile_path):
        expect(path.is_file(), f"missing required path: {path.relative_to(root)}", errors)
    if errors:
        return {"valid": False, "phase": phase, "errors": errors}

    contract = load_json(contract_path)
    gate = load_json(gate_path)
    scan = load_json(scan_path)
    audit = load_json(audit_path)
    dockerfile = dockerfile_path.read_text(encoding="utf-8-sig").splitlines()

    expect(
        contract.get("schema_version") == "runbook-sentinel/container-base-security-refresh/v1",
        "contract schema mismatch",
        errors,
    )
    expect(contract.get("checkpoint") == "baseline-0032", "checkpoint mismatch", errors)
    expect(
        contract.get("contract_status") == "frozen_before_candidate_pull_or_implementation",
        "contract status mismatch",
        errors,
    )
    starting = contract.get("starting_checkpoint", {})
    expect(starting.get("public_main_commit") == START_COMMIT, "starting commit mismatch", errors)
    expect(starting.get("lifecycle") == "stopped", "predecessor must remain stopped", errors)
    expect(starting.get("v0_0_31_tag_or_release_exists") is False, "v0.0.31 must remain unpublished", errors)

    weakness = contract.get("measured_weakness", {})
    expect(weakness.get("source_base_index_digest") == OLD_DIGEST, "old base digest mismatch", errors)
    expect(weakness.get("unique_high_cves") == ["CVE-2026-14456", "CVE-2026-54876"], "HIGH CVE set mismatch", errors)
    expect(weakness.get("historical_zero_result_scan_may_satisfy_successor_gate") is False, "historical scan cannot pass successor gate", errors)
    expect(weakness.get("renewed_scan_receipt_sha256") == SCAN_RECEIPT_SHA256, "scan receipt hash contract mismatch", errors)
    expect(weakness.get("blocked_release_audit_sha256") == AUDIT_RECEIPT_SHA256, "audit receipt hash contract mismatch", errors)
    expect(sha256(scan_path) == SCAN_RECEIPT_SHA256, "retained scan receipt bytes changed", errors)
    expect(sha256(audit_path) == AUDIT_RECEIPT_SHA256, "retained blocked audit bytes changed", errors)
    expect(scan.get("status") == "fail", "retained scan receipt must remain fail", errors)
    expect(scan.get("results", {}).get("unique_vulnerability_count") == 2, "retained HIGH count mismatch", errors)
    expect(scan.get("gate", {}).get("release_allowed") is False, "failed candidate cannot become releasable", errors)
    failed_checks = [item.get("id") for item in audit.get("checks", []) if item.get("status") == "fail"]
    expect(failed_checks == ["CHECK-007"], "blocked audit failed-check set mismatch", errors)

    admitted = contract.get("admitted_source", {})
    expect(admitted.get("index_digest") == NEW_DIGEST, "admitted index digest mismatch", errors)
    expect(admitted.get("linux_amd64_manifest_digest") == NEW_MANIFEST, "admitted platform manifest mismatch", errors)
    expect(admitted.get("reference") == f"cgr.dev/chainguard/python@{NEW_DIGEST}", "mutable or unexpected source reference", errors)
    expect(admitted.get("platform") == "linux/amd64", "platform mismatch", errors)
    expect(admitted.get("user") == "65532", "non-root user mismatch", errors)
    expect(admitted.get("has_shell") is False and admitted.get("has_apk") is False, "distroless boundary mismatch", errors)
    expect(admitted.get("libcrypto3_version") == "3.6.3-r5", "libcrypto3 fixed version mismatch", errors)
    expect(admitted.get("libssl3_version") == "3.6.3-r5", "libssl3 fixed version mismatch", errors)
    remote_scan = admitted.get("remote_critical_high_scan", {})
    expect(remote_scan.get("result_count") == 0, "remote source scan is not zero", errors)
    expect(remote_scan.get("sarif_body_intrinsically_binds_target") is False, "generic SARIF target-binding limitation missing", errors)

    expect(gate.get("contract_version") == "source-gate/v1", "source gate schema mismatch", errors)
    expect(gate.get("decision", {}).get("status") == "ready", "source gate is not ready", errors)
    expect(gate.get("sources", [{}])[0].get("locator") == f"cgr.dev/chainguard/python@{NEW_DIGEST}", "source gate locator mismatch", errors)
    criteria = gate.get("sources", [{}])[0].get("criteria", [])
    expect(len(criteria) == 8, "source gate criterion count mismatch", errors)
    expect(all(item.get("status") == "pass" for item in criteria), "source gate contains a non-pass criterion", errors)
    prohibited = gate.get("write_boundary", {}).get("requires_explicit_authorization", [])
    expect(any("redistribute" in item for item in prohibited), "image redistribution boundary missing", errors)
    expect(any("real infrastructure" in item for item in prohibited), "real-infrastructure boundary missing", errors)

    bounded = contract.get("bounded_change", {})
    expect(bounded.get("new_project_dependencies") == [], "new dependencies are not allowed", errors)
    expect(bounded.get("new_model_or_retrieval_configuration") == [], "new model or retrieval configuration is not allowed", errors)
    forbidden = bounded.get("forbidden_changes", [])
    expect(any("authorization capabilities approval" in item for item in forbidden), "external enforcement boundary missing", errors)
    expect(any("frozen development or held-out splits" in item for item in forbidden), "frozen evaluation boundary missing", errors)

    old_from = f"FROM cgr.dev/chainguard/python@{OLD_DIGEST}"
    new_from = f"FROM cgr.dev/chainguard/python@{NEW_DIGEST}"
    old_label = f'LABEL dev.runbook-sentinel.base.digest="{OLD_DIGEST}"'
    new_label = f'LABEL dev.runbook-sentinel.base.digest="{NEW_DIGEST}"'
    if phase == "frozen":
        expect(dockerfile and dockerfile[0] == old_from, "preimplementation Dockerfile FROM changed", errors)
        expect(old_label in dockerfile, "preimplementation base label changed", errors)
        expect(new_from not in dockerfile and new_label not in dockerfile, "candidate digest implemented before public freeze", errors)
        expect('LABEL org.opencontainers.image.version="0.0.31"' in dockerfile, "preimplementation version identity changed", errors)
        expect(any("runbook-sentinel-0.0.31.pyz" in line for line in dockerfile), "preimplementation package identity changed", errors)
    else:
        expect(dockerfile and dockerfile[0] == new_from, "implemented Dockerfile FROM mismatch", errors)
        expect(new_label in dockerfile, "implemented base label mismatch", errors)
        expect(old_from not in dockerfile and old_label not in dockerfile, "old base digest remains active", errors)
        expect('LABEL org.opencontainers.image.version="0.0.32"' in dockerfile, "implemented version identity mismatch", errors)
        expect(any("runbook-sentinel-0.0.32.pyz" in line for line in dockerfile), "implemented package identity mismatch", errors)

    no_go = contract.get("no_go_boundaries", {})
    expect(no_go and all(value is False for value in no_go.values()), "a no-go boundary is asserted true", errors)
    return {
        "valid": not errors,
        "phase": phase,
        "checkpoint": contract.get("checkpoint"),
        "source_gate_status": gate.get("decision", {}).get("status"),
        "admitted_index_digest": admitted.get("index_digest"),
        "retained_failed_check": failed_checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the frozen BASELINE-0032 container-base security refresh contract.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--phase", choices=("frozen", "implemented"), default="frozen")
    args = parser.parse_args()
    result = evaluate(args.root.resolve(), args.phase)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
