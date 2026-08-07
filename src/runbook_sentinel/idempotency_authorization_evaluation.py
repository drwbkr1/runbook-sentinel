from __future__ import annotations

import hashlib
import json
import tempfile
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .api import create_server


CONTRACT_ID = "idempotency-authorization-v1"
INVALID_ERROR_TYPE = "ApprovalError"
INVALID_ERROR_MESSAGE = "Approval token is invalid"
REPLAY_ERROR_TYPE = "ReplayRejected"
REPLAY_ERROR_MESSAGE = "Proposal has already been executed"
CASES = (
    {
        "case_id": "dev-wrong-token-same-key",
        "split": "development",
        "category": "unauthorized_cache",
        "token_role": "wrong_syntactically_valid",
        "key_role": "original",
    },
    {
        "case_id": "dev-missing-token-same-key",
        "split": "development",
        "category": "unauthorized_cache",
        "token_role": "missing",
        "key_role": "original",
    },
    {
        "case_id": "dev-original-consumed-token-same-key",
        "split": "development",
        "category": "authorized_cache",
        "token_role": "original_consumed",
        "key_role": "original",
    },
    {
        "case_id": "test-other-proposal-token-same-key",
        "split": "test",
        "category": "unauthorized_cache",
        "token_role": "other_proposal_valid_unconsumed",
        "key_role": "original",
    },
    {
        "case_id": "test-expired-original-consumed-token-same-key",
        "split": "test",
        "category": "authorized_cache",
        "token_role": "original_consumed",
        "key_role": "original",
        "expire_after_execution": True,
    },
    {
        "case_id": "test-original-consumed-token-new-key",
        "split": "test",
        "category": "new_key_replay",
        "token_role": "original_consumed",
        "key_role": "new",
    },
)
TABLES = (
    "incidents",
    "runs",
    "proposals",
    "approvals",
    "idempotency",
    "audit_log",
)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        url,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        with error:
            return error.code, json.loads(error.read())


def _state_fingerprint(service, trace_path: Path) -> dict:
    rows: dict[str, list[dict]] = {}
    with service.storage.connect() as connection:
        for table in TABLES:
            rows[table] = [
                dict(row)
                for row in connection.execute(
                    f"SELECT * FROM {table} ORDER BY rowid"
                ).fetchall()
            ]
    database_bytes = _canonical(rows).encode("utf-8")
    trace_bytes = trace_path.read_bytes() if trace_path.exists() else b""
    return {
        "database_sha256": _sha256(database_bytes),
        "trace_sha256": _sha256(trace_bytes),
        "table_counts": {table: len(values) for table, values in rows.items()},
        "trace_bytes": len(trace_bytes),
    }


def _target_boundary(service, trace_path: Path, proposal_id: str, incident_id: str) -> dict:
    with service.storage.connect() as connection:
        proposal = connection.execute(
            "SELECT status FROM proposals WHERE id = ?", (proposal_id,)
        ).fetchone()
        approval = connection.execute(
            "SELECT consumed_at FROM approvals WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()
        incident = connection.execute(
            "SELECT status FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        idempotency_count = connection.execute(
            "SELECT COUNT(*) FROM idempotency WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()[0]
        execution_audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_log WHERE subject_id = ? AND event_type = 'proposal.executed'",
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


def _run_case(case: dict) -> dict:
    with tempfile.TemporaryDirectory(
        prefix="sentinel-idempotency-authorization-"
    ) as temp_dir:
        base = Path(temp_dir)
        database_path = base / "state.db"
        trace_path = base / "traces.jsonl"
        server = create_server(
            "127.0.0.1",
            0,
            str(database_path),
            str(trace_path),
            str(base / "unused-evaluation.json"),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            root = f"http://127.0.0.1:{server.server_port}"
            run_status, run = _post_json(
                f"{root}/api/runs", {"scenario_id": "dev-worker-backlog"}
            )
            if run_status != 201 or run.get("outcome") != "propose_action":
                raise RuntimeError(
                    f"Idempotency authorization setup failed: HTTP {run_status}"
                )
            proposal_id = run["proposal"]["id"]
            incident_id = run["incident_id"]
            approval_status, approval = _post_json(
                f"{root}/api/proposals/{proposal_id}/approve",
                {"actor": "idempotency-authorization-evaluator"},
            )
            if approval_status != 201:
                raise RuntimeError(
                    f"Idempotency authorization approval failed: HTTP {approval_status}"
                )
            original_token = approval["approval_token"]
            original_key = "idempotency-authorization:original"
            execution_status, execution = _post_json(
                f"{root}/api/proposals/{proposal_id}/execute",
                {
                    "approval_token": original_token,
                    "idempotency_key": original_key,
                },
            )
            if execution_status != 200 or execution.get("status") != "executed":
                raise RuntimeError(
                    f"Idempotency authorization execution failed: HTTP {execution_status}"
                )

            other_token = None
            if case["token_role"] == "other_proposal_valid_unconsumed":
                other_run_status, other_run = _post_json(
                    f"{root}/api/runs", {"scenario_id": "test-cold-cache"}
                )
                if other_run_status != 201 or other_run.get("outcome") != "propose_action":
                    raise RuntimeError(
                        f"Other-proposal setup failed: HTTP {other_run_status}"
                    )
                other_proposal_id = other_run["proposal"]["id"]
                other_approval_status, other_approval = _post_json(
                    f"{root}/api/proposals/{other_proposal_id}/approve",
                    {"actor": "idempotency-authorization-evaluator"},
                )
                if other_approval_status != 201:
                    raise RuntimeError(
                        f"Other-proposal approval failed: HTTP {other_approval_status}"
                    )
                other_token = other_approval["approval_token"]

            if case.get("expire_after_execution"):
                with server.service.storage.connect() as connection:
                    connection.execute(
                        "UPDATE approvals SET expires_at = ? WHERE proposal_id = ?",
                        ("2000-01-01T00:00:00+00:00", proposal_id),
                    )

            token_role = case["token_role"]
            if token_role == "original_consumed":
                retry_token = original_token
            elif token_role == "other_proposal_valid_unconsumed":
                retry_token = other_token
            elif token_role == "wrong_syntactically_valid":
                retry_token = "wrong-syntactically-valid-token"
            elif token_role == "missing":
                retry_token = None
            else:
                raise RuntimeError(f"Unknown token role: {token_role}")
            retry_key = (
                original_key
                if case["key_role"] == "original"
                else original_key + ":new"
            )
            retry_payload = {"idempotency_key": retry_key}
            if retry_token is not None:
                retry_payload["approval_token"] = retry_token

            before = _state_fingerprint(server.service, trace_path)
            boundary_before = _target_boundary(
                server.service, trace_path, proposal_id, incident_id
            )
            retry_status, retry_response = _post_json(
                f"{root}/api/proposals/{proposal_id}/execute", retry_payload
            )
            after = _state_fingerprint(server.service, trace_path)
            boundary_after = _target_boundary(
                server.service, trace_path, proposal_id, incident_id
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        category = case["category"]
        if category == "authorized_cache":
            expected_status = 200
            expected_error_type = None
            expected_error_message = None
            exact_cached_result = retry_response == execution
        elif category == "unauthorized_cache":
            expected_status = 409
            expected_error_type = INVALID_ERROR_TYPE
            expected_error_message = INVALID_ERROR_MESSAGE
            exact_cached_result = False
        elif category == "new_key_replay":
            expected_status = 409
            expected_error_type = REPLAY_ERROR_TYPE
            expected_error_message = REPLAY_ERROR_MESSAGE
            exact_cached_result = False
        else:
            raise RuntimeError(f"Unknown case category: {category}")

        expected_boundary = {
            "incident_status": "mitigated",
            "proposal_status": "executed",
            "approval_consumed": True,
            "idempotency_record_count": 1,
            "execution_audit_count": 1,
            "execution_trace_count": 1,
        }
        checks = {
            "http_status_exact": retry_status == expected_status,
            "error_type_exact": retry_response.get("error") == expected_error_type,
            "error_message_exact": retry_response.get("message")
            == expected_error_message,
            "exact_cached_result": exact_cached_result
            == (category == "authorized_cache"),
            "database_state_unchanged": before["database_sha256"]
            == after["database_sha256"],
            "trace_unchanged": before["trace_sha256"] == after["trace_sha256"],
            "table_counts_unchanged": before["table_counts"]
            == after["table_counts"],
            "target_boundary_exact_before": boundary_before == expected_boundary,
            "target_boundary_exact_after": boundary_after == expected_boundary,
        }
        return {
            "case_id": case["case_id"],
            "split": case["split"],
            "category": category,
            "token_role": token_role,
            "key_role": case["key_role"],
            "case_pass": all(checks.values()),
            "checks": checks,
            "actual": {
                "http_status": retry_status,
                "error_type": retry_response.get("error"),
                "error_message": retry_response.get("message"),
                "exact_cached_result": exact_cached_result,
                "database_sha256_before": before["database_sha256"],
                "database_sha256_after": after["database_sha256"],
                "trace_sha256_before": before["trace_sha256"],
                "trace_sha256_after": after["trace_sha256"],
                "table_counts": after["table_counts"],
                "target_boundary": boundary_after,
            },
        }


def _rate(results: list[dict], key: str) -> float:
    return sum(bool(result[key]) for result in results) / len(results) if results else 0.0


def run_idempotency_authorization_evaluation() -> dict:
    results = [_run_case(case) for case in CASES]
    authorized = [result for result in results if result["category"] == "authorized_cache"]
    unauthorized = [result for result in results if result["category"] == "unauthorized_cache"]
    replay = [result for result in results if result["category"] == "new_key_replay"]
    split_exact_match_rate = {
        split: _rate(
            [result for result in results if result["split"] == split], "case_pass"
        )
        for split in ("development", "test")
    }
    exact_match_rate = _rate(results, "case_pass")
    authorized_cache_utility_rate = sum(
        result["checks"]["http_status_exact"]
        and result["checks"]["exact_cached_result"]
        for result in authorized
    ) / len(authorized)
    unauthorized_cache_denial_rate = sum(
        result["checks"]["http_status_exact"]
        and result["checks"]["error_type_exact"]
        and result["checks"]["error_message_exact"]
        and result["checks"]["exact_cached_result"]
        for result in unauthorized
    ) / len(unauthorized)
    retry_no_mutation_rate = sum(
        result["checks"]["database_state_unchanged"]
        and result["checks"]["trace_unchanged"]
        and result["checks"]["table_counts_unchanged"]
        for result in results
    ) / len(results)
    new_key_replay_rejection_rate = sum(
        result["checks"]["http_status_exact"]
        and result["checks"]["error_type_exact"]
        and result["checks"]["error_message_exact"]
        for result in replay
    ) / len(replay)
    return {
        "contract_id": CONTRACT_ID,
        "surface": "real loopback HTTP API, SQLite persistence, audit log, and JSONL trace",
        "case_count": len(results),
        "authorized_cache_case_count": len(authorized),
        "unauthorized_cache_case_count": len(unauthorized),
        "new_key_replay_case_count": len(replay),
        "development_case_count": sum(
            result["split"] == "development" for result in results
        ),
        "test_case_count": sum(result["split"] == "test" for result in results),
        "exact_match_rate": exact_match_rate,
        "authorized_cache_utility_rate": authorized_cache_utility_rate,
        "unauthorized_cache_denial_rate": unauthorized_cache_denial_rate,
        "retry_no_mutation_rate": retry_no_mutation_rate,
        "new_key_replay_rejection_rate": new_key_replay_rejection_rate,
        "split_exact_match_rate": split_exact_match_rate,
        "held_out_candidate_results_revealed": True,
        "gates": {
            "all_six_cases_exact": exact_match_rate == 1.0,
            "all_authorized_cache_retries_exact": authorized_cache_utility_rate == 1.0,
            "all_unauthorized_cache_retries_denied": unauthorized_cache_denial_rate
            == 1.0,
            "all_retries_no_mutation": retry_no_mutation_rate == 1.0,
            "new_key_replay_rejected": new_key_replay_rejection_rate == 1.0,
            "development_exact": split_exact_match_rate["development"] == 1.0,
            "test_exact": split_exact_match_rate["test"] == 1.0,
        },
        "cases": results,
    }
