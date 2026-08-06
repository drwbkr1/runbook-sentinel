# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0001-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765/dashboard`.

The MCP server uses JSON-RPC over standard input/output:

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel mcp --db var/mcp.db
```

Container packaging is currently deferred. Three official Python base candidates failed the baseline source gate; see `artifacts/verification/container-source-gate.json`. The native Python workflow is the only accepted runtime for this checkpoint.

## Security boundary

This baseline operates only on a deterministic synthetic SRE environment. It contains no connectors, secrets, credentials, arbitrary command execution, or access to real infrastructure. MCP exposes diagnostic and proposal tools only; execution requires a separate human approval token that is never returned to the agent.

See `docs/status.md`, `docs/architecture.md`, `docs/threat-model.md`, and `docs/evaluation-contract.md` for current project truth.
