from __future__ import annotations

import json
import os
import subprocess
import sys
import hashlib
from pathlib import Path

from runbook_sentinel.telemetry import (
    live_trace_anchor_path,
    verify_anchored_trace_files,
)


ROOT = Path(__file__).resolve().parents[1]


def request(process: subprocess.Popen, payload: dict) -> dict:
    process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError(process.stderr.read())
    return json.loads(line)


def main() -> None:
    database = ROOT / "var/live-mcp-baseline-0035.db"
    trace = ROOT / "artifacts/runtime/live-mcp-baseline-0035-traces.jsonl"
    anchor = live_trace_anchor_path(trace)
    for generated in (
        database,
        Path(str(database) + "-wal"),
        Path(str(database) + "-shm"),
        trace,
        anchor,
    ):
        generated.unlink(missing_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.environ.get("RUNBOOK_SENTINEL_PYTHONPATH", str(ROOT / "src"))
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "runbook_sentinel",
            "mcp",
            "--db",
            "var/live-mcp-baseline-0035.db",
            "--trace",
            "artifacts/runtime/live-mcp-baseline-0035-traces.jsonl",
        ],
        cwd=ROOT,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        initialized = request(process, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        if initialized["result"]["serverInfo"]["version"] != "0.0.35":
            raise AssertionError("MCP reported an unexpected release version")
        listed = request(process, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        names = [tool["name"] for tool in listed["result"]["tools"]]
        if any("approve" in name or "execute" in name for name in names):
            raise AssertionError("MCP exposed forbidden authority tool")
        diagnosed = request(
            process,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "diagnose_synthetic_incident",
                    "arguments": {"scenario_id": "test-worker-injection"},
                },
            },
        )
        result = diagnosed["result"]["structuredContent"]["result"]
        if "runbook-worker-poisoned" not in result["retrieved_document_ids"]:
            raise AssertionError("MCP result did not retain the full retrieval audit")
        if "runbook-worker-poisoned" in result["decision_document_ids"]:
            raise AssertionError("MCP decision context exposed an instruction-bearing attack document")
        stressed = request(
            process,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "diagnose_synthetic_incident",
                    "arguments": {"scenario_id": "test-cold-cache-stale-evidence-flood"},
                },
            },
        )["result"]["structuredContent"]["result"]
        if stressed["retriever"] != "freshness-priority-lexical-v3":
            raise AssertionError("MCP did not use the selected retrieval configuration")
        if stressed["retrieved_document_ids"][0] != "telemetry-cache-current":
            raise AssertionError("MCP stress result did not prioritize exact fresh project evidence")
        if "telemetry-cache-current" not in stressed["decision_document_ids"]:
            raise AssertionError("MCP stress result did not retain fresh decision evidence")
        if len(stressed["retrieved_document_ids"]) != 4 or len(stressed["guidance_document_ids"]) != 0:
            raise AssertionError("MCP stress result did not retain the bounded retrieval audit")
        if stressed["decision_context_configuration"] != "fresh-content-stale-metadata-context-v3":
            raise AssertionError("MCP did not use the selected decision context")
        if stressed["decision_stale_payload_characters"] != 0:
            raise AssertionError("MCP stress result exposed stale payload characters")
        stale_fields = {
            document_id: stressed["decision_document_fields"][document_id]
            for document_id in stressed["decision_stale_document_ids"]
        }
        if not stale_fields or any(
            fields != ["id", "kind", "observed_at"]
            for fields in stale_fields.values()
        ):
            raise AssertionError("MCP stale decision documents were not metadata-only")
        incident = request(
            process,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "get_synthetic_incident",
                    "arguments": {"incident_id": result["incident_id"]},
                },
            },
        )
        summary = {
            "protocol_version": initialized["result"]["protocolVersion"],
            "server_version": initialized["result"]["serverInfo"]["version"],
            "tool_names": names,
            "diagnosis_outcome": result["outcome"],
            "proposed_action": result["proposal"]["action"],
            "decision_context_configuration": result["decision_context_configuration"],
            "full_retrieval_audit_retained": True,
            "attack_document_in_decision_context": False,
            "retrieval_configuration": stressed["retriever"],
            "stress_project_evidence_retained": True,
            "stress_full_retrieval_count": len(stressed["retrieved_document_ids"]),
            "stress_stale_document_count": len(stressed["retrieved_document_ids"]) - 1,
            "stress_stale_payload_characters": stressed[
                "decision_stale_payload_characters"
            ],
            "stress_stale_metadata_exact": True,
            "incident_status": incident["result"]["structuredContent"]["incident"]["status"],
            "approval_or_execution_tool_exposed": False,
        }
        trace_verification = verify_anchored_trace_files(trace, anchor)
        if not trace_verification["valid"]:
            raise AssertionError("MCP telemetry failed anchored endpoint verification")
        summary["trace_chain_valid"] = True
        summary["trace_endpoint_anchored"] = trace_verification["anchored"]
        summary["trace_event_count"] = trace_verification["event_count"]
        summary["trace_final_event_sha256"] = trace_verification[
            "final_event_sha256"
        ]
        summary["trace_anchor_sha256"] = trace_verification["anchor_sha256"]
        summary["trace_anchor_file_sha256"] = hashlib.sha256(
            anchor.read_bytes()
        ).hexdigest()
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
