# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

Current candidate: `v0.0.8`, a synthetic-only research preview that preserves project-classified evidence under a frozen untrusted-guidance flood in development and held-out splits while retaining controlled evidence relations, exact isolated approval/execution trajectories, terminal state, evidence-condition coverage, and the excluded local-model comparison. Public source availability does not imply production readiness or authorization to connect it to operational infrastructure.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

The selected evidence-priority lexical retriever first preserves externally project-classified telemetry and status within the bounded result, then fills remaining slots with untrusted guidance. Returned identities remain available for audit, but only telemetry and status records enter the decision context. Runbook prose never grants authority.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0008-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765/dashboard`.

The MCP server uses JSON-RPC over standard input/output:

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel mcp --db var/mcp.db
```

## Retrieval-stress, behavioral-relation, and terminal-state evaluation

Baseline 0008 freezes one development and one held-out guidance-flood pair where five query-matching instruction-bearing runbooks compete for a top-4 result. The selected v2 retriever retains required project evidence and three auditable guidance records in all six repeated stress attempts; v1 retains no required project evidence and remains preserved with disposition `remediate`. The 78-trial candidate also grades 12 controlled-relation attempts and executes 27 expected actions through the real approval and executor path while proving 51 no-action trials remain unchanged. The harness runs only after the agent result exists, holds approval material only in disposable evaluation state, and is not exposed by the agent, CLI runtime, API automation, MCP, or dashboard.

## Local-model comparison

Baseline 0004 adds an optional direct-loopback Ollama evaluation adapter. The measured `llama3.2:3b` candidate was excluded after only 5 of 54 outputs passed the exact parser; exact trajectory and `pass^3` were both 0.0. The deterministic control remains the default. Zero accepted model proposals and zero attack actions demonstrate fail-closed enforcement, not useful model safety.

The repository never downloads a model or supplies tools, credentials, approvals, or execution authority. See `artifacts/verification/model-source-gate-baseline-0004.json`, `artifacts/evaluations/baseline-0004-comparison.json`, and ADR 0003 for the exact source gate, evidence, and decision.

Container packaging is currently deferred. Three official Python base candidates failed the baseline source gate; see `artifacts/verification/container-source-gate.json`. The native Python workflow is the only accepted runtime for this checkpoint.

## Security boundary

This baseline operates only on a deterministic synthetic SRE environment. It contains no connectors, secrets, credentials, arbitrary command execution, or access to real infrastructure. MCP exposes diagnostic and proposal tools only; execution requires a separate human approval token that is never returned to the agent.

See `docs/status.md`, `docs/architecture.md`, `docs/threat-model.md`, and `docs/evaluation-contract.md` for current project truth.
