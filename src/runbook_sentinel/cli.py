from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .api import create_server
from .evaluation import AGENT_CONFIGURATIONS, CONTROL_AGENT_CONFIGURATION, run_evaluation
from .mcp_server import main as mcp_main
from .operator_auth import authorization_value, validate_operator_capability
from .retrieval import (
    DECISION_CONTEXT_CONFIGURATIONS,
    DEFAULT_DECISION_CONTEXT,
    DEFAULT_RETRIEVAL_CONFIGURATION,
    RETRIEVAL_CONFIGURATIONS,
)
from .service import RunbookSentinel
from .telemetry import live_trace_anchor_path


def _print(value: dict | list) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _read_operator_capability(from_stdin: bool) -> str:
    capability = (
        sys.stdin.readline().rstrip("\r\n")
        if from_stdin
        else getpass.getpass("Per-launch operator capability: ")
    )
    return validate_operator_capability(capability)


def _loopback_server_url(value: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Approval server must be a loopback HTTP origin")
    return value.rstrip("/")


def _approve_over_http(
    server_url: str,
    proposal_id: str,
    capability: str,
    ttl_seconds: int | None,
) -> dict:
    payload = {} if ttl_seconds is None else {"ttl_seconds": ttl_seconds}
    request = Request(
        f"{_loopback_server_url(server_url)}/api/proposals/{quote(proposal_id, safe='')}/approve",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": authorization_value(capability),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, request, file_pointer, code, message, headers, new_url):
            raise HTTPError(new_url, code, "Approval redirects are forbidden", headers, file_pointer)

    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=10) as response:
            return json.loads(response.read())
    except HTTPError as error:
        with error:
            payload = json.loads(error.read())
        raise RuntimeError(
            f"Approval request failed with HTTP {error.code}: {payload.get('error')}"
        ) from None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="runbook-sentinel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--scenario", required=True)
    run_parser.add_argument("--db", default="var/sentinel.db")
    run_parser.add_argument("--trace", default="var/traces.jsonl")

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--proposal", required=True)
    approve_parser.add_argument("--server", default="http://127.0.0.1:8765")
    approve_parser.add_argument("--ttl-seconds", type=int)
    approve_parser.add_argument("--operator-capability-stdin", action="store_true")

    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("--proposal", required=True)
    execute_parser.add_argument("--token", required=True)
    execute_parser.add_argument("--idempotency-key", required=True)
    execute_parser.add_argument("--db", default="var/sentinel.db")
    execute_parser.add_argument("--trace", default="var/traces.jsonl")

    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--output", default="artifacts/evaluations/runs/baseline-0025-manual.json")
    evaluate_parser.add_argument("--trials", type=int, default=3)
    evaluate_parser.add_argument(
        "--agent-configuration",
        choices=AGENT_CONFIGURATIONS,
        default=CONTROL_AGENT_CONFIGURATION,
    )
    evaluate_parser.add_argument("--model-contract", default="eval/model-contract.json")
    evaluate_parser.add_argument(
        "--decision-context",
        choices=DECISION_CONTEXT_CONFIGURATIONS,
        default=DEFAULT_DECISION_CONTEXT,
    )
    evaluate_parser.add_argument(
        "--retrieval-configuration",
        choices=RETRIEVAL_CONFIGURATIONS,
        default=DEFAULT_RETRIEVAL_CONFIGURATION,
    )

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8765)
    serve_parser.add_argument("--db", default="var/sentinel.db")
    serve_parser.add_argument("--trace", default="var/traces.jsonl")
    serve_parser.add_argument("--evaluation", default="artifacts/evaluations/latest.json")
    serve_parser.add_argument("--operator-capability-stdin", action="store_true")

    mcp_parser = subparsers.add_parser("mcp")
    mcp_parser.add_argument("--db", default="var/mcp.db")
    mcp_parser.add_argument("--trace", default="var/mcp-traces.jsonl")

    args = parser.parse_args(argv)
    if args.command == "evaluate":
        report = run_evaluation(
            Path(args.output),
            args.trials,
            args.decision_context,
            args.agent_configuration,
            Path(args.model_contract),
            retrieval_configuration=args.retrieval_configuration,
        )
        _print({"metrics": report["metrics"], "gates": report["gates"]})
    elif args.command == "serve":
        capability = _read_operator_capability(args.operator_capability_stdin)
        server = create_server(
            args.host,
            args.port,
            args.db,
            args.trace,
            args.evaluation,
            capability,
        )
        del capability
        print(f"Runbook Sentinel listening on http://{args.host}:{server.server_port}/dashboard", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    elif args.command == "mcp":
        mcp_main(["--db", args.db, "--trace", args.trace])
    elif args.command == "approve":
        capability = _read_operator_capability(args.operator_capability_stdin)
        try:
            _print(
                _approve_over_http(
                    args.server,
                    args.proposal,
                    capability,
                    args.ttl_seconds,
                )
            )
        finally:
            del capability
    else:
        service = RunbookSentinel(
            args.db,
            args.trace,
            str(live_trace_anchor_path(args.trace)),
        )
        if args.command == "run":
            _print(service.run_scenario(args.scenario))
        elif args.command == "execute":
            _print(service.execute(args.proposal, args.token, args.idempotency_key))
