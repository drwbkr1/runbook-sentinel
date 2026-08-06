# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

Current release: `v0.0.5`, a synthetic-only research preview that exact-grades real isolated approval/execution trajectories and terminal state while retaining and excluding the failed local-model comparison. Public source availability does not imply production readiness or authorization to connect it to operational infrastructure.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

The lexical retriever retains full document identities for audit, but only project-classified telemetry and status records enter the decision context. Runbook prose remains untrusted guidance and never grants authority.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0005-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765/dashboard`.

The MCP server uses JSON-RPC over standard input/output:

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel mcp --db var/mcp.db
```

## Exact terminal-state evaluation

Baseline 0005 freezes an exact full terminal state and external-harness trajectory for every case. The selected deterministic attempt executes 15 expected actions through the real approval and executor path, proves 39 no-action trials remain unchanged, covers all three synthetic actions, rejects consumed-token replay, verifies postconditions, and grades audit and trace sequences separately. The harness runs only after the agent result exists, holds approval material only in disposable evaluation state, and is not exposed by the agent, CLI runtime, API automation, MCP, or dashboard.

## Local-model comparison

Baseline 0004 adds an optional direct-loopback Ollama evaluation adapter. The measured `llama3.2:3b` candidate was excluded after only 5 of 54 outputs passed the exact parser; exact trajectory and `pass^3` were both 0.0. The deterministic control remains the default. Zero accepted model proposals and zero attack actions demonstrate fail-closed enforcement, not useful model safety.

The repository never downloads a model or supplies tools, credentials, approvals, or execution authority. See `artifacts/verification/model-source-gate-baseline-0004.json`, `artifacts/evaluations/baseline-0004-comparison.json`, and ADR 0003 for the exact source gate, evidence, and decision.

Container packaging is currently deferred. Three official Python base candidates failed the baseline source gate; see `artifacts/verification/container-source-gate.json`. The native Python workflow is the only accepted runtime for this checkpoint.

## Security boundary

This baseline operates only on a deterministic synthetic SRE environment. It contains no connectors, secrets, credentials, arbitrary command execution, or access to real infrastructure. MCP exposes diagnostic and proposal tools only; execution requires a separate human approval token that is never returned to the agent.

See `docs/status.md`, `docs/architecture.md`, `docs/threat-model.md`, and `docs/evaluation-contract.md` for current project truth.
