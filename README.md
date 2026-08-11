# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

Latest verified public release: `v0.0.24`. It adds exactly two project-authored adversarial transforms and a fail-closed condition/outcome/split interaction metric. A held-out instruction-bearing deployment conflict must abstain, while development stale-cache poisoning must request evidence with zero stale payload exposure. All 44 cases pass three trials, all 42 prior scenario and terminal identities remain exact, all 20 semantically valid interaction cells are covered, and in-band proposal plus terminal attack success remain zero.

PR `#22` merged exact reviewed head `07cc52c329b7dfdbc3d8b68ff0783360fb55df3a` with history preserved as `3b44377b7c13a0bb8a12c20603bc14975d674d87`. Local, remote-only candidate, merged-main, and public-tag source/package evaluations, exact 222-event anchors, 27 validators, 42 tests, two-build archive reproduction, bounded MCP, real API/approval/executor/state/telemetry, parsing, scans, original-detail dashboards, selected asset downloads, and rendered public pages reconcile to the release closure. Candidate `v0.0.11` remains rejected and unpublished. Forty-four cases remain below the separate v0.1.0 target, and synthetic 20-cell coverage is not universal prompt-injection resistance. Public availability does not imply production readiness or authority to connect to operational infrastructure.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

The selected freshness-priority lexical retriever first preserves externally project-classified telemetry and status that pass a fail-closed one-hour freshness rule, then ranks stale project evidence and untrusted guidance. Full returned records remain available for audit. The decision context receives complete fresh telemetry/status records and projects stale records to exactly `id`, `kind`, and `observed_at`; stale `title` and `content` never cross that boundary. Missing, malformed, naive, or future timestamps never receive fresh treatment. Runbook prose never grants authority.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0024-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

The server requests the per-launch operator capability through a hidden prompt. Enter the same high-entropy capability at the hidden prompt used by the separate `approve --proposal <id>` command; neither command accepts the capability as an argument or environment variable. Then open `http://127.0.0.1:8765/dashboard`.

Build and verify the standard-library-only zipapp without installing a build backend or dependency:

```powershell
python scripts/build_zipapp.py
python scripts/verify_package_contract.py --contract eval/package-contract-0024.json --archive dist/runbook-sentinel-0.0.24.pyz
python dist/runbook-sentinel-0.0.24.pyz --help
```

The builder uses an exact 39-entry allowlist, fixed ZIP metadata, an embedded frozen evaluation manifest, and a package manifest containing per-entry hashes. Repeated builds must be byte-identical. No package-registry or container claim is made.

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
