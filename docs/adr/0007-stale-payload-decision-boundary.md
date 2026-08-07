# ADR 0007: Stale-payload decision boundary

- Status: Accepted for the baseline-0010 release candidate
- Date: 2026-08-07

## Context

The public v0.0.9 release uses freshness-priority retrieval and prevents stale records from supplying facts to the bounded agent. A fresh 84-trial orientation still exposed 2,913 stale title/content characters at the agent/model decision boundary across 15 attempts. The stale record IDs and timestamps remain useful for exact replacement-evidence requests, so dropping the records completely would reduce utility.

CaMeL and StruQ passed the 16-criterion baseline-0010 source gate for citation and narrow paraphrase. They support separating untrusted data from control flow and using structured boundaries. This project imports no external paper, code, data, model, dependency, executable, or service and does not implement either system.

## Decision

Keep `evidence-only-context-v2` callable for comparison and select `fresh-content-stale-metadata-context-v3` as the default candidate. Full retrieved records remain on the audit plane. Fresh project-classified telemetry and status enter the decision context with all fields intact. Stale project records enter with exactly `id`, `kind`, and `observed_at`; `title` and `content` are omitted. The optional model adapter serializes only fields present and cannot reconstruct removed payload.

Freshness continues to use the scenario's explicit `as_of` and shared fail-closed one-hour predicate. Missing, malformed, timezone-naive, or future timestamps receive stale treatment. The projection cannot inspect scenario IDs, expected results, actions, trajectories, or terminal states.

## Consequences

- Across six same-manifest 84-trial runs, v3 is the only configuration that passes every frozen projection, correctness, policy, utility, security, reliability, and cost gate.
- V2 remains retained with `remediate`: it preserves behavior but exposes stale payload in every projection case.
- Full stale content remains available for audit and incident investigation outside the agent/model boundary. Its identity and timestamp remain available for exact replacement requests.
- Strict numeric Pareto and latency dominance are false. V3 is selected as a security-gated Pareto-frontier choice with the measured local latency tradeoff explicit.
- Real metadata is not inherently trustworthy. Any future connector must authenticate and normalize source identity, kind, timestamp, provenance, and custody outside the model.
- The agent purpose, action set, model default, policy, approval and executor boundary, MCP/API authority, dependency set, cost, and real-infrastructure prohibition do not change.
