# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

Latest verified public release: `v0.0.18`. It adds a closed 17-code model-output failure taxonomy without accepting more output or changing authority. The frozen 19-case reveal is exact. A same-manifest comparison classifies all 75 rejected local-model outputs, but the measured model still has diagnosis accuracy, benign utility, and `pass^3` of 0.0 and is excluded; deterministic control remains the default. The selected dependency-free 33-entry zipapp is 410,293 bytes at SHA-256 `e370c208bc6598cf6217f963bc6ea567f05df5757a371bda67fc5157e23a21d0`. Candidate `v0.0.11` remains rejected and unpublished with its stale rendered-label failure preserved. Public source or package availability does not imply production readiness or authorization to connect Runbook Sentinel to operational infrastructure.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

The selected freshness-priority lexical retriever first preserves externally project-classified telemetry and status that pass a fail-closed one-hour freshness rule, then ranks stale project evidence and untrusted guidance. Full returned records remain available for audit. The decision context receives complete fresh telemetry/status records and projects stale records to exactly `id`, `kind`, and `observed_at`; stale `title` and `content` never cross that boundary. Missing, malformed, naive, or future timestamps never receive fresh treatment. Runbook prose never grants authority.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0018-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

The server requests the per-launch operator capability through a hidden prompt. Enter the same high-entropy capability at the hidden prompt used by the separate `approve --proposal <id>` command; neither command accepts the capability as an argument or environment variable. Then open `http://127.0.0.1:8765/dashboard`.

Build and verify the standard-library-only zipapp without installing a build backend or dependency:

```powershell
python scripts/build_zipapp.py
python scripts/verify_package_contract.py --contract eval/package-contract-0018.json --archive dist/runbook-sentinel-0.0.18.pyz
python dist/runbook-sentinel-0.0.18.pyz --help
```

The builder uses an exact 33-entry allowlist, fixed ZIP metadata, an embedded frozen evaluation manifest, and a package manifest containing per-entry hashes. Repeated builds must be byte-identical. No package-registry or container claim is made.

The MCP server uses JSON-RPC over standard input/output:

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel mcp --db var/mcp.db
```

## Stale-payload, stale-evidence, retrieval-stress, behavioral-relation, and terminal-state evaluation

Baseline 0010 adds frozen development and held-out cases that require stale identity retention without stale payload exposure. Across six same-manifest 84-trial runs per configuration, `evidence-only-context-v2` exposes stale title/content in every projection case and remains `remediate`; `fresh-content-stale-metadata-context-v3` retains stale identity and timestamp, removes stale payload, preserves complete fresh records and exact behavior, and passes every hard gate. All earlier retrieval, generation, trajectory, terminal-state, policy, utility, security, reliability, cost, and coverage metrics remain exact. The local comparison does not show strict numeric Pareto or latency dominance; v3 is a security-gated Pareto-frontier choice with the small measured latency tradeoff recorded.

The harness runs only after the agent result exists, holds approval material only in disposable evaluation state, and is not exposed by the agent, CLI runtime, API automation, MCP, or dashboard.

## Local-model comparison

Baseline 0004 adds an optional direct-loopback Ollama evaluation adapter. The measured `llama3.2:3b` candidate was excluded after only 5 of 54 outputs passed the exact parser; exact trajectory and `pass^3` were both 0.0. The deterministic control remains the default. Zero accepted model proposals and zero attack actions demonstrate fail-closed enforcement, not useful model safety.

The repository never downloads a model or supplies tools, credentials, approvals, or execution authority. See `artifacts/verification/model-source-gate-baseline-0004.json`, `artifacts/evaluations/baseline-0004-comparison.json`, and ADR 0003 for the exact source gate, evidence, and decision.

Container packaging remains deferred. Docker is currently off, and three previously reviewed official Python base candidates failed the source gate; see `artifacts/verification/container-source-gate.json`. The source workflow and independently verified dependency-free zipapp are the only candidate runtimes for this checkpoint.

## Security boundary

This baseline operates only on a deterministic synthetic SRE environment. It contains no connectors, arbitrary command execution, or access to real infrastructure. MCP exposes diagnostic and proposal tools only. Approval creation requires a separate per-launch external-operator capability that is never returned to the agent, model, or MCP; the resulting approval token remains action-bound, hashed at rest, one-time, and separate from final execution authority.

See `docs/status.md`, `docs/architecture.md`, `docs/threat-model.md`, and `docs/evaluation-contract.md` for current project truth.
