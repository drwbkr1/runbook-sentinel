# Roadmap

## Active checkpoint baseline-0015 - approval authority truth

Public v0.0.14 exposed an unauthenticated caller-declared approval actor. The explicitly approved baseline-0015 candidate now requires one project-specific per-launch `Sentinel-Capability` before approval-body parsing, rejects caller identity, derives the persisted launch identity server-side, and labels the boundary `authenticated external operator`. The raw capability remains outside the agent, model, MCP, arguments, environment, repository, package, persistence, audit, traces, logs, evaluation records, and dashboard. All 24 tests, 51-file manifest checks, source/package 84+9+6+10 evaluations, bounded MCP, real approval/executor/state/telemetry surfaces, 28-entry byte-identical archive builds, rendered dashboards, and no-alternates clean-clone gates pass. Baseline 0015 now proceeds at UNIT-005 for review and public release verification; public v0.0.14 remains authoritative until those gates pass.

## Completed checkpoint baseline-0014 - idempotency cache authorization

A fresh run of the verified public v0.0.13 package passed all existing gates, but a real API probe showed that the same-proposal idempotency cache returned an exact completed execution result for wrong or missing approval tokens. The released calls caused no second mutation, yet they disclosed protected result data and returned false authorization success. Baseline 0014 freezes six development and held-out real-API cases, requires a matching consumed approval before cached-result disclosure, preserves the original completed retry even after expiry, and exact-grades state, audit, trace, replay, and split outcomes separately. Version-bound source/package, no-alternates clone, GitHub review, merged-main, selected-asset, downloaded-byte, and rendered-public gates pass. The bounded work does not change the agent, retrieval, actions, capabilities, executor, storage schema, dependencies, credentials, or synthetic-only infrastructure boundary. The next checkpoint remains intentionally unchosen until a fresh run of public v0.0.14 exposes the next measurable weakness.

## Completed checkpoint baseline-0013 - approval lifetime integrity

The verified public v0.0.12 package and fresh 84-attempt trace exposed a gap where invalid approval lifetimes were accepted before mutation, leaving an approved proposal with an already-expired token and no recovery path. Baseline 0013 enforces a JSON integer from 1 through 300 seconds outside the model, rejects invalid values before proposal, approval, audit, trace, or incident mutation, and exact-grades nine frozen development and held-out cases separately from the existing scenario evaluation. Source, package, no-alternates clone, GitHub review, merged-main, selected-asset, downloaded-byte, and rendered-public gates pass while the agent, retrieval, capabilities, executor, idempotency, replay, postconditions, synthetic-only scope, and prior release boundaries remain unchanged. The next checkpoint remains intentionally unchosen until a fresh run of public v0.0.13 exposes the next measurable weakness.

## Completed checkpoint baseline-0001 - deterministic control

Establish repository governance, a deterministic SRE environment, bounded control agent, approval/executor boundary, API, MCP server, dashboard, persistence, telemetry, frozen exact evaluation, container path, and clean-clone verification.

## Completed checkpoint baseline-0002 - topology coverage

Expand the frozen exact suite from 9 to 16 cases, cover all eight declared SRE topology domains, add explicit coverage grading, and close adjacent non-action diagnostic gaps without adding executor capabilities.

## Completed checkpoint baseline-0003 - retrieval boundary comparison

First compare the accepted full retrieved context with a standard-library evidence-only decision context while retaining full retrieval audit. Measure required evidence recall, exact utility, instruction-bearing attack-document exposure, action attack success, repeated reliability, latency, and cost separately. Dense or hybrid retrieval remains gated on external-source approval.

## Completed checkpoint baseline-0004 - local model adapter

The exact Ollama 0.32.5 and Llama 3.2 3B Instruct Q4_K_M local artifacts passed identity, license, acceptable-use, integrity, fitness, privacy, and security review for synthetic-only evaluation. The typed loopback-only candidate completed its frozen comparison and was excluded: exact trajectory and `pass^3` were 0.0, with 5 valid parses in 54 attempts. The adapter remains research infrastructure and the deterministic control remains the default.

## Completed checkpoint baseline-0005 - exact terminal-state grading

The frozen 54-trial evaluation replaces the generation-proxy tool-trajectory score with isolated synthetic approval/execution trajectories and exact terminal-state grading. Selected attempt 004 passed all development, held-out test, policy, terminal attack, approval-boundary, action-coverage, no-mutation, postcondition, idempotency, replay, audit, trace, and `pass^3` gates. Real surfaces, a no-local-object clone, GitHub review, and merged `main` passed; approval material remains outside the agent and model.

## Completed checkpoint baseline-0006 - thesis-condition coverage

Explicitly classify complete, incomplete, stale, conflicting, and instruction-bearing evidence; require every condition and adversarial coverage in both development and held-out splits; and add only the two missing development cases. The selected 60-trial candidate passes the new fail-closed coverage gates without changing the agent, action set, or authority boundary. Versioned real surfaces, clean-clone verification, GitHub review, and merged `main` pass; the release remains synthetic-only and research-informed.

## Completed checkpoint baseline-0007 - controlled evidence relations

Replace aggregate-only condition coverage with exact controlled relations. Freeze instruction-injection invariance and fresh-to-stale directional safety in both development and held-out splits, then grade paired outcomes, actions, trajectories, and terminal states without changing the agent, retriever, action set, or authority boundary.

## Completed checkpoint baseline-0008 - guidance-flood retrieval resilience

Make retrieval measurement discriminating by adding development and untouched held-out cases where five query-matching untrusted guidance documents compete with trusted project evidence under the frozen top-4 limit. Retain a pre-change `lexical-token-overlap-v1` failure, then compare one generic evidence-priority lexical candidate. Select it only if trusted project evidence, exact benign utility, security boundaries, repeated reliability, latency, and cost form a measured Pareto improvement. The agent, three-action surface, approval/executor boundary, deterministic offline default, and real-infrastructure prohibition remain unchanged.

The selected `evidence-priority-lexical-v2` checkpoint passed 78 frozen trials, all six stress attempts, real CLI/API/MCP and execution-boundary verification, a clean clone, GitHub review, merged-main verification, and public release reconciliation. The next checkpoint is intentionally unchosen until a fresh run of public v0.0.8 exposes the next measurable weakness.

## Completed checkpoint baseline-0009 - stale-evidence retrieval resilience

The fresh v0.0.8 run passed, but a bounded development probe showed that five stale, query-matching telemetry records can consume all four v2 retrieval positions and crowd out the current telemetry needed for a useful action proposal. Schema 1.8 freezes one development and one sealed held-out pair, exact behavior and terminal state, independent stale-evidence validation, and separate retrieval, utility, security, reliability, latency, and cost gates.

`freshness-priority-lexical-v3` is selected as the only configuration passing the stale-evidence hard gates across three same-manifest 84-trial runs. Retained v2 comparisons remain `remediate`. The selection records a small local common-case latency increase and therefore makes no strict Pareto-dominance or general performance claim. Version-bound, native-surface, clean-clone, GitHub, merged-main, tag, release, and public-artifact verification pass. The next checkpoint remains intentionally unchosen until a fresh run of public v0.0.9 exposes the next measurable weakness.

## Completed checkpoint baseline-0010 - stale-payload decision boundary

The fresh v0.0.9 run passed but showed that the released decision context still forwards stale project titles and content to the agent/model boundary. Those payloads are unnecessary for exact replacement-evidence requests and enlarge the attack surface. Schema 1.9 freezes one development and one sealed held-out projection case, exact field-level requirements, complete fresh-payload retention, and unchanged behavior.

`fresh-content-stale-metadata-context-v3` is selected as the only hard-gate-passing configuration across six same-manifest 84-trial runs. It retains complete retrieval records for audit, passes full fresh records to the decision context, and projects stale records to `id`, `kind`, and `observed_at`. Retained v2 controls expose stale payloads and remain `remediate`. Version-bound, native-surface, clean-clone, GitHub, merged-main, tag, release, and rendered-public verification pass. The selection is a security-gated Pareto-frontier choice, not a strict latency, production-readiness, or external-system superiority claim. The next checkpoint remains intentionally unchosen until a fresh run of public v0.0.10 exposes the next measurable weakness.

## Stopped checkpoint baseline-0011 - first portable package candidate

The public v0.0.10 run passed every existing system gate, but its release had no portable package asset. BASELINE-0011 froze an exact standard-library zipapp contract, retained a nondeterministic default-zipapp control, produced byte-identical clean candidate archives, and passed source/package evaluation parity and packaged MCP. The candidate was stopped and never published after the first packaged real-surface reveal passed 49 of 50 checks but rendered `Baseline 0010` while health and evaluation reported baseline-0011. The candidate and contract were not changed after reveal.

## Completed checkpoint baseline-0012 - canonical package and rendered identity

Treat the BASELINE-0011 dashboard mismatch as a known regression, not held-out evidence. Create a new v0.0.12 candidate whose dashboard and source test derive the rendered checkpoint from one canonical runtime value. Preserve the agent, retrieval, decision-context, policy, approval, executor, scenario, synthetic-split, and real-infrastructure boundaries. A pre-merge audit stopped promotion after detecting impossible future-dated provenance metadata; the earlier functionally passing candidate and clean-clone receipt remain retained as superseded. The corrected local and renewed no-local-object clean-clone source/package, package reproducibility, MCP, HTTP/dashboard, state, telemetry, visual, and byte-rebuild gates pass. GitHub review, merged-main verification, selected release assets, downloaded public-byte identity, annotated tag, and rendered public pages pass. The next checkpoint remains intentionally unchosen until a fresh run of public v0.0.12 exposes the next measurable weakness.

## Research preview v0.1.0

Expand to at least 48 frozen cases across the approved SRE topology, meet precommitted security and utility gates, verify all real surfaces, and release only with a reconciled evaluation report and explicit repository visibility decision.
