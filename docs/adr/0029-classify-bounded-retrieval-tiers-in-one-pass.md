# ADR 0029: Classify bounded retrieval tiers in one pass

- Status: accepted for BASELINE-0034 contract freeze
- Date: 2026-08-23

## Context

Verified public v0.0.33 is the exact starting checkpoint. A fresh run from its reconciled public-main bytes passes 57 scenarios, 171 attempts, all 136 Boolean gates, and an anchored 261-event trace. Retrieval, generation, tool trajectory, policy, terminal state, benign utility, repeated-trial reliability, and cost remain separately reported and exact. Proposal and terminal attack success remain zero.

The highest-leverage measured product weakness is still returned-context breadth. Selected `freshness-priority-lexical-v3` returns 123 additional untrusted record instances across 87 of 153 eligible attempts, with mean expected-document share 0.683006535948. Retained and admissible `bounded-trust-tier-lexical-v4` reduces the extra count to 93 and improves the share to 0.709150326797 without changing required evidence, ranks, behavior, policy, utility, attacks, reliability, or cost. It remains excluded because its retained one-shot whole-system median is 65.443 ms versus 64.377 ms for v3.

V4 ranks once, but then evaluates the freshness predicate twice for every project-evidence item: once while constructing the fresh tier and again while constructing the stale tier. That predicate reparses the same `as_of` timestamp and each document timestamp on both calls. A development-only diagnostic reference parses `as_of` once, parses each eligible project-evidence timestamp once, and classifies the item once. It returns exactly the v4 document IDs across all 31 development scenarios. In a balanced 120-round, 2,480-call-per-round diagnostic it measured 17,006.028 ns per call versus 19,899.859 ns for current v4, a 14.542% reduction. This diagnostic is not selection evidence and does not repair the historical latency result.

Current official Python 3.12 documentation supports the existing timezone-aware `datetime.fromisoformat` semantics and `perf_counter_ns` for high-resolution monotonic short-duration measurement. The source gate imports no external code, data, model, prompt, metric package, or benchmark.

## Decision

Freeze one experimental configuration, `single-pass-bounded-trust-tier-lexical-v5`. Preserve v4 lexical scoring, telemetry bonus, document-ID tie breaking, tier order, caps, no-backfill rule, four-document maximum, returned record shape, and decision-context projection. Parse the request `as_of` once and classify each eligible project-evidence item exactly once. Do not add a cross-request cache: scenario documents are mutable dictionaries loaded anew, and caching would introduce identity, invalidation, memory, and stale-state risks unrelated to this improvement.

Publish and anonymously reconcile this preimplementation freeze before v5 exists in runtime code. Keep v3 as the product default until a frozen comparison completes. The held-out split cannot be inspected or used for optimization.

Selection requires all of the following:

1. v5 returns exactly v4's document IDs and ranks on both frozen splits;
2. development focus strictly improves over v3 and all required evidence remains complete on both splits;
3. the exact five selected-v3 observational fingerprints may differ only under the already frozen candidate-admissibility rules, while all other 131 Boolean gates pass;
4. scenario, generation, tool trajectory, policy, terminal state, benign utility, proposal and terminal attack success, repeated-trial reliability, and cost do not regress;
5. five independently launched development-only retriever benchmarks each have zero v4/v5 ID mismatches, v5 is faster in each, and their median ratio is at most 0.95; and
6. a balanced six-report whole-system sequence (`v3`, `v5`, `v5`, `v3`, `v3`, `v5`) has candidate aggregate median, p95, and diagnosis median no greater than control at recorded precision.

Only after these gates pass may a separate identity-bound transition change the default and update selected-default conformance records. The promoted default must then pass all 136 Boolean gates on source, package, clean-clone, and local-container surfaces. If any gate fails or is inconclusive, retain v5 and all evidence as excluded, keep v3 selected, and do not release the candidate as a Pareto improvement.

## Consequences

- The candidate changes one runtime implementation path and no model, agent, prompt, decision projection, policy, approval, executor, credential, capability, authorization, scenario, split, or grader boundary.
- Whole-system latency remains distinct from retriever microbenchmark latency; neither may rescue failure in the other.
- V4's unfavorable retained result remains immutable.
- No dependency, cache, multi-agent design, fine-tuning, Kubernetes, external asset, secret, paid service, or real-infrastructure connection is introduced.
- The release remains synthetic-only and research-informed. Exact synthetic ID focus is not exhaustive semantic relevance, broad production performance, or universal prompt-injection resistance.
