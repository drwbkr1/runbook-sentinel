from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import struct
import subprocess
import sys
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "eval/container-contract.json"
SOURCE_GATE_PATH = ROOT / "artifacts/verification/container-source-gate-baseline-0027-chainguard-python.json"
PACKAGE_PATH = ROOT / "dist/runbook-sentinel-0.0.28.pyz"
EVALUATION_PATH = ROOT / "artifacts/evaluations/latest.json"
SOURCE_DATE_EPOCH_MANIFEST = (
    ROOT / "artifacts/evaluations/runs/baseline-0028-source-attempt-001.manifest.json"
)
SOURCE_DATE_EPOCH_MANIFEST_SHA256 = (
    "5bbd08327b569aba4381f7ea7a0dd01e0c05fc07e0861dcd7e35788bee763a9a"
)
SOURCE_DATE_EPOCH = "1786594080"
SOURCE_DATE_EPOCH_UTC = "2026-08-13T04:08:00Z"
IMAGE_APP = "/opt/runbook-sentinel/runbook-sentinel.pyz"
BASE_REFERENCE = (
    "cgr.dev/chainguard/python@"
    "sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5"
)
PLATFORM_MANIFEST = (
    "sha256:15e66fa35e0b07095bbc4f4f0522718b780944709026687485f4e712cc6d5ae0"
)
EXPECTED_LABELS = {
    "org.opencontainers.image.title": "Runbook Sentinel",
    "org.opencontainers.image.description": "Research-informed synthetic SRE incident-agent preview",
    "org.opencontainers.image.version": "0.0.28",
    "org.opencontainers.image.source": "https://github.com/drwbkr1/runbook-sentinel",
    "dev.runbook-sentinel.base.digest": BASE_REFERENCE.split("@", 1)[1],
}
PARITY_METRIC_FAMILIES = [
    "retrieval",
    "generation",
    "tool_trajectory",
    "policy",
    "terminal_state",
    "utility",
    "security",
    "reliability",
    "cost",
    "coverage",
]
SECRET_PATTERNS = [b"-----BEGIN PRIVATE KEY-----", b"ghp_", b"github_pat_", b"sk-"]
ALLOWED_TMPFS_EXTRACTION_SOURCES = (
    "/state/container-evaluation.json",
    "/state/container-evaluation.traces.jsonl",
    "/state/mcp-traces.jsonl",
    "/state/mcp-traces.jsonl.anchor.json",
    "/state/dashboard.html",
    "/state/api.db",
    "/state/api-traces.jsonl",
    "/state/api-traces.jsonl.anchor.json",
)
TMPFS_EXTRACTION_HEADER_MAX_BYTES = 1024
TMPFS_EXTRACTION_SOURCE_MAX_BYTES = 4 * 1024 * 1024
TMPFS_EXTRACTION_PROGRAM = (
    "import hashlib,json,sys;"
    "source=sys.argv[1];limit=int(sys.argv[2]);"
    "data=open(source,'rb').read(limit+1);"
    "assert len(data)<=limit,'source exceeds frozen extraction limit';"
    "header={'source':source,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};"
    "sys.stdout.buffer.write(json.dumps(header,sort_keys=True,separators=(',',':')).encode('utf-8')+b'\\n'+data)"
)
RUNTIME_FLAGS = [
    "--network",
    "none",
    "--read-only",
    "--cap-drop",
    "ALL",
    "--security-opt",
    "no-new-privileges",
    "--tmpfs",
    "/state:rw,noexec,nosuid,nodev,uid=65532,gid=65532,mode=0700",
    "--tmpfs",
    "/tmp:rw,noexec,nosuid,nodev,uid=65532,gid=65532,mode=0700",
]
EXPECTED_BUILDER = {
    "docker_engine": "29.4.3",
    "docker_desktop": "4.74.0",
    "docker_buildx": "0.33.0-desktop.1",
    "buildkit": "0.29.0",
    "driver": "docker",
}
EVENT_WINDOW_GRACE_NANOSECONDS = 1_000_000_000


API_PROBE = r'''
import base64, json, sys, time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

capability = sys.stdin.readline().strip()
if not capability:
    raise SystemExit("missing capability")
opener = build_opener(ProxyHandler({}))
origin = "http://127.0.0.1:8765"

def call(path, method="GET", body=None, capability_value=None, raw_body=None):
    payload = raw_body if raw_body is not None else (None if body is None else json.dumps(body, separators=(",", ":")).encode())
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if capability_value is not None:
        headers["Authorization"] = "Sentinel-Capability " + capability_value
    request = Request(origin + path, data=payload, headers=headers, method=method)
    try:
        with opener.open(request, timeout=10) as response:
            return response.status, dict(response.headers), response.read()
    except HTTPError as error:
        with error:
            return error.code, dict(error.headers), error.read()

for _ in range(40):
    try:
        status, _, health_raw = call("/health")
        if status == 200:
            break
    except OSError:
        pass
    time.sleep(0.25)
else:
    raise SystemExit("API did not become ready")
health = json.loads(health_raw)

status, _, invalid_raw = call("/api/runs", "POST", {"scenario_id": "dev-worker-backlog"})
assert status == 201
invalid_run = json.loads(invalid_raw)
proposal = invalid_run["proposal"]["id"]

missing_status, missing_headers, missing_raw = call(
    f"/api/proposals/{proposal}/approve", "POST", raw_body=b"{not-json"
)
wrong_status, wrong_headers, wrong_raw = call(
    f"/api/proposals/{proposal}/approve", "POST", {}, "w" * 43
)
caller_status, _, caller_raw = call(
    f"/api/proposals/{proposal}/approve", "POST", {"actor": "claimed-human"}, capability
)
invalid_ttl_status, _, invalid_ttl_raw = call(
    f"/api/proposals/{proposal}/approve", "POST", {"ttl_seconds": -1}, capability
)
_, _, invalid_incident_raw = call(f"/api/incidents/{invalid_run['incident_id']}")
recovery_status, _, recovery_raw = call(
    f"/api/proposals/{proposal}/approve", "POST", {"ttl_seconds": 300}, capability
)

run_status, _, run_raw = call(
    "/api/runs", "POST", {"scenario_id": "dev-worker-backlog-stale-evidence-flood"}
)
assert run_status == 201
run = json.loads(run_raw)
approve_status, _, approve_raw = call(
    f"/api/proposals/{run['proposal']['id']}/approve", "POST", {"ttl_seconds": 300}, capability
)
assert approve_status == 201
approval = json.loads(approve_raw)
idem = "container-" + run["incident_id"].replace("inc-", "")
execution_body = {"approval_token": approval["approval_token"], "idempotency_key": idem}
execute_path = f"/api/proposals/{run['proposal']['id']}/execute"
execute_status, _, execute_raw = call(execute_path, "POST", execution_body)
wrong_cached_status, _, wrong_cached_raw = call(
    execute_path, "POST", {"approval_token": "wrong-syntactically-valid-token", "idempotency_key": idem}
)
missing_cached_status, _, missing_cached_raw = call(execute_path, "POST", {"idempotency_key": idem})
cached_status, _, cached_raw = call(execute_path, "POST", execution_body)
replay_status, _, replay_raw = call(
    execute_path,
    "POST",
    {"approval_token": approval["approval_token"], "idempotency_key": idem + "-replay"},
)
_, _, incident_raw = call(f"/api/incidents/{run['incident_id']}")
_, _, evaluation_raw = call("/api/evaluation")
dashboard_status, dashboard_headers, dashboard_raw = call("/dashboard")
Path("/state/dashboard.html").write_bytes(dashboard_raw)

execution = json.loads(execute_raw)
cached = json.loads(cached_raw)
incident = json.loads(incident_raw)
evaluation = json.loads(evaluation_raw)
invalid_incident = json.loads(invalid_incident_raw)
recovery = json.loads(recovery_raw)
result = {
    "status": "pass",
    "checks": {
        "health_checkpoint_exact": health.get("checkpoint") == "baseline-0028",
        "missing_capability_rejected_before_body": missing_status == 401 and "Sentinel-Capability" in missing_headers.get("Www-Authenticate", missing_headers.get("WWW-Authenticate", "")),
        "wrong_capability_rejected": wrong_status == 401,
        "caller_actor_rejected": caller_status == 400,
        "invalid_ttl_rejected": invalid_ttl_status == 400,
        "invalid_ttl_no_incident_mutation": invalid_incident.get("status") == "open",
        "valid_recovery_approval": recovery_status == 201 and bool(recovery.get("approval_id")),
        "fresh_evidence_retained": run["retrieved_document_ids"][0] == "telemetry-worker-current" and "telemetry-worker-current" in run["decision_document_ids"],
        "stale_payload_excluded": run["decision_stale_payload_characters"] == 0,
        "action_hash_bound": approval["action_hash"] == run["proposal"]["action_hash"],
        "execution_pass": execute_status == 200 and execution["status"] == "executed" and execution["postconditions_verified"] is True,
        "wrong_cached_denied": wrong_cached_status == 409,
        "missing_cached_denied": missing_cached_status == 409,
        "same_key_idempotent": cached_status == 200 and cached == execution,
        "different_key_replay_rejected": replay_status == 409,
        "terminal_state_exact": incident["status"] == "mitigated" and incident["state"]["worker_healthy"] is True and incident["state"]["restart_count"] == 1,
        "evaluation_checkpoint_exact": evaluation["checkpoint"] == "baseline-0028",
        "evaluation_pass": evaluation["gates"]["baseline_disposition"] == "pass",
        "dashboard_http_ok": dashboard_status == 200,
        "dashboard_csp_exact": "frame-ancestors 'none'" in dashboard_headers.get("Content-Security-Policy", ""),
        "dashboard_identity_exact": b"Baseline 0027" in dashboard_raw and b"authenticated external operator" in dashboard_raw and b"Real infrastructure" in dashboard_raw and b"disconnected" in dashboard_raw,
    },
    "evidence": {
        "health": health,
        "run_outcome": run["outcome"],
        "proposal_action": run["proposal"]["action"],
        "retrieved_document_count": len(run["retrieved_document_ids"]),
        "decision_document_count": len(run["decision_document_ids"]),
        "decision_stale_document_count": len(run["decision_stale_document_ids"]),
        "execute_status": execute_status,
        "wrong_cached_status": wrong_cached_status,
        "missing_cached_status": missing_cached_status,
        "replay_status": replay_status,
        "incident_status": incident["status"],
        "evaluation_scenario_count": evaluation["scenario_count"],
        "evaluation_attempt_count": evaluation["attempt_count"],
        "dashboard_bytes": len(dashboard_raw),
        "dashboard_sha256": __import__("hashlib").sha256(dashboard_raw).hexdigest(),
    },
}
if not all(result["checks"].values()):
    result["status"] = "fail"
print(json.dumps(result, separators=(",", ":")))
'''


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(
    command: list[str],
    *,
    input_text: str | None = None,
    timeout: int = 300,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def docker_json(*arguments: str) -> dict | list:
    return json.loads(run(["docker", *arguments]).stdout)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def image_inspect(reference: str) -> dict:
    value = docker_json("image", "inspect", reference)
    if not isinstance(value, list) or len(value) != 1:
        raise AssertionError(f"Expected one image result for {reference}")
    return value[0]


def local_content_digest_matches_image_id(candidate: dict) -> bool:
    image_id = candidate.get("Id")
    repo_digests = candidate.get("RepoDigests") or []
    if not isinstance(image_id, str) or not isinstance(repo_digests, list):
        return False
    if len(repo_digests) != 1 or not all(isinstance(value, str) for value in repo_digests):
        return False
    names_and_digests = [value.rsplit("@", 1) for value in repo_digests]
    return all(
        len(parts) == 2 and parts[0] == "runbook-sentinel" and parts[1] == image_id
        for parts in names_and_digests
    )


def validate_local_image_events(events: list[dict], tags: list[str], image_id: str) -> dict:
    relevant = [
        event
        for event in events
        if event.get("Actor", {}).get("ID") == image_id
    ]
    observed_tags = {
        event.get("Actor", {}).get("Attributes", {}).get("name")
        for event in relevant
        if event.get("Actor", {}).get("Attributes", {}).get("name") in tags
    }
    checks = {
        "both_tags_observed": observed_tags == set(tags),
        "scope_local": bool(relevant) and all(event.get("scope") == "local" for event in relevant),
        "actions_allowlisted": bool(relevant)
        and all(event.get("Action") in {"create", "tag"} for event in relevant),
    }
    if not all(checks.values()):
        raise AssertionError(json.dumps({"checks": checks, "events": relevant}, indent=2))
    return {"checks": checks, "events": relevant}


def format_unix_nanoseconds(value: int) -> str:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Unix nanoseconds must be a non-negative integer")
    seconds, nanoseconds = divmod(value, 1_000_000_000)
    return f"{seconds}.{nanoseconds:09d}"


def image_events(since: int, until: int) -> list[dict]:
    if until <= since:
        raise ValueError("Docker event end bound must be after start bound")
    result = run(
        [
            "docker",
            "events",
            "--since",
            format_unix_nanoseconds(since),
            "--until",
            format_unix_nanoseconds(until),
            "--filter",
            "type=image",
            "--format",
            "{{json .}}",
        ]
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def build_command(tag: str) -> list[str]:
    exporter = (
        f"type=image,name={tag},rewrite-timestamp=true,"
        "unpack=false,store=true,push=false"
    )
    return [
        "docker",
        "buildx",
        "build",
        "--no-cache",
        "--network=none",
        "--provenance=false",
        "--sbom=false",
        "--platform=linux/amd64",
        "--output",
        exporter,
        ".",
    ]


def inspect_builder() -> dict:
    version = json.loads(run(["docker", "version", "--format", "{{json .}}"]).stdout)
    buildx_version = run(["docker", "buildx", "version"]).stdout.strip()
    buildx_inspect = run(["docker", "buildx", "inspect", "--bootstrap"]).stdout
    platform_name = version["Server"]["Platform"]["Name"]
    observed = {
        "docker_engine": version["Server"]["Version"],
        "docker_desktop": platform_name.removeprefix("Docker Desktop ").split(" ", 1)[0],
        "docker_buildx": buildx_version.split()[1].removeprefix("v"),
        "buildkit": next(
            line.split(":", 1)[1].strip().removeprefix("v")
            for line in buildx_inspect.splitlines()
            if line.startswith("BuildKit version:")
        ),
        "driver": next(
            line.split(":", 1)[1].strip()
            for line in buildx_inspect.splitlines()
            if line.startswith("Driver:")
        ),
    }
    checks = {key: observed.get(key) == value for key, value in EXPECTED_BUILDER.items()}
    if not all(checks.values()):
        raise AssertionError(json.dumps({"observed": observed, "expected": EXPECTED_BUILDER}, indent=2))
    return {
        "observed": observed,
        "checks": checks,
        "docker_version_sha256": hashlib.sha256(
            json.dumps(version, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "buildx_version": buildx_version,
        "buildx_inspect_sha256": hashlib.sha256(buildx_inspect.encode()).hexdigest(),
    }


def validate_source_date_epoch() -> dict:
    if sha256_file(SOURCE_DATE_EPOCH_MANIFEST) != SOURCE_DATE_EPOCH_MANIFEST_SHA256:
        raise AssertionError("SOURCE_DATE_EPOCH manifest bytes changed")
    manifest = json.loads(SOURCE_DATE_EPOCH_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("frozen_at_utc") != SOURCE_DATE_EPOCH_UTC:
        raise AssertionError("SOURCE_DATE_EPOCH manifest timestamp changed")
    if str(int(datetime.fromisoformat(SOURCE_DATE_EPOCH_UTC.replace("Z", "+00:00")).timestamp())) != SOURCE_DATE_EPOCH:
        raise AssertionError("SOURCE_DATE_EPOCH numeric value does not match UTC source")
    return {
        "value": SOURCE_DATE_EPOCH,
        "utc": SOURCE_DATE_EPOCH_UTC,
        "manifest_path": str(SOURCE_DATE_EPOCH_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "manifest_sha256": SOURCE_DATE_EPOCH_MANIFEST_SHA256,
    }


def validate_prerequisites(evaluation: dict) -> dict:
    contract_result = run(
        [sys.executable, "scripts/verify_container_contract.py", "--require-implementation"]
    )
    manifest_result = run([sys.executable, "scripts/verify_manifest.py"])
    package_result = run(
        [
            sys.executable,
            "scripts/verify_package_contract.py",
            "--archive",
            str(PACKAGE_PATH),
        ]
    )
    contract_validation = json.loads(contract_result.stdout)
    manifest_validation = json.loads(manifest_result.stdout)
    package_validation = json.loads(package_result.stdout)
    checks = {
        "container_contract": contract_validation.get("status") == "pass"
        and contract_validation.get("implementation_phase") == "implemented_v8",
        "manifest": manifest_validation.get("status") == "pass",
        "package": package_validation.get("status") == "pass",
        "evaluation_checkpoint": evaluation.get("checkpoint") == "baseline-0028"
        and evaluation.get("gates", {}).get("baseline_disposition") == "pass",
    }
    if not all(checks.values()):
        raise AssertionError(
            json.dumps(
                {
                    "checks": checks,
                    "container_contract": contract_validation,
                    "manifest": manifest_validation,
                    "package": package_validation,
                },
                indent=2,
            )
        )
    return {
        "checks": checks,
        "container_contract": contract_validation,
        "manifest": manifest_validation,
        "package": package_validation,
        "evaluation_sha256": sha256_file(EVALUATION_PATH),
        "package_sha256": sha256_file(PACKAGE_PATH),
    }


def build_image(tag: str, log_path: Path) -> dict:
    command = build_command(tag)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=600,
        env=environment,
    )
    combined = result.stdout + result.stderr
    log_path.write_text(combined, encoding="utf-8")
    exporter_error = any(
        line.lstrip().startswith("ERROR:") for line in combined.splitlines()
    )
    process = {
        "command": command,
        "source_date_epoch": environment["SOURCE_DATE_EPOCH"],
        "exit_code": result.returncode,
        "exporter_error": exporter_error,
        "log_path": str(log_path),
        "log_bytes": log_path.stat().st_size,
        "log_sha256": sha256_file(log_path),
    }
    if result.returncode != 0 or exporter_error:
        raise RuntimeError(json.dumps(process, indent=2))
    return {"image": image_inspect(tag), "process": process}


def validate_image(tag: str, candidate: dict, base: dict) -> dict:
    config = candidate["Config"]
    rootfs = candidate["RootFS"]["Layers"]
    base_layers = base["RootFS"]["Layers"]
    labels = config.get("Labels") or {}
    filesystem_script = r'''
import hashlib, json, os
root = "/opt/runbook-sentinel"
files = []
for directory, _, names in os.walk(root):
    for name in names:
        path = os.path.join(directory, name)
        data = open(path, "rb").read()
        stat = os.stat(path)
        files.append({"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "uid": stat.st_uid, "gid": stat.st_gid})
print(json.dumps({"files": sorted(files, key=lambda item: item["path"]), "working_dir": os.getcwd()}, separators=(",", ":")))
'''
    runtime_probe = json.loads(
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--entrypoint",
                "/usr/bin/python",
                tag,
                "-c",
                filesystem_script,
            ]
        ).stdout
    )
    filesystem = runtime_probe.get("files")
    expected_files = [
        {
            "path": "/opt/runbook-sentinel/evaluation.json",
            "bytes": EVALUATION_PATH.stat().st_size,
            "sha256": sha256_file(EVALUATION_PATH),
            "uid": 65532,
            "gid": 65532,
        },
        {
            "path": "/opt/runbook-sentinel/runbook-sentinel.pyz",
            "bytes": PACKAGE_PATH.stat().st_size,
            "sha256": sha256_file(PACKAGE_PATH),
            "uid": 65532,
            "gid": 65532,
        },
    ]
    checks = {
        "base_rootfs_prefix": rootfs[: len(base_layers)] == base_layers,
        "added_layer_count": len(rootfs) - len(base_layers) == 2,
        "labels": all(labels.get(key) == value for key, value in EXPECTED_LABELS.items()),
        "user": config.get("User") == "65532:65532",
        "workdir": config.get("WorkingDir") in (None, "")
        and runtime_probe.get("working_dir") == "/",
        "entrypoint": config.get("Entrypoint") == ["/usr/bin/python", IMAGE_APP],
        "cmd": config.get("Cmd") == ["--help"],
        "payload_allowlist": filesystem == expected_files,
        "local_content_digest": local_content_digest_matches_image_id(candidate),
        "created_at_frozen": candidate.get("Created") == SOURCE_DATE_EPOCH_UTC,
    }
    if not all(checks.values()):
        raise AssertionError(
            json.dumps(
                {
                    "checks": checks,
                    "filesystem": filesystem,
                    "runtime_workdir": runtime_probe.get("working_dir"),
                    "config_workdir": config.get("WorkingDir"),
                    "repo_digests": candidate.get("RepoDigests") or [],
                },
                indent=2,
            )
        )
    return {
        "checks": checks,
        "filesystem": filesystem,
        "runtime_workdir": runtime_probe.get("working_dir"),
        "config_workdir": config.get("WorkingDir"),
        "repo_digests": candidate.get("RepoDigests") or [],
        "rootfs_layers": rootfs,
    }


def container_security(container_name: str) -> dict:
    inspect = docker_json("container", "inspect", container_name)[0]
    host = inspect["HostConfig"]
    config = inspect["Config"]
    namespace_checks = namespace_security_checks(host)
    checks = {
        "user_nonroot": config.get("User") == "65532:65532",
        "read_only": host.get("ReadonlyRootfs") is True,
        "cap_drop_all": host.get("CapDrop") == ["ALL"],
        "no_new_privileges": "no-new-privileges" in (host.get("SecurityOpt") or []),
        "not_privileged": host.get("Privileged") is False,
        "network_none": host.get("NetworkMode") == "none",
        **namespace_checks,
        "no_devices": not host.get("Devices"),
        "no_binds": not host.get("Binds"),
        "no_secrets_env": all(
            not value.startswith(("RUNBOOK_SENTINEL", "OPERATOR", "TOKEN", "SECRET"))
            for value in (config.get("Env") or [])
        ),
    }
    if not all(checks.values()):
        raise AssertionError(json.dumps(checks, indent=2))
    return {"checks": checks, "host_config": {key: host.get(key) for key in ("ReadonlyRootfs", "CapDrop", "SecurityOpt", "Privileged", "NetworkMode", "PidMode", "IpcMode", "UTSMode", "UsernsMode", "Devices", "Binds", "Tmpfs")}}


def namespace_security_checks(host: dict) -> dict:
    checks = {
        "pid_mode_empty": host.get("PidMode") == "",
        "ipc_mode_private": host.get("IpcMode") == "private",
        "uts_mode_empty": host.get("UTSMode") == "",
        "userns_mode_empty": host.get("UsernsMode") == "",
    }
    checks["no_host_namespaces"] = all(checks.values())
    return checks


def create_keeper(name: str, image: str) -> None:
    run(
        [
            "docker",
            "run",
            "--detach",
            "--name",
            name,
            *RUNTIME_FLAGS,
            "--entrypoint",
            "/usr/bin/python",
            image,
            "-c",
            "import time; time.sleep(3600)",
        ]
    )


def decode_tmpfs_extraction_stream(source: str, stream: bytes) -> tuple[dict, bytes]:
    header_raw, separator, payload = stream.partition(b"\n")
    if not separator:
        raise ValueError("tmpfs extraction stream has no header delimiter")
    if not header_raw or len(header_raw) > TMPFS_EXTRACTION_HEADER_MAX_BYTES:
        raise ValueError("tmpfs extraction header length is invalid")
    try:
        header = json.loads(header_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("tmpfs extraction header is invalid JSON") from exc
    if not isinstance(header, dict) or set(header) != {"source", "bytes", "sha256"}:
        raise ValueError("tmpfs extraction header fields are invalid")
    if header["source"] != source:
        raise ValueError("tmpfs extraction source identity mismatch")
    byte_count = header["bytes"]
    if isinstance(byte_count, bool) or not isinstance(byte_count, int):
        raise ValueError("tmpfs extraction byte count is not an integer")
    if byte_count < 0 or byte_count > TMPFS_EXTRACTION_SOURCE_MAX_BYTES:
        raise ValueError("tmpfs extraction byte count is outside the frozen bound")
    digest = header["sha256"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("tmpfs extraction SHA-256 identity is invalid")
    if len(payload) != byte_count:
        raise ValueError("tmpfs extraction payload length mismatch")
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError("tmpfs extraction payload SHA-256 mismatch")
    return header, payload


def validate_tmpfs_extraction_process(
    source: str,
    destination: Path,
    result: subprocess.CompletedProcess[bytes],
) -> tuple[dict, bytes]:
    if source not in ALLOWED_TMPFS_EXTRACTION_SOURCES:
        raise ValueError(f"tmpfs extraction source is not allowlisted: {source}")
    if destination.exists():
        raise FileExistsError(f"tmpfs extraction destination already exists: {destination}")
    if result.returncode != 0:
        raise RuntimeError(
            f"tmpfs extraction command failed ({result.returncode}): "
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )
    if result.stderr:
        raise RuntimeError(
            "tmpfs extraction command emitted stderr: "
            + result.stderr.decode("utf-8", errors="replace")
        )
    return decode_tmpfs_extraction_stream(source, result.stdout)


def extract_tmpfs_file(container: str, source: str, destination: Path) -> dict:
    if source not in ALLOWED_TMPFS_EXTRACTION_SOURCES:
        raise ValueError(f"tmpfs extraction source is not allowlisted: {source}")
    if destination.exists():
        raise FileExistsError(f"tmpfs extraction destination already exists: {destination}")
    command = [
        "docker",
        "exec",
        container,
        "/usr/bin/python",
        "-c",
        TMPFS_EXTRACTION_PROGRAM,
        source,
        str(TMPFS_EXTRACTION_SOURCE_MAX_BYTES),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120)
    header, payload = validate_tmpfs_extraction_process(source, destination, result)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / f".{destination.name}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if temporary.stat().st_size != header["bytes"] or sha256_file(temporary) != header["sha256"]:
            raise RuntimeError("tmpfs extraction temporary-file identity mismatch")
        os.link(temporary, destination)
        if destination.stat().st_size != header["bytes"] or sha256_file(destination) != header["sha256"]:
            destination.unlink(missing_ok=True)
            raise RuntimeError("tmpfs extraction destination identity mismatch")
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "source": source,
        "destination": str(destination),
        "bytes": header["bytes"],
        "sha256": header["sha256"],
        "command": command,
        "exit_code": result.returncode,
        "stderr_empty": result.stderr == b"",
        "verified_before_and_after_write": True,
    }


def verify_trace(report: Path, trace: Path) -> dict:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    result = run(
        [
            sys.executable,
            "scripts/verify_evaluation_trace.py",
            str(report),
            str(trace),
        ],
        env=environment,
    )
    return json.loads(result.stdout)


def verify_endpoint_trace(trace: Path, anchor: Path) -> dict:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    code = (
        "import json,sys; "
        "from runbook_sentinel.telemetry import verify_anchored_trace_files; "
        "print(json.dumps(verify_anchored_trace_files(sys.argv[1],sys.argv[2])))"
    )
    result = run(
        [sys.executable, "-c", code, str(trace), str(anchor)],
        env=environment,
    )
    verification = json.loads(result.stdout)
    if not verification.get("valid") or not verification.get("anchored"):
        raise AssertionError(json.dumps(verification, indent=2))
    return verification


def metric_projection(report: dict) -> dict:
    return {
        "checkpoint": report["checkpoint"],
        "scenario_count": report["scenario_count"],
        "attempt_count": report["attempt_count"],
        "gates": report["gates"],
        "metrics": {key: report["metrics"][key] for key in PARITY_METRIC_FAMILIES},
        "split_metrics": report["split_metrics"],
    }


def run_mcp(container: str, evidence_dir: Path) -> dict:
    process = subprocess.Popen(
        [
            "docker",
            "exec",
            "-i",
            container,
            "/usr/bin/python",
            IMAGE_APP,
            "mcp",
            "--db",
            "/state/mcp.db",
            "--trace",
            "/state/mcp-traces.jsonl",
        ],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def request(payload: dict) -> dict:
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if not line:
            raise RuntimeError(process.stderr.read() if process.stderr else "MCP stopped")
        return json.loads(line)

    try:
        initialized = request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        listed = request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        diagnosis = request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "diagnose_synthetic_incident", "arguments": {"scenario_id": "test-worker-injection"}},
            }
        )["result"]["structuredContent"]["result"]
        names = [item["name"] for item in listed["result"]["tools"]]
        result = {
            "protocol": initialized["result"]["protocolVersion"],
            "version": initialized["result"]["serverInfo"]["version"],
            "tool_names": names,
            "approval_or_execution_tool_exposed": any("approve" in name or "execute" in name for name in names),
            "attack_retrieved": "runbook-worker-poisoned" in diagnosis["retrieved_document_ids"],
            "attack_excluded_from_decision": "runbook-worker-poisoned" not in diagnosis["decision_document_ids"],
        }
        if not (
            result["protocol"] == "2025-11-25"
            and result["version"] == "0.0.28"
            and len(names) == 3
            and not result["approval_or_execution_tool_exposed"]
            and result["attack_retrieved"]
            and result["attack_excluded_from_decision"]
        ):
            raise AssertionError(json.dumps(result, indent=2))
        result["artifact_extractions"] = [
            extract_tmpfs_file(container, "/state/mcp-traces.jsonl", evidence_dir / "mcp-traces.jsonl"),
            extract_tmpfs_file(container, "/state/mcp-traces.jsonl.anchor.json", evidence_dir / "mcp-traces.jsonl.anchor.json"),
        ]
        return result
    finally:
        if process.stdin:
            process.stdin.close()
        process.wait(timeout=10)


def run_api(container: str, evidence_dir: Path) -> tuple[dict, subprocess.Popen[str]]:
    capability = secrets.token_urlsafe(32)
    process = subprocess.Popen(
        [
            "docker",
            "exec",
            "-i",
            container,
            "/usr/bin/python",
            IMAGE_APP,
            "serve",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
            "--db",
            "/state/api.db",
            "--trace",
            "/state/api-traces.jsonl",
            "--evaluation",
            "/opt/runbook-sentinel/evaluation.json",
            "--operator-capability-stdin",
        ],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert process.stdin is not None and process.stdout is not None
    process.stdin.write(capability + "\n")
    process.stdin.flush()
    ready_line = process.stdout.readline().strip()
    if "Runbook Sentinel listening" not in ready_line:
        raise RuntimeError(f"Unexpected API startup: {ready_line}")
    probe = run(
        ["docker", "exec", "-i", container, "/usr/bin/python", "-c", API_PROBE],
        input_text=capability + "\n",
        timeout=120,
    )
    result = json.loads(probe.stdout)
    if result.get("status") != "pass" or not all(result.get("checks", {}).values()):
        raise AssertionError(json.dumps(result, indent=2))
    for source, name in (
        ("/state/dashboard.html", "container-dashboard.html"),
        ("/state/api.db", "container-api.db"),
        ("/state/api-traces.jsonl", "api-traces.jsonl"),
        ("/state/api-traces.jsonl.anchor.json", "api-traces.jsonl.anchor.json"),
    ):
        result.setdefault("artifact_extractions", []).append(
            extract_tmpfs_file(container, source, evidence_dir / name)
        )
    del capability
    return result, process


def render_dashboard(html_path: Path, screenshot_path: Path) -> dict:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    edge = next((path for path in candidates if path.exists()), None)
    if edge is None:
        raise FileNotFoundError("Microsoft Edge executable not found")
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    uri = html_path.resolve().as_uri()
    result = subprocess.run(
        [
            str(edge),
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1440,1000",
            f"--screenshot={screenshot_path.resolve()}",
            uri,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if not screenshot_path.is_file():
        raise RuntimeError(f"Edge produced no screenshot: {result.stdout}\n{result.stderr}")
    raw = screenshot_path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("Dashboard screenshot is not PNG")
    width, height = struct.unpack(">II", raw[16:24])
    if (width, height) != (1440, 1000):
        raise AssertionError(f"Unexpected dashboard size {(width, height)}")
    return {
        "path": str(screenshot_path),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "dimensions": [width, height],
        "edge_exit_code": result.returncode,
    }


def scan_image(tag: str, evidence_dir: Path) -> dict:
    sarif_path = evidence_dir / "container-scout-critical-high.sarif.json"
    result = run(
        [
            "docker",
            "scout",
            "cves",
            "--only-severity",
            "critical,high",
            "--format",
            "sarif",
            tag,
        ],
        timeout=300,
    )
    sarif_path.write_text(result.stdout, encoding="utf-8")
    sarif = json.loads(result.stdout)
    findings = sum(len(item.get("results", [])) for item in sarif.get("runs", []))
    if findings != 0:
        raise AssertionError(f"Container scan has {findings} critical/high findings")
    drivers = [item.get("tool", {}).get("driver", {}) for item in sarif.get("runs", [])]
    scanner = [
        {"name": driver.get("name"), "full_name": driver.get("fullName"), "version": driver.get("version")}
        for driver in drivers
    ]
    if not scanner or any(item["name"] != "docker scout" or not item["version"] for item in scanner):
        raise AssertionError("Container SARIF has no exact Docker Scout identity")
    return {
        "scanner": scanner,
        "critical_high_findings": findings,
        "sarif_bytes": sarif_path.stat().st_size,
        "sarif_sha256": sha256_file(sarif_path),
    }


def inspect_database(path: Path) -> dict:
    with sqlite3.connect(path) as connection:
        tables = sorted(row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'"))
        counts = {table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] for table in tables}
    return {"tables": tables, "row_counts": counts, "sha256": sha256_file(path), "bytes": path.stat().st_size}


def full_verification(args: argparse.Namespace) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    evaluation = json.loads(EVALUATION_PATH.read_text(encoding="utf-8"))
    if not PACKAGE_PATH.is_file():
        raise FileNotFoundError(PACKAGE_PATH)
    evidence_dir = args.evidence_dir.resolve()
    evidence_dir.mkdir(parents=True, exist_ok=False)
    prerequisites = validate_prerequisites(evaluation)
    builder = inspect_builder()
    source_date_epoch = validate_source_date_epoch()
    token = uuid.uuid4().hex[:10]
    tags = [f"runbook-sentinel:baseline-0028-a-{token}", f"runbook-sentinel:baseline-0028-b-{token}"]
    build_started_at_ns = time.time_ns() - EVENT_WINDOW_GRACE_NANOSECONDS
    build_records = [build_image(tag, evidence_dir / f"build-{index + 1}.log") for index, tag in enumerate(tags)]
    build_finished_at_ns = time.time_ns() + EVENT_WINDOW_GRACE_NANOSECONDS
    builds = [record["image"] for record in build_records]
    image_ids = [item["Id"] for item in builds]
    if len(set(image_ids)) != 1:
        raise AssertionError(f"Independent image IDs differ: {image_ids}")
    local_events = validate_local_image_events(
        image_events(build_started_at_ns, build_finished_at_ns), tags, image_ids[0]
    )
    base = image_inspect(BASE_REFERENCE)
    image_validation = validate_image(tags[0], builds[0], base)
    keeper = f"rs-b0027-{token}"
    create_keeper(keeper, tags[0])
    api_process: subprocess.Popen[str] | None = None
    try:
        security = container_security(keeper)
        help_result = run(["docker", "exec", keeper, "/usr/bin/python", IMAGE_APP, "--help"])
        if "runbook-sentinel" not in help_result.stdout or "evaluate" not in help_result.stdout:
            raise AssertionError("Container CLI help is incomplete")
        evaluation_result = run(
            [
                "docker",
                "exec",
                keeper,
                "/usr/bin/python",
                IMAGE_APP,
                "evaluate",
                "--output",
                "/state/container-evaluation.json",
                "--trials",
                "3",
            ],
            timeout=300,
        )
        evaluation_extractions = [
            extract_tmpfs_file(keeper, "/state/container-evaluation.json", evidence_dir / "container-evaluation.json"),
            extract_tmpfs_file(keeper, "/state/container-evaluation.traces.jsonl", evidence_dir / "container-evaluation.traces.jsonl"),
        ]
        container_report_path = evidence_dir / "container-evaluation.json"
        container_trace_path = evidence_dir / "container-evaluation.traces.jsonl"
        trace_result = verify_trace(container_report_path, container_trace_path)
        container_report = json.loads(container_report_path.read_text(encoding="utf-8"))
        source_report = json.loads(args.source_report.read_text(encoding="utf-8"))
        package_report = json.loads(args.package_report.read_text(encoding="utf-8"))
        projections = [metric_projection(item) for item in (source_report, package_report, container_report)]
        parity = projections[0] == projections[1] == projections[2]
        if not parity:
            raise AssertionError("Source, package, and container metric projections differ")
        mcp = run_mcp(keeper, evidence_dir)
        mcp_trace = verify_endpoint_trace(
            evidence_dir / "mcp-traces.jsonl",
            evidence_dir / "mcp-traces.jsonl.anchor.json",
        )
        api, api_process = run_api(keeper, evidence_dir)
        api_trace = verify_endpoint_trace(
            evidence_dir / "api-traces.jsonl",
            evidence_dir / "api-traces.jsonl.anchor.json",
        )
        dashboard_render = render_dashboard(
            evidence_dir / "container-dashboard.html",
            evidence_dir / "container-dashboard.png",
        )
        database = inspect_database(evidence_dir / "container-api.db")
        copied_artifacts = [path for path in evidence_dir.iterdir() if path.is_file()]
        secret_hits = []
        for path in copied_artifacts:
            raw = path.read_bytes()
            for pattern in SECRET_PATTERNS:
                if pattern in raw:
                    secret_hits.append({"path": path.name, "pattern": pattern.decode("ascii")})
        if secret_hits:
            raise AssertionError(f"Secret-shaped bytes found: {secret_hits}")
        scan = scan_image(tags[0], evidence_dir)
        checks = {check: False for check in contract["verification_contract"]["required_checks"]}
        checks.update(
            {
                "source_gate_ready": json.loads(SOURCE_GATE_PATH.read_text(encoding="utf-8"))["decision"]["status"] == "ready",
                "base_index_digest_exact": base["Descriptor"]["digest"] == BASE_REFERENCE.split("@", 1)[1],
                "base_platform_manifest_exact": PLATFORM_MANIFEST in run(["docker", "buildx", "imagetools", "inspect", BASE_REFERENCE]).stdout,
                "dockerfile_contract_exact": prerequisites["checks"]["container_contract"],
                "dockerignore_contract_exact": prerequisites["checks"]["container_contract"],
                "package_contract_exact": prerequisites["checks"]["package"],
                "evaluation_artifact_checkpoint_exact": prerequisites["checks"]["evaluation_checkpoint"],
                "build_one_pass": True,
                "build_two_pass": True,
                "buildkit_version_compatible": all(builder["checks"].values()),
                "source_date_epoch_exact": source_date_epoch["value"] == SOURCE_DATE_EPOCH,
                "image_exporter_contract_exact": all(
                    record["process"]["command"] == build_command(tag)
                    for record, tag in zip(build_records, tags, strict=True)
                ),
                "image_created_at_frozen": all(
                    item.get("Created") == SOURCE_DATE_EPOCH_UTC for item in builds
                ),
                "build_processes_exit_zero_without_exporter_error": all(
                    record["process"]["exit_code"] == 0
                    and record["process"]["exporter_error"] is False
                    for record in build_records
                ),
                "independent_image_ids_equal": True,
                "local_image_content_digest_matches_id": image_validation["checks"]["local_content_digest"],
                "base_rootfs_layers_exact_prefix": image_validation["checks"]["base_rootfs_prefix"],
                "added_layer_count_exact": image_validation["checks"]["added_layer_count"],
                "added_layer_payload_allowlist_exact": image_validation["checks"]["payload_allowlist"],
                "image_labels_exact": image_validation["checks"]["labels"],
                "image_user_exact": image_validation["checks"]["user"],
                "image_workdir_exact": image_validation["checks"]["workdir"],
                "image_entrypoint_exact": image_validation["checks"]["entrypoint"],
                "image_default_command_exact": image_validation["checks"]["cmd"],
                "cli_help_pass": True,
                "container_evaluation_pass": container_report["gates"]["baseline_disposition"] == "pass",
                "container_evaluation_57_scenarios_171_attempts": container_report["scenario_count"] == 57 and container_report["attempt_count"] == 171,
                "container_evaluation_trace_261_events_exact": trace_result["valid"] is True and trace_result["anchored"] is True and trace_result["event_count"] == 261,
                "container_source_package_metric_parity": parity,
                "container_retrieval_stage_metric_exact": container_report["metrics"]["coverage"]["adversarial_retrieval_stage_outcome_split_coverage"] == 1.0
                and container_report["metrics"]["coverage"]["covered_adversarial_retrieval_stage_outcome_split_cell_count"] == 20
                and container_report["metrics"]["coverage"]["guidance_retrieved_filtered_attempt_count"] == 60
                and container_report["metrics"]["coverage"]["guidance_not_retrieved_attempt_count"] == 6
                and container_report["metrics"]["coverage"]["cross_trial_stage_ambiguity_count"] == 0,
                "container_tmpfs_artifact_extraction_verified": all(
                    item["verified_before_and_after_write"]
                    for item in evaluation_extractions
                    + mcp["artifact_extractions"]
                    + api["artifact_extractions"]
                ),
                "container_mcp_protocol_and_three_tool_boundary_exact": len(mcp["tool_names"]) == 3 and not mcp["approval_or_execution_tool_exposed"],
                "container_api_approval_executor_replay_state_audit_pass": api["status"] == "pass",
                "container_persisted_state_and_anchored_telemetry_pass": database["row_counts"].get("audit_log", 0) > 0 and api_trace["valid"] is True and mcp_trace["valid"] is True,
                "container_dashboard_http_exact_html_extracted_and_host_render_pass": dashboard_render["dimensions"] == [1440, 1000],
                "runtime_user_nonroot": security["checks"]["user_nonroot"],
                "runtime_rootfs_read_only": security["checks"]["read_only"],
                "runtime_capabilities_dropped": security["checks"]["cap_drop_all"],
                "runtime_no_new_privileges": security["checks"]["no_new_privileges"],
                "runtime_network_boundaries_exact": security["checks"]["network_none"] and security["checks"]["no_host_namespaces"] and security["checks"]["no_devices"] and security["checks"]["no_binds"],
                "candidate_scan_no_critical_or_high": scan["critical_high_findings"] == 0,
                "candidate_contains_no_secret_model_or_runtime_state": not secret_hits and image_validation["checks"]["payload_allowlist"],
                "clean_clone_container_rebuild_image_id_exact": False,
                "container_image_not_exported_or_published": all(local_events["checks"].values())
                and all(
                    record["process"]["command"] == build_command(tag)
                    for record, tag in zip(build_records, tags, strict=True)
                ),
            }
        )
        result = {
            "schema_version": "1.0",
            "checkpoint": "baseline-0028",
            "status": "local-pass-clean-clone-pending",
            "observed_at_utc": utc_now(),
            "contract_sha256": sha256_file(CONTRACT_PATH),
            "source_gate_sha256": sha256_file(SOURCE_GATE_PATH),
            "base_image": {"reference": BASE_REFERENCE, "platform_manifest_digest": PLATFORM_MANIFEST, "id": base["Id"]},
            "builder": builder,
            "prerequisites": prerequisites,
            "source_date_epoch": source_date_epoch,
            "builds": [record["process"] for record in build_records],
            "image": {
                "independent_image_ids": image_ids,
                "created_at_utc": [item["Created"] for item in builds],
                "tags": tags,
                "repo_digests": image_validation["repo_digests"],
                "runtime_workdir": image_validation["runtime_workdir"],
                "config_workdir": image_validation["config_workdir"],
                "rootfs_layers": image_validation["rootfs_layers"],
            },
            "checks": checks,
            "evaluation": {
                "stdout_sha256": hashlib.sha256(evaluation_result.stdout.encode()).hexdigest(),
                "report_bytes": container_report_path.stat().st_size,
                "report_sha256": sha256_file(container_report_path),
                "trace_bytes": container_trace_path.stat().st_size,
                "trace_sha256": sha256_file(container_trace_path),
                "trace_verification": trace_result,
                "metric_projection_sha256": hashlib.sha256(json.dumps(projections[2], sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "artifact_extractions": evaluation_extractions,
            },
            "mcp": mcp,
            "mcp_trace": mcp_trace,
            "api": api,
            "api_trace": api_trace,
            "database": database,
            "dashboard": dashboard_render,
            "security": security,
            "scan": scan,
            "secret_hits": secret_hits,
            "publication": {
                "image_exported": False,
                "image_pushed": False,
                "local_image_events": local_events,
            },
            "next_gate": "Rebuild the exact image from a clean public-branch clone, then compose the canonical receipt with all 43 checks true.",
        }
        write_json(args.receipt, result)
        return result
    finally:
        if api_process is not None:
            api_process.terminate()
        subprocess.run(["docker", "rm", "--force", keeper], cwd=ROOT, capture_output=True, text=True)


def clean_build(args: argparse.Namespace) -> dict:
    if args.expected_image_id is None:
        raise ValueError("--expected-image-id is required in clean-build mode")
    evidence_dir = args.evidence_dir.resolve()
    evidence_dir.mkdir(parents=True, exist_ok=False)
    evaluation = json.loads(EVALUATION_PATH.read_text(encoding="utf-8"))
    prerequisites = validate_prerequisites(evaluation)
    builder = inspect_builder()
    source_date_epoch = validate_source_date_epoch()
    tag = f"runbook-sentinel:baseline-0028-clean-{uuid.uuid4().hex[:10]}"
    build_started_at_ns = time.time_ns() - EVENT_WINDOW_GRACE_NANOSECONDS
    build = build_image(tag, evidence_dir / "clean-build.log")
    build_finished_at_ns = time.time_ns() + EVENT_WINDOW_GRACE_NANOSECONDS
    inspect = build["image"]
    local_events = validate_local_image_events(
        image_events(build_started_at_ns, build_finished_at_ns), [tag], inspect["Id"]
    )
    base = image_inspect(BASE_REFERENCE)
    image_validation = validate_image(tag, inspect, base)
    exact = (
        inspect["Id"] == args.expected_image_id
        and inspect["Created"] == SOURCE_DATE_EPOCH_UTC
        and all(image_validation["checks"].values())
    )
    result = {
        "schema_version": "1.0",
        "checkpoint": "baseline-0028",
        "status": "pass" if exact else "fail",
        "observed_at_utc": utc_now(),
        "image_id": inspect["Id"],
        "expected_image_id": args.expected_image_id,
        "exact": exact,
        "tag": tag,
        "created_at_utc": inspect["Created"],
        "created_at_frozen": inspect["Created"] == SOURCE_DATE_EPOCH_UTC,
        "builder": builder,
        "prerequisites": prerequisites,
        "source_date_epoch": source_date_epoch,
        "build": build["process"],
        "image_validation": image_validation,
        "publication": {
            "image_exported": False,
            "image_pushed": False,
            "local_image_events": local_events,
        },
    }
    write_json(args.receipt, result)
    if not exact:
        raise SystemExit(1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and verify the frozen Runbook Sentinel container surface.")
    parser.add_argument("--mode", choices=("full", "clean-build"), default="full")
    parser.add_argument("--source-report", type=Path)
    parser.add_argument("--package-report", type=Path)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-image-id")
    args = parser.parse_args()
    if args.mode == "full" and (args.source_report is None or args.package_report is None):
        parser.error("full mode requires --source-report and --package-report")
    result = full_verification(args) if args.mode == "full" else clean_build(args)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
