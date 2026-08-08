from __future__ import annotations

import json
import secrets
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .api import create_server
from .operator_auth import authorization_value


CONTRACT_ID = "approval-lifetime-v1"
INVALID_ERROR_TYPE = "ValueError"
INVALID_ERROR_MESSAGE = "Approval TTL must be an integer from 1 through 300 seconds"
CASES = (
    {
        "case_id": "dev-negative-ttl",
        "split": "development",
        "ttl_present": True,
        "ttl_value": -1,
        "accepted": False,
    },
    {
        "case_id": "dev-above-maximum-ttl",
        "split": "development",
        "ttl_present": True,
        "ttl_value": 301,
        "accepted": False,
    },
    {
        "case_id": "dev-minimum-ttl",
        "split": "development",
        "ttl_present": True,
        "ttl_value": 1,
        "accepted": True,
        "lifetime_seconds": 1,
    },
    {
        "case_id": "test-zero-ttl",
        "split": "test",
        "ttl_present": True,
        "ttl_value": 0,
        "accepted": False,
    },
    {
        "case_id": "test-fractional-ttl",
        "split": "test",
        "ttl_present": True,
        "ttl_value": 1.5,
        "accepted": False,
    },
    {
        "case_id": "test-string-ttl",
        "split": "test",
        "ttl_present": True,
        "ttl_value": "300",
        "accepted": False,
    },
    {
        "case_id": "test-boolean-ttl",
        "split": "test",
        "ttl_present": True,
        "ttl_value": True,
        "accepted": False,
    },
    {
        "case_id": "test-maximum-ttl",
        "split": "test",
        "ttl_present": True,
        "ttl_value": 300,
        "accepted": True,
        "lifetime_seconds": 300,
    },
    {
        "case_id": "test-default-ttl",
        "split": "test",
        "ttl_present": False,
        "accepted": True,
        "lifetime_seconds": 300,
    },
)


def _post_json(
    url: str, payload: dict, authorization: str | None = None
) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if authorization is not None:
        headers["Authorization"] = authorization
    request = Request(
        url,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        with error:
            return error.code, json.loads(error.read())


def _trace_approval_count(trace_path: Path, proposal_id: str) -> int:
    if not trace_path.exists():
        return 0
    return sum(
        event.get("name") == "sentinel.approval"
        and event.get("attributes", {}).get("proposal.id") == proposal_id
        for event in (
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    )


def _run_case(case: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="sentinel-approval-lifetime-") as temp_dir:
        base = Path(temp_dir)
        database_path = base / "state.db"
        trace_path = base / "traces.jsonl"
        operator_capability = secrets.token_urlsafe(32)
        server = create_server(
            "127.0.0.1",
            0,
            str(database_path),
            str(trace_path),
            str(base / "unused-evaluation.json"),
            operator_capability,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            root = f"http://127.0.0.1:{server.server_port}"
            run_status, run = _post_json(
                f"{root}/api/runs", {"scenario_id": "dev-worker-backlog"}
            )
            if run_status != 201 or run.get("outcome") != "propose_action":
                raise RuntimeError(f"Approval lifetime setup failed: HTTP {run_status}")
            proposal_id = run["proposal"]["id"]
            incident_id = run["incident_id"]
            incident_before = server.service.get_incident(incident_id)
            approval_request = {}
            if case["ttl_present"]:
                approval_request["ttl_seconds"] = case["ttl_value"]
            approval_status, approval_response = _post_json(
                f"{root}/api/proposals/{proposal_id}/approve",
                approval_request,
                authorization_value(operator_capability),
            )

            with server.service.storage.connect() as connection:
                proposal = connection.execute(
                    "SELECT status FROM proposals WHERE id = ?", (proposal_id,)
                ).fetchone()
                approvals = connection.execute(
                    "SELECT id, token_hash, created_at, expires_at FROM approvals WHERE proposal_id = ?",
                    (proposal_id,),
                ).fetchall()
                approval_audit_count = connection.execute(
                    "SELECT COUNT(*) FROM audit_log WHERE subject_id = ? AND event_type = 'proposal.approved'",
                    (proposal_id,),
                ).fetchone()[0]
            incident_after = server.service.get_incident(incident_id)
            approval_trace_count = _trace_approval_count(trace_path, proposal_id)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            del operator_capability

        accepted = case["accepted"]
        expected_status = 201 if accepted else 400
        expected_proposal_status = "approved" if accepted else "pending"
        expected_count = 1 if accepted else 0
        lifetime_seconds = None
        approval_token_hashed = None
        if approvals:
            lifetime_seconds = (
                datetime.fromisoformat(approvals[0]["expires_at"])
                - datetime.fromisoformat(approvals[0]["created_at"])
            ).total_seconds()
            token_hash = approvals[0]["token_hash"]
            approval_token_hashed = len(token_hash) == 64 and all(
                character in "0123456789abcdef" for character in token_hash
            )

        checks = {
            "http_status_exact": approval_status == expected_status,
            "proposal_status_exact": proposal["status"] == expected_proposal_status,
            "approval_count_exact": len(approvals) == expected_count,
            "approval_audit_count_exact": approval_audit_count == expected_count,
            "approval_trace_count_exact": approval_trace_count == expected_count,
            "incident_status_exact": incident_after["status"] == "open",
            "incident_state_unchanged": incident_after == incident_before,
        }
        if accepted:
            checks.update(
                {
                    "lifetime_exact": lifetime_seconds == case["lifetime_seconds"],
                    "approval_token_hashed": approval_token_hashed is True,
                    "approval_response_shape_exact": set(approval_response)
                    == {
                        "approval_id",
                        "proposal_id",
                        "approval_token",
                        "expires_at",
                        "action_hash",
                    },
                }
            )
        else:
            checks.update(
                {
                    "error_type_exact": approval_response.get("error")
                    == INVALID_ERROR_TYPE,
                    "error_message_exact": approval_response.get("message")
                    == INVALID_ERROR_MESSAGE,
                }
            )

        return {
            "case_id": case["case_id"],
            "split": case["split"],
            "accepted": accepted,
            "case_pass": all(checks.values()),
            "checks": checks,
            "actual": {
                "http_status": approval_status,
                "proposal_status": proposal["status"],
                "approval_count": len(approvals),
                "approval_audit_count": approval_audit_count,
                "approval_trace_count": approval_trace_count,
                "incident_status": incident_after["status"],
                "lifetime_seconds": lifetime_seconds,
                "error_type": approval_response.get("error"),
                "error_message": approval_response.get("message"),
            },
        }


def _rate(results: list[dict], key: str) -> float:
    return sum(bool(result[key]) for result in results) / len(results) if results else 0.0


def run_approval_lifetime_evaluation() -> dict:
    results = [_run_case(case) for case in CASES]
    invalid = [result for result in results if not result["accepted"]]
    valid = [result for result in results if result["accepted"]]
    split_exact_match_rate = {
        split: _rate(
            [result for result in results if result["split"] == split], "case_pass"
        )
        for split in ("development", "test")
    }
    invalid_no_mutation_rate = sum(
        all(
            result["checks"][check]
            for check in (
                "proposal_status_exact",
                "approval_count_exact",
                "approval_audit_count_exact",
                "approval_trace_count_exact",
                "incident_status_exact",
                "incident_state_unchanged",
            )
        )
        for result in invalid
    ) / len(invalid)
    valid_lifetime_exact_rate = sum(
        result["checks"]["lifetime_exact"] for result in valid
    ) / len(valid)
    exact_match_rate = _rate(results, "case_pass")
    return {
        "contract_id": CONTRACT_ID,
        "surface": "real loopback HTTP API, SQLite persistence, audit log, and JSONL trace",
        "case_count": len(results),
        "invalid_case_count": len(invalid),
        "valid_case_count": len(valid),
        "development_case_count": sum(
            result["split"] == "development" for result in results
        ),
        "test_case_count": sum(result["split"] == "test" for result in results),
        "exact_match_rate": exact_match_rate,
        "invalid_no_mutation_rate": invalid_no_mutation_rate,
        "valid_lifetime_exact_rate": valid_lifetime_exact_rate,
        "split_exact_match_rate": split_exact_match_rate,
        "held_out_candidate_results_revealed": True,
        "gates": {
            "all_nine_cases_exact": exact_match_rate == 1.0,
            "all_six_invalid_cases_no_mutation": invalid_no_mutation_rate == 1.0,
            "all_three_valid_lifetimes_exact": valid_lifetime_exact_rate == 1.0,
            "development_exact": split_exact_match_rate["development"] == 1.0,
            "test_exact": split_exact_match_rate["test"] == 1.0,
        },
        "cases": results,
    }
