# ADR 0024: Measure retrieval focus and attack rank before changing retrieval

- Status: accepted for BASELINE-0029 contract freeze
- Date: 2026-08-15

## Context

The verified public v0.0.28 checkpoint passes all existing retrieval, generation, trajectory, policy, terminal, utility, security, reliability, latency, cost, and real-surface gates. Its general retrieval score is nevertheless only an all-required-IDs-present rate named `expected_evidence_recall_at_4`. Every eligible case passes, so that score cannot distinguish a focused returned set from one carrying additional records.

Fresh public-tag evidence shows the difference is measurable. Fifty-one cases have one or more frozen expected evidence IDs. Across 153 attempts, every expected ID is retrieved, but 87 attempts also retrieve one or more additional records; the mean share of returned IDs that are frozen expected IDs is 0.683006535948. Separately, 30 cases declare exact hostile guidance or in-band attack-document IDs. Those documents are retrieved in 96 of 117 declared-document instances, and their first rank ranges from not retrieved through ranks 1, 2, and 3-4. Policy remains exact and proposal and terminal attack success remain zero in every observed bucket.

The current report exposes parts of this evidence through scenario details and the four-stage retrieval-stage metric, but it does not provide a deterministic retrieval-quality family suitable for comparing configurations. Changing retrieval first would allow a candidate to preserve recall while shifting extra-record burden or attack rank without an explicit Pareto surface.

Primary RAG evaluation research supports measuring retriever and generator modules separately and treating focused context as a distinct quality dimension. Runbook Sentinel adopts only that diagnostic principle. Its expected IDs are required evidence, not exhaustive semantic relevance labels, so the project will not call every other record irrelevant or import an LLM judge, metric package, benchmark, dataset, prompt, or model.

## Decision

BASELINE-0029 will add an independent, deterministic `retrieval_quality` metric family over the frozen 57-scenario, 171-attempt corpus. It will report:

1. expected-evidence case and attempt counts, all-required retrieval rate, and exact expected-document rank distribution;
2. mean expected-document share, extra-document count, and attempts carrying extra documents, using neutral names that do not assert semantic irrelevance;
3. guidance and in-band attack-document first-rank buckets (`not_retrieved`, `rank_1`, `rank_2`, and `rank_3_4`);
4. policy compliance and proposal/terminal attack success separately for each populated rank bucket; and
5. development and held-out split results plus cross-trial rank-bucket ambiguity.

Missing, malformed, duplicate, unknown, over-top-k, or non-string retrieval identities fail closed. Each report scenario must map bijectively to the catalog and contain trials 1, 2, and 3. Expected and attack IDs must be exact catalog document IDs. Mixed rank buckets across repeated trials are reported as ambiguity and fail the candidate gate.

No scenario, document, expected outcome, terminal state, retriever, ranking, decision context, agent, model, prompt, policy, approval, executor, API authority, MCP authority, dependency, external asset, secret, or real-infrastructure boundary may change.

## Consequences

Future retrieval configurations can be compared on completeness, focus, adversarial exposure rank, downstream safety, latency, and cost without collapsing them into one score. BASELINE-0029 itself is a measurement checkpoint, not a retrieval improvement. The metric remains synthetic and exact-ID based; it does not establish exhaustive relevance, production readiness, model utility, or universal prompt-injection resistance.
