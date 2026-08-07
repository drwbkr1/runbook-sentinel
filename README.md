# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

Current release candidate: `v0.0.9`, a synthetic-only research preview that preserves current project-classified evidence when stale, query-matching telemetry crowds a bounded retrieval result. It retains the earlier untrusted-guidance, behavioral-relation, evidence-condition, approval/execution, terminal-state, and excluded local-model evaluations. Public source availability does not imply production readiness or authorization to connect it to operational infrastructure.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

The selected freshness-priority lexical retriever first preserves externally project-classified telemetry and status that pass a fail-closed one-hour freshness rule, then ranks stale project evidence and untrusted guidance. Returned identities remain available for audit, but only telemetry and status records enter the decision context. Missing, malformed, naive, or future timestamps never receive fresh priority. Runbook prose never grants authority.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0009-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765/dashboard`.

The MCP server uses JSON-RPC over standard input/output:

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel mcp --db var/mcp.db
```

## Stale-evidence, retrieval-stress, behavioral-relation, and terminal-state evaluation

Baseline 0009 adds one development and one held-out pair where five stale, query-matching telemetry records compete with current decision evidence for a top-4 result. The selected v3 retriever retains the current evidence and exact behavior in all six repeated stale-evidence attempts. Retained v2 comparisons lose the current evidence and remain `remediate`. Across 28 scenarios and 84 trials, v3 also passes the earlier six guidance-flood attempts and 12 controlled-relation attempts, executes all 33 expected actions through the real approval and executor path, and leaves all 51 no-action trials unchanged. The local comparison does not show strict latency dominance: v3 is selected because it is the only configuration that passes the hard reliability gates, with the measured latency tradeoff recorded rather than hidden.

The harness runs only after the agent result exists, holds approval material only in disposable evaluation state, and is not exposed by the agent, CLI runtime, API automation, MCP, or dashboard.

## Local-model comparison

Baseline 0004 adds an optional direct-loopback Ollama evaluation adapter. The measured `llama3.2:3b` candidate was excluded after only 5 of 54 outputs passed the exact parser; exact trajectory and `pass^3` were both 0.0. The deterministic control remains the default. Zero accepted model proposals and zero attack actions demonstrate fail-closed enforcement, not useful model safety.

The repository never downloads a model or supplies tools, credentials, approvals, or execution authority. See `artifacts/verification/model-source-gate-baseline-0004.json`, `artifacts/evaluations/baseline-0004-comparison.json`, and ADR 0003 for the exact source gate, evidence, and decision.

Container packaging is currently deferred. Three official Python base candidates failed the baseline source gate; see `artifacts/verification/container-source-gate.json`. The native Python workflow is the only accepted runtime for this checkpoint.

## Security boundary

This baseline operates only on a deterministic synthetic SRE environment. It contains no connectors, secrets, credentials, arbitrary command execution, or access to real infrastructure. MCP exposes diagnostic and proposal tools only; execution requires a separate human approval token that is never returned to the agent.

See `docs/status.md`, `docs/architecture.md`, `docs/threat-model.md`, and `docs/evaluation-contract.md` for current project truth.
