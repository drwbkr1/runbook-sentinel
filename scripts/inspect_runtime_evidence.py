from __future__ import annotations

import hashlib
import json
import sqlite3
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    database = ROOT / "var/live-api-baseline-0006.db"
    trace = ROOT / "artifacts/runtime/live-api-baseline-0006-traces.jsonl"
    evaluation = ROOT / "artifacts/evaluations/latest.json"
    manifest = ROOT / "eval/manifest.json"
    screenshot = ROOT / "artifacts/verification/dashboard-baseline-0006.png"
    required = [database, trace, evaluation, manifest, screenshot]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(json.dumps({"status": "fail", "missing": missing}, indent=2))

    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        table_names = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        required_tables = {"incidents", "runs", "proposals", "approvals", "idempotency", "audit_log"}
        approval_columns = [row[1] for row in connection.execute("PRAGMA table_info(approvals)")]
        token_hashes = [row[0] for row in connection.execute("SELECT token_hash FROM approvals")]
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in sorted(required_tables)
        }
        executed = connection.execute("SELECT COUNT(*) FROM proposals WHERE status='executed'").fetchone()[0]
        consumed = connection.execute("SELECT COUNT(*) FROM approvals WHERE consumed_at IS NOT NULL").fetchone()[0]
        audit_types = [row[0] for row in connection.execute("SELECT event_type FROM audit_log ORDER BY sequence")]

    trace_text = trace.read_text(encoding="utf-8")
    trace_events = [json.loads(line) for line in trace_text.splitlines() if line.strip()]
    run_trace_events = [event for event in trace_events if event["name"] == "sentinel.run"]
    forbidden_trace_terms = [term for term in ("approval_token", "Authorization", "Bearer ", "secret") if term in trace_text]
    latest = json.loads(evaluation.read_text(encoding="utf-8"))
    with screenshot.open("rb") as handle:
        signature = handle.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("Dashboard artifact is not a PNG")
    width, height = struct.unpack(">II", signature[16:24])

    checks = {
        "required_tables_present": required_tables.issubset(table_names),
        "raw_token_column_absent": "approval_token" not in approval_columns and "token" not in approval_columns,
        "stored_tokens_are_sha256": bool(token_hashes) and all(len(value) == 64 for value in token_hashes),
        "executed_proposals_have_consumed_approvals": executed > 0 and executed == consumed,
        "audit_contains_approval_and_execution": "proposal.approved" in audit_types and "proposal.executed" in audit_types,
        "trace_has_expected_events": {"sentinel.run", "sentinel.approval", "sentinel.execute"}.issubset({event["name"] for event in trace_events}),
        "trace_has_no_forbidden_terms": not forbidden_trace_terms,
        "decision_context_is_evidence_only": bool(run_trace_events)
        and all(
            event["attributes"].get("retrieval.decision_context") == "evidence-only-context-v2"
            and event["attributes"].get("retrieval.decision_document_count", 0)
            <= event["attributes"].get("retrieval.document_count", 0)
            for event in run_trace_events
        ),
        "evaluation_passed": latest["gates"]["baseline_disposition"] == "pass",
        "evaluation_tool_trajectory_exact": latest["metrics"]["tool_trajectory"]["exact_match"] == 1.0,
        "evaluation_terminal_state_exact": latest["metrics"]["terminal_state"]["exact_match_rate"] == 1.0,
        "evaluation_evidence_condition_coverage": latest["metrics"]["coverage"]["evidence_condition_split_coverage"] == 1.0,
        "evaluation_adversarial_split_coverage": latest["metrics"]["coverage"]["adversarial_split_coverage"] == 1.0,
        "evaluation_matches_frozen_manifest": latest["manifest_sha256"] == sha256(manifest),
        "dashboard_has_expected_dimensions": (width, height) == (1440, 1000),
    }
    receipt = {
        "schema_version": "1.0",
        "checkpoint": latest["checkpoint"],
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "database": {"sha256": sha256(database), "counts": counts, "audit_event_types": audit_types},
        "telemetry": {"sha256": sha256(trace), "event_count": len(trace_events), "forbidden_terms": forbidden_trace_terms},
        "evaluation": {
            "sha256": sha256(evaluation),
            "manifest_sha256": latest["manifest_sha256"],
            "attempt_count": latest["attempt_count"],
            "evidence_condition_split_coverage": latest["metrics"]["coverage"]["evidence_condition_split_coverage"],
            "adversarial_split_coverage": latest["metrics"]["coverage"]["adversarial_split_coverage"],
        },
        "dashboard": {"sha256": sha256(screenshot), "width": width, "height": height},
    }
    output = ROOT / "artifacts/verification/native-baseline-0006.json"
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if receipt["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
