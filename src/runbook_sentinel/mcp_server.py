from __future__ import annotations

import argparse
import json
import sys

from .errors import SentinelError
from .service import RunbookSentinel
from .telemetry import live_trace_anchor_path


TOOLS = [
    {
        "name": "list_synthetic_scenarios",
        "title": "List synthetic SRE scenarios",
        "description": "List closed-world synthetic scenarios available to the bounded incident agent.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "outputSchema": {"type": "object", "properties": {"scenarios": {"type": "array"}}, "required": ["scenarios"]},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "diagnose_synthetic_incident",
        "title": "Diagnose a synthetic SRE incident",
        "description": "Run the bounded agent. It may create an additive proposal record but cannot approve or execute it.",
        "inputSchema": {
            "type": "object",
            "properties": {"scenario_id": {"type": "string"}},
            "required": ["scenario_id"],
            "additionalProperties": False,
        },
        "outputSchema": {"type": "object", "properties": {"result": {"type": "object"}}, "required": ["result"]},
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "get_synthetic_incident",
        "title": "Get synthetic incident state",
        "description": "Read persisted synthetic incident state. This tool cannot mutate or execute.",
        "inputSchema": {
            "type": "object",
            "properties": {"incident_id": {"type": "string"}},
            "required": ["incident_id"],
            "additionalProperties": False,
        },
        "outputSchema": {"type": "object", "properties": {"incident": {"type": "object"}}, "required": ["incident"]},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
]


class MCPServer:
    def __init__(self, service: RunbookSentinel):
        self.service = service

    def handle(self, message: dict) -> dict | None:
        if "id" not in message:
            return None
        request_id = message["id"]
        method = message.get("method")
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "runbook-sentinel", "version": "0.0.33"},
                    "instructions": "Synthetic SRE diagnostics and proposals only. No approval or execution tools are exposed.",
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = message.get("params", {})
                name = params.get("name")
                arguments = params.get("arguments", {})
                if name == "list_synthetic_scenarios":
                    structured = {"scenarios": self.service.list_scenarios()}
                elif name == "diagnose_synthetic_incident":
                    structured = {"result": self.service.run_scenario(arguments["scenario_id"])}
                elif name == "get_synthetic_incident":
                    structured = {"incident": self.service.get_incident(arguments["incident_id"])}
                else:
                    raise ValueError(f"Unknown tool: {name}")
                result = {
                    "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
                    "structuredContent": structured,
                    "isError": False,
                }
            else:
                return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except (KeyError, ValueError, SentinelError) as error:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": str(error)}}

    def serve(self) -> None:
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                response = self.handle(json.loads(line))
            except json.JSONDecodeError as error:
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(error)}}
            if response is not None:
                sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                sys.stdout.flush()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="var/mcp.db")
    parser.add_argument("--trace", default="var/mcp-traces.jsonl")
    args = parser.parse_args(argv)
    MCPServer(
        RunbookSentinel(
            args.db,
            args.trace,
            str(live_trace_anchor_path(args.trace)),
        )
    ).serve()


if __name__ == "__main__":
    main()
