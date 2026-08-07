from __future__ import annotations

import argparse
import json
from pathlib import Path

from .api import create_server
from .evaluation import AGENT_CONFIGURATIONS, CONTROL_AGENT_CONFIGURATION, run_evaluation
from .mcp_server import main as mcp_main
from .retrieval import (
    DECISION_CONTEXT_CONFIGURATIONS,
    DEFAULT_DECISION_CONTEXT,
    DEFAULT_RETRIEVAL_CONFIGURATION,
    RETRIEVAL_CONFIGURATIONS,
)
from .service import RunbookSentinel


def _print(value: dict | list) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="runbook-sentinel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--scenario", required=True)
    run_parser.add_argument("--db", default="var/sentinel.db")
    run_parser.add_argument("--trace", default="var/traces.jsonl")

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--proposal", required=True)
    approve_parser.add_argument("--actor", required=True)
    approve_parser.add_argument("--db", default="var/sentinel.db")
    approve_parser.add_argument("--trace", default="var/traces.jsonl")

    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("--proposal", required=True)
    execute_parser.add_argument("--token", required=True)
    execute_parser.add_argument("--idempotency-key", required=True)
    execute_parser.add_argument("--db", default="var/sentinel.db")
    execute_parser.add_argument("--trace", default="var/traces.jsonl")

    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--output", default="artifacts/evaluations/runs/baseline-0014-manual.json")
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
        server = create_server(args.host, args.port, args.db, args.trace, args.evaluation)
        print(f"Runbook Sentinel listening on http://{args.host}:{server.server_port}/dashboard", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    elif args.command == "mcp":
        mcp_main(["--db", args.db, "--trace", args.trace])
    else:
        service = RunbookSentinel(args.db, args.trace)
        if args.command == "run":
            _print(service.run_scenario(args.scenario))
        elif args.command == "approve":
            _print(service.approve(args.proposal, args.actor))
        elif args.command == "execute":
            _print(service.execute(args.proposal, args.token, args.idempotency_key))
