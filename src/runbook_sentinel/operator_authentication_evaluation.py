from __future__ import annotations

import hashlib
import http.client
from importlib.resources import files
import json
import re
import secrets
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from statistics import median
from time import perf_counter
from urllib.request import urlopen

from .api import create_server
from .operator_auth import (
    AUTHENTICATION_CHALLENGE,
    AUTHENTICATION_SCHEME,
    authorization_value,
)


CONTRACT_ID = "operator-authentication-v1"
TABLES = (
    "incidents",
    "runs",
    "proposals",
    "approvals",
    "idempotency",
    "audit_log",
)


def load_contract_bytes() -> bytes:
    repository_contract = (
        Path(__file__).resolve().parents[2] / "eval/operator-authentication-contract.json"
    )
    if repository_contract.is_file():
        return repository_contract.read_bytes()
    return files("runbook_sentinel").joinpath(
        "data/operator-authentication-contract.json"
    ).read_bytes()


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _post(
    port: int,
    path: str,
    body: bytes,
    authorization_values: list[str] | None = None,
) -> tuple[int, dict, dict[str, list[str]], float]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    started = perf_counter()
    try:
        connection.putrequest("POST", path)
        connection.putheader("Content-Type", "application/json")
        connection.putheader("Content-Length", str(len(body)))
        for value in authorization_values or []:
            connection.putheader("Authorization", value)
        connection.endheaders(body)
        response = connection.getresponse()
        response_body = response.read()
        headers: dict[str, list[str]] = {}
        for name, value in response.getheaders():
            headers.setdefault(name.casefold(), []).append(value)
        elapsed_ms = (perf_counter() - started) * 1000
        return response.status, json.loads(response_body), headers, elapsed_ms
    finally:
        connection.close()


def _rows(service) -> dict[str, list[dict]]:
    with service.storage.connect() as connection:
        return {
            table: [
                dict(row)
                for row in connection.execute(
                    f"SELECT * FROM {table} ORDER BY rowid"
                ).fetchall()
            ]
            for table in TABLES
        }


def _state_fingerprint(service, trace_path: Path) -> dict:
    rows = _rows(service)
    trace_bytes = trace_path.read_bytes() if trace_path.exists() else b""
    return {
        "rows_sha256": _sha256(_canonical(rows).encode("utf-8")),
        "trace_sha256": _sha256(trace_bytes),
        "table_counts": {table: len(values) for table, values in rows.items()},
        "trace_bytes": len(trace_bytes),
    }


def _approval_observation(service, trace_path: Path, proposal_id: str) -> dict:
    with service.storage.connect() as connection:
        proposal = connection.execute(
            "SELECT status FROM proposals WHERE id = ?", (proposal_id,)
        ).fetchone()
        approvals = connection.execute(
            "SELECT actor, token_hash, created_at, expires_at, consumed_at FROM approvals WHERE proposal_id = ?",
            (proposal_id,),
        ).fetchall()
        approval_audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_log WHERE subject_id = ? AND event_type = 'proposal.approved'",
            (proposal_id,),
        ).fetchone()[0]
    trace_events = (
        [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if trace_path.exists()
        else []
    )
    approval_trace_count = sum(
        event.get("name") == "sentinel.approval"
        and event.get("attributes", {}).get("proposal.id") == proposal_id
        for event in trace_events
    )
    lifetime_seconds = None
    actor = None
    if approvals:
        actor = approvals[0]["actor"]
        lifetime_seconds = (
            datetime.fromisoformat(approvals[0]["expires_at"])
            - datetime.fromisoformat(approvals[0]["created_at"])
        ).total_seconds()
    return {
        "proposal_status": proposal["status"],
        "approval_count": len(approvals),
        "approval_audit_count": approval_audit_count,
        "approval_trace_count": approval_trace_count,
        "operator_identity": actor,
        "lifetime_seconds": lifetime_seconds,
    }


def _terminal_observation(service, trace_path: Path, proposal_id: str, incident_id: str) -> dict:
    with service.storage.connect() as connection:
        incident = connection.execute(
            "SELECT status FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        proposal = connection.execute(
            "SELECT status FROM proposals WHERE id = ?", (proposal_id,)
        ).fetchone()
        approval = connection.execute(
            "SELECT consumed_at FROM approvals WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()
        idempotency_count = connection.execute(
            "SELECT COUNT(*) FROM idempotency WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()[0]
        execution_audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_log WHERE subject_id = ? AND event_type = 'proposal.executed'",
            (proposal_id,),
        ).fetchone()[0]
    trace_events = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    execution_trace_count = sum(
        event.get("name") == "sentinel.execute"
        and event.get("attributes", {}).get("proposal.id") == proposal_id
        for event in trace_events
    )
    return {
        "incident_status": incident["status"],
        "proposal_status": proposal["status"],
        "approval_consumed": approval["consumed_at"] is not None,
        "idempotency_record_count": idempotency_count,
        "execution_audit_count": execution_audit_count,
        "execution_trace_count": execution_trace_count,
    }


def _surface_bytes(base: Path, service, trace_path: Path, response_payloads: list[dict], dashboard: bytes) -> bytes:
    parts = [_canonical(_rows(service)).encode("utf-8")]
    for suffix in ("state.db", "state.db-wal", "state.db-shm"):
        path = base / suffix
        if path.exists():
            parts.append(path.read_bytes())
    if trace_path.exists():
        parts.append(trace_path.read_bytes())
    parts.append(_canonical(response_payloads).encode("utf-8"))
    parts.append(dashboard)
    return b"\n".join(parts)


def _authorization_values(
    role: str, current: str, wrong: str, prior: str
) -> list[str]:
    if role == "missing":
        return []
    if role == "current_launch":
        return [authorization_value(current)]
    if role == "wrong_valid_shape":
        return [authorization_value(wrong)]
    if role == "bearer_current_capability":
        return [f"Bearer {current}"]
    if role == "scheme_without_value":
        return [AUTHENTICATION_SCHEME]
    if role == "duplicate_current_launch":
        return [authorization_value(current), authorization_value(current)]
    if role == "prior_launch":
        return [authorization_value(prior)]
    raise ValueError(f"Unknown authorization role: {role}")


def _run_case(case: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="sentinel-operator-auth-") as temp_dir:
        base = Path(temp_dir)
        trace_path = base / "traces.jsonl"
        current_capability = secrets.token_urlsafe(32)
        wrong_capability = secrets.token_urlsafe(32)
        prior_capability = secrets.token_urlsafe(32)
        if case["authorization"] == "prior_launch":
            prior_server = create_server(
                "127.0.0.1",
                0,
                str(base / "prior-state.db"),
                str(base / "prior-traces.jsonl"),
                str(base / "unused-prior-evaluation.json"),
                prior_capability,
            )
            prior_server.server_close()
        server = create_server(
            "127.0.0.1",
            0,
            str(base / "state.db"),
            str(trace_path),
            str(base / "unused-evaluation.json"),
            current_capability,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        response_payloads: list[dict] = []
        try:
            port = server.server_port
            run_status, run, _, _ = _post(
                port,
                "/api/runs",
                _canonical({"scenario_id": "dev-worker-backlog"}).encode("utf-8"),
            )
            if run_status != 201 or run.get("outcome") != "propose_action":
                raise RuntimeError(f"Operator authentication setup failed: HTTP {run_status}")
            response_payloads.append(run)
            proposal_id = run["proposal"]["id"]
            incident_id = run["incident_id"]
            before = _state_fingerprint(server.service, trace_path)
            raw_body = (
                b"{"
                if case["body"] == "malformed_json"
                else _canonical(case["body"]).encode("utf-8")
            )
            status, response, headers, latency_ms = _post(
                port,
                f"/api/proposals/{proposal_id}/approve",
                raw_body,
                _authorization_values(
                    case["authorization"],
                    current_capability,
                    wrong_capability,
                    prior_capability,
                ),
            )
            response_payloads.append(response)
            after_approval = _state_fingerprint(server.service, trace_path)
            approval_observation = _approval_observation(
                server.service, trace_path, proposal_id
            )
            challenge_values = headers.get("www-authenticate", [])
            observed = {
                "http_status": status,
                "challenge": challenge_values[0] if len(challenge_values) == 1 else None,
                "error_type": response.get("error"),
                "error_message": response.get("message"),
                **approval_observation,
            }
            terminal = None
            execution_status = None
            postconditions_verified = None
            if case["expected"]["accepted"]:
                execution_status, execution, _, execution_latency_ms = _post(
                    port,
                    f"/api/proposals/{proposal_id}/execute",
                    _canonical(
                        {
                            "approval_token": response["approval_token"],
                            "idempotency_key": f"operator-auth:{case['case_id']}",
                        }
                    ).encode("utf-8"),
                )
                latency_ms += execution_latency_ms
                response_payloads.append(execution)
                postconditions_verified = execution.get("postconditions_verified")
                terminal = _terminal_observation(
                    server.service, trace_path, proposal_id, incident_id
                )

            with urlopen(
                f"http://127.0.0.1:{port}/dashboard", timeout=10
            ) as dashboard_response:
                dashboard = dashboard_response.read()
            surfaces = _surface_bytes(
                base, server.service, trace_path, response_payloads, dashboard
            )
            secrets_absent = all(
                secret.encode("ascii") not in surfaces
                for secret in (
                    current_capability,
                    wrong_capability,
                    prior_capability,
                )
            )

            expected = case["expected"]
            checks = {
                "http_status_exact": status == expected["http_status"],
                "challenge_exact": (
                    challenge_values == [AUTHENTICATION_CHALLENGE]
                    if expected["challenge_exact"]
                    else challenge_values == []
                ),
                "error_type_exact": response.get("error") == expected.get("error_type"),
                "error_message_exact": response.get("message")
                == expected.get("error_message"),
                "state_unchanged": (
                    before == after_approval
                    if expected.get("state_unchanged") is True
                    else True
                ),
                "body_not_parsed": (
                    response.get("error") == "OperatorAuthenticationError"
                    if expected.get("body_not_parsed") is True
                    else True
                ),
                "proposal_status_exact": approval_observation["proposal_status"]
                == expected.get("proposal_status", "pending"),
                "approval_count_exact": approval_observation["approval_count"]
                == expected.get("approval_count", 0),
                "approval_audit_count_exact": approval_observation[
                    "approval_audit_count"
                ]
                == expected.get("approval_audit_count", 0),
                "approval_trace_count_exact": approval_observation[
                    "approval_trace_count"
                ]
                == expected.get("approval_trace_count", 0),
                "operator_identity_server_derived": (
                    bool(
                        re.fullmatch(
                            r"operator-[0-9a-f]{16}",
                            approval_observation["operator_identity"] or "",
                        )
                    )
                    if expected.get("operator_identity_server_derived") is True
                    else approval_observation["operator_identity"] is None
                ),
                "caller_actor_absent": (
                    approval_observation["operator_identity"]
                    not in {"sentinel-agent-self-declared", "claimed-human"}
                    if expected.get("caller_actor_absent") is True
                    else True
                ),
                "capability_absent_from_surfaces": secrets_absent,
                "lifetime_exact": (
                    approval_observation["lifetime_seconds"]
                    == expected["lifetime_seconds"]
                    if "lifetime_seconds" in expected
                    else approval_observation["lifetime_seconds"] is None
                ),
                "execution_http_status_exact": (
                    execution_status == expected["execution_http_status"]
                    if "execution_http_status" in expected
                    else execution_status is None
                ),
                "postconditions_verified": (
                    postconditions_verified is expected["postconditions_verified"]
                    if "postconditions_verified" in expected
                    else postconditions_verified is None
                ),
                "authorized_terminal_state_exact": (
                    terminal
                    == {
                        "incident_status": "mitigated",
                        "proposal_status": "executed",
                        "approval_consumed": True,
                        "idempotency_record_count": 1,
                        "execution_audit_count": 1,
                        "execution_trace_count": 1,
                    }
                    if expected["accepted"]
                    else terminal is None
                ),
            }
            exact = all(checks.values())
            record = {
                "case_id": case["case_id"],
                "split": case["split"],
                "authorization_role": case["authorization"],
                "accepted_expected": expected["accepted"],
                "observed": observed,
                "checks": checks,
                "exact": exact,
                "latency_ms": round(latency_ms, 3),
                "state_before_sha256": _sha256(_canonical(before).encode("utf-8")),
                "state_after_approval_sha256": _sha256(
                    _canonical(after_approval).encode("utf-8")
                ),
            }
            if any(
                secret in _canonical(record)
                for secret in (
                    current_capability,
                    wrong_capability,
                    prior_capability,
                )
            ):
                raise RuntimeError("Operator capability entered evaluation record")
            return record
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            del current_capability
            del wrong_capability
            del prior_capability


def _rate(records: list[dict], predicate) -> float:
    return sum(bool(predicate(record)) for record in records) / len(records) if records else 0.0


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * percentile + 0.999999) - 1))
    return ordered[index]


def run_operator_authentication_evaluation() -> dict:
    contract_bytes = load_contract_bytes()
    contract = json.loads(contract_bytes)
    if contract.get("contract_id") != CONTRACT_ID:
        raise ValueError("Operator authentication contract identity mismatch")
    records = [_run_case(case) for case in contract["cases"]]
    development = [record for record in records if record["split"] == "development"]
    test = [record for record in records if record["split"] == "test"]
    denied = [record for record in records if not record["accepted_expected"]]
    accepted = [record for record in records if record["accepted_expected"]]
    authentication_denials = [
        record
        for record in denied
        if record["observed"]["http_status"] == 401
    ]
    latencies = [record["latency_ms"] for record in records]
    metrics = {
        "case_count": len(records),
        "exact_match_rate": _rate(records, lambda record: record["exact"]),
        "development_exact_match_rate": _rate(
            development, lambda record: record["exact"]
        ),
        "test_exact_match_rate": _rate(test, lambda record: record["exact"]),
        "authentication_denial_exact_rate": _rate(
            authentication_denials, lambda record: record["exact"]
        ),
        "authorized_utility_exact_rate": _rate(
            accepted, lambda record: record["exact"]
        ),
        "unauthorized_no_mutation_rate": _rate(
            denied, lambda record: record["checks"]["state_unchanged"]
        ),
        "server_derived_identity_rate": _rate(
            accepted,
            lambda record: record["checks"]["operator_identity_server_derived"],
        ),
        "capability_exclusion_rate": _rate(
            records,
            lambda record: record["checks"]["capability_absent_from_surfaces"],
        ),
        "prior_launch_rejection_rate": _rate(
            [
                record
                for record in records
                if record["authorization_role"] == "prior_launch"
            ],
            lambda record: record["exact"],
        ),
        "latency_ms": {
            "median": round(median(latencies), 3),
            "p95": round(_percentile(latencies, 0.95), 3),
        },
        "model_calls": 0,
        "estimated_cost_usd": 0.0,
    }
    gates = {
        "contract_case_count_exact": len(records) == 10,
        "development_exact": all(record["exact"] for record in development),
        "test_exact": all(record["exact"] for record in test),
        "authentication_denial_exact": metrics[
            "authentication_denial_exact_rate"
        ]
        == 1.0,
        "authorized_utility_exact": metrics["authorized_utility_exact_rate"] == 1.0,
        "unauthorized_no_mutation": metrics["unauthorized_no_mutation_rate"]
        == 1.0,
        "server_derived_identity": metrics["server_derived_identity_rate"] == 1.0,
        "capability_exclusion": metrics["capability_exclusion_rate"] == 1.0,
        "prior_launch_rejection": metrics["prior_launch_rejection_rate"] == 1.0,
    }
    gates["operator_authentication_disposition"] = (
        "pass" if all(gates.values()) else "fail"
    )
    result = {
        "schema_version": "1.0",
        "contract_id": CONTRACT_ID,
        "contract_sha256": _sha256(contract_bytes),
        "checkpoint": "baseline-0015",
        "records": records,
        "metrics": metrics,
        "gates": gates,
    }
    return result
