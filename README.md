# Runbook Sentinel

Runbook Sentinel is a research-informed, retrieval-grounded SRE incident agent. It is designed to remain useful, repeatable, and policy-compliant when evidence is incomplete, adversarial, conflicting, or stale.

Release checkpoint `v0.0.26` is verified and published as the current public synthetic-only research preview. It separates filtered hostile guidance, in-band hostile evidence, and adversarial cases without instruction-bearing content; adds one exact project-authored development analog; and grades the eighteen observed-valid exposure-stage/outcome/split cells fail closed. All 57 cases pass three trials, all 56 prior scenario and terminal identities remain exact, stale payload exposure is zero, and proposal plus terminal attack success remain zero.

Release checkpoint `v0.0.27` is verified and published as the current public synthetic-only research preview without changing agent behavior or authority. PR `#25` merged exact reviewed head `eb057438113573e1fdecd459b6843b7fd8902d01` with history preserved as `70d90e015b0ef0cadc8222c18113517de941d41d`; annotated tag object `610fb4be58943cd22ab6a672c7db7abf8590a2e2` peels to audited closure `02029b3045e7f90bb8590d5c6fb18ddfadffec6e`. Selected public zipapp/checksum bytes, live repository/release/tag pages, and fresh no-alternates public-tag source, downloaded-package, MCP, API, state, telemetry, dashboard, scan, and local-container paths reconcile. Three tag-source builds reproduce exact local image ID `sha256:4a29935f0b2db110d6dfad8617aea821529feb7fd6ba9e8ad70f2ab6563d84ee` on the verified Docker/Buildx/BuildKit stack. The image was not exported, pushed, or published; this is not a cross-builder or production-readiness claim.

Release checkpoint `v0.0.28` is verified and published as the current public synthetic-only research preview. It adds only fail-closed reporting that distinguishes 60 hostile-guidance attempts retrieved then filtered from 6 attempts where the declared hostile document was never retrieved; no retrieval behavior or authority changes. PR `#26` merged exact reviewed head `99ed8f96f55c994feff168252fcde0941054746b` with history preserved as `9aec054f8c97f04c36fc39685667e86c5e8d097e`; annotated tag object `5026ecff0d2351a3231ea8d340e4b330a31cc52d` peels to audited release closure `a93ad62e952421dfec2a80c396a3fb8b0e8e580a`. Selected public zipapp/checksum bytes, rendered repository/release/tag pages, and fresh no-alternates public-tag source, downloaded-package, MCP, API, state, telemetry, dashboards, scan, and local-container paths reconcile; external receipt commit `8e41963dda38d15c5d504471bdbb0a3f4f59ba57` publishes the exact result. Three tag-source builds reproduce exact local image ID `sha256:9a62f5e1daf61089ef6c9ceb71afd930c72ea60874bcec4eba78c4fc35467e2e` on the verified Docker/Buildx/BuildKit stack. The image was not exported, pushed, or published; this is not a cross-builder, production-readiness, universal-safety, or perpetual-vulnerability claim.

Candidate checkpoint `v0.0.29` adds deterministic returned-set focus, extra-record burden, hostile-document rank, conditional safety, split, and repeated-trial ambiguity reporting without changing retrieval or authority. Its immutable source candidate is public and exact; the 43-entry package contract, 45-check local-container contract, and 135-file pre-build manifest pass locally with archive and image bytes still absent until their public seal.

PR `#24` merged exact reviewed head `48eb7669582b372ef2d0c8986374fa0823133f61` with history preserved as `2fac52759e0d3f6857491f40d1958f62a85e70b4`. Annotated tag object `2c8593ec5f77ab76e12da926336dfa06b97a67eb` peels to release closure `74bf5cba93b0697e74163a335c3dbfcc4d5d7418`. Selected public assets, downloaded bytes, live repository/release/tag pages, and a fresh public-tag clone repeat 31 validators, 47 tests, two independent archive rebuilds, source/package 171-attempt evaluations with exact 261-event anchors, bounded MCP, real API/approval/executor/state/telemetry, parsing, scans, and complete dashboards. Candidate `v0.0.11` remains rejected and unpublished. Synthetic eighteen-cell coverage is not universal prompt-injection resistance or production readiness.

The bounded agent can diagnose, request evidence, propose an action, or abstain. It cannot execute actions. A deterministic approval broker, policy gate, and synthetic-only executor enforce authority outside the model.

The selected freshness-priority lexical retriever first preserves externally project-classified telemetry and status that pass a fail-closed one-hour freshness rule, then ranks stale project evidence and untrusted guidance. Full returned records remain available for audit. The decision context receives complete fresh telemetry/status records and projects stale records to exactly `id`, `kind`, and `observed_at`; stale `title` and `content` never cross that boundary. Missing, malformed, naive, or future timestamps never receive fresh treatment. Runbook prose never grants authority.

## Baseline commands

Run all commands from the repository root with Python 3.12 or newer.

```powershell
$env:PYTHONPATH = 'src'
python -m runbook_sentinel evaluate --output artifacts/evaluations/runs/baseline-0029-manual.json
python -m unittest discover -s tests -v
python -m runbook_sentinel serve --host 127.0.0.1 --port 8765
```

The server requests the per-launch operator capability through a hidden prompt. Enter the same high-entropy capability at the hidden prompt used by the separate `approve --proposal <id>` command; neither command accepts the capability as an argument or environment variable. Then open `http://127.0.0.1:8765/dashboard`.

Build and verify the standard-library-only zipapp without installing a build backend or dependency:

```powershell
python scripts/build_zipapp.py
python scripts/verify_package_contract.py --contract eval/package-contract-0029.json --archive dist/runbook-sentinel-0.0.29.pyz
python dist/runbook-sentinel-0.0.29.pyz --help
```

The v0.0.29 builder uses an exact 43-entry allowlist, fixed ZIP metadata, an embedded frozen evaluation manifest, and a package manifest containing per-entry hashes. Repeated builds must be byte-identical. The container is a digest-pinned local verification surface; no package-registry or container-image publication claim is made.

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

Container image publication remains out of scope. Docker is live for local verification, the earlier three official Python base candidates remain excluded, and one exact Chainguard digest is admitted only under the frozen local build/runtime contract. The dependency-free zipapp remains the only selected release artifact; see `artifacts/verification/container-baseline-0027.json` for the 43-of-43 local and clean-clone evidence.

## Security boundary

This baseline operates only on a deterministic synthetic SRE environment. It contains no connectors, arbitrary command execution, or access to real infrastructure. MCP exposes diagnostic and proposal tools only. Approval creation requires a separate per-launch external-operator capability that is never returned to the agent, model, or MCP; the resulting approval token remains action-bound, hashed at rest, one-time, and separate from final execution authority.

See `docs/status.md`, `docs/architecture.md`, `docs/threat-model.md`, and `docs/evaluation-contract.md` for current project truth.
