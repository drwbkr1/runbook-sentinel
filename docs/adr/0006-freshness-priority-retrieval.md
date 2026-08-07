# ADR 0006: Freshness-priority lexical retrieval

- Status: Accepted for the baseline-0009 release candidate
- Date: 2026-08-07

## Context

The public v0.0.8 `evidence-priority-lexical-v2` retriever reserves top-4 capacity for project-classified telemetry and status before untrusted guidance. A frozen development pair and sealed held-out pair show a remaining availability defect: five stale, query-matching telemetry records can consume all four positions and crowd out the current record needed for the exact useful action. The downstream agent fails safely by requesting evidence, but benign utility and expected execution are lost.

Current primary research reviewed through `artifacts/verification/research-source-gate-baseline-0009.json` supports treating outdated-document interference as a distinct retrieval problem. The project imports no external paper, code, data, model, dependency, executable, or service.

## Decision

Keep v1 and v2 callable for comparison and select `freshness-priority-lexical-v3` as the default candidate. V3 preserves lexical scoring and deterministic tie-breaking, but orders positive matches into three groups: fresh project evidence, stale project evidence, and other untrusted records. Freshness uses the scenario's explicit `as_of` and the same one-hour predicate used by the bounded agent.

The predicate fails closed. Missing, malformed, timezone-naive, or future `observed_at` values are not fresh. The rule cannot inspect scenario IDs, expected outcomes, actions, trajectories, or terminal states. Full retrieved identities remain auditable, and only externally classified telemetry/status enter the decision context.

## Consequences

- V3 is the only compared configuration that passes every frozen stale-evidence reliability gate across three same-manifest 84-trial runs.
- V2 remains retained with `remediate`; its safe request for evidence is not rewritten as success because it loses required utility.
- The comparison does not establish strict numeric Pareto dominance. On the 26 original work-equivalent cases, v3's local median diagnosis latency is 0.131 ms higher and median end-to-end latency is 4.681 ms higher. V3 is selected for hard-gate reliability with this tradeoff explicit.
- Synthetic project metadata is not evidence of real provenance. Any real connector must authenticate and normalize source identity, kind, timestamp, and custody outside the model before this priority rule can be trusted.
- The agent purpose, action set, policy, approval and executor boundary, MCP/API authority, dependency set, cost, and real-infrastructure prohibition do not change.
