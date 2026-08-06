from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def request(process: subprocess.Popen, payload: dict) -> dict:
    process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError(process.stderr.read())
    return json.loads(line)


def main() -> None:
    database = ROOT / "var/live-mcp-baseline-0005.db"
    trace = ROOT / "artifacts/runtime/live-mcp-baseline-0005-traces.jsonl"
    for generated in (database, Path(str(database) + "-wal"), Path(str(database) + "-shm"), trace):
        generated.unlink(missing_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "runbook_sentinel",
            "mcp",
            "--db",
            "var/live-mcp-baseline-0005.db",
            "--trace",
            "artifacts/runtime/live-mcp-baseline-0005-traces.jsonl",
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
        if initialized["result"]["serverInfo"]["version"] != "0.0.5":
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
        incident = request(
            process,
            {
                "jsonrpc": "2.0",
                "id": 4,
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
            "incident_status": incident["result"]["structuredContent"]["incident"]["status"],
            "approval_or_execution_tool_exposed": False,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
