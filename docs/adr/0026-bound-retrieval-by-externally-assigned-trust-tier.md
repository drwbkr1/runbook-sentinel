# ADR 0026: Bound retrieval by externally assigned trust tier

- Status: accepted for BASELINE-0031 contract freeze
- Date: 2026-08-17

## Context

Verified public v0.0.30 remains exact. A fresh public-tag run passes 57 scenarios, 171 attempts, all 136 Boolean gates, and an anchored 261-event trace. Required-evidence recall, generation, trajectory, terminal state, policy, utility, and repeated-trial reliability are each 1.0; proposal and terminal attack success remain zero.

The newly stable retrieval-quality family exposes the next product-default weakness. Among 153 attempts with frozen required evidence, all required IDs are present, but 87 attempts carry one or more additional records. The 123 additional record instances yield mean expected-document share 0.683006535948. These records are not proven irrelevant: expected IDs denote required evidence, not exhaustive relevance. They nevertheless represent measurable context width and untrusted-content exposure whose utility should be justified experimentally.

The v3 retriever ranks lexical matches, separates project evidence from untrusted guidance, then prioritizes fresh project evidence over stale project evidence and guidance. It still fills the four-record limit from a single tier. In development-only stress cases, one current evidence record can therefore be followed by three stale or untrusted records.

Recent primary RAG evaluation research already passed the project's identity, rights, integrity, fitness, reproducibility, and security gate for two narrow principles: measure retriever and generator modules separately, and expose useful-information versus noise tradeoffs. This checkpoint reuses that exact two-day-old gate. It imports no external code, metric package, prompt, judge, dataset, model, service, relevance label, or paper byte.

## Decision

Freeze one experimental retrieval configuration, `bounded-trust-tier-lexical-v4`. Preserve v3 lexical scoring and document-ID tie breaking within each externally assigned tier, then select at most:

1. two fresh project-evidence records;
2. one stale project-evidence record; and
3. one untrusted-guidance record.

Do not backfill unused tier quotas. The global maximum remains four. Project-evidence kind, timestamp, freshness, provenance, and custody must be authenticated and normalized outside the model before these tiers can be trusted. Retrieved content itself remains untrusted. Full selected records remain available for audit; the decision-context projection remains unchanged.

Development-only reference evaluation preserves every required evidence ID and its rank. Across the 28 eligible development cases and three trials, extra-document count falls from 66 to 48 and mean expected-document share rises from 0.6964285714285714 to 0.7261904761904762. The number of attempts carrying extras remains 45, so the candidate is a bounded width reduction rather than a universal focus solution.

Three simpler score filters were rejected before implementation. Ratios of 0.50 and 0.75 to the first returned score preserve complete required evidence in only 27 and 26 of 28 eligible development cases; keeping only first-score ties also preserves only 26. These results remain retained and cannot be rewritten as favorable evidence.

Publish the preimplementation freeze before adding v4. Keep `freshness-priority-lexical-v3` as the product default until same-manifest three-trial control and candidate reports exist. The held-out split cannot be used for tuning. V4 may replace v3 only if focus improves, all required evidence and ranks remain exact on both splits, every existing coverage and adversarial-stage contract passes without ambiguity, downstream behavior and utility do not regress, attack success remains zero, repeated-trial reliability remains exact, and latency and cost are non-inferior within recorded precision.

## Consequences

- The candidate directly limits worst-tier context width without changing lexical scoring, the decision projection, or any authority boundary.
- A development improvement does not predict the held-out result. Failure or non-inferiority loss will be preserved and v4 excluded.
- Guidance remains represented rather than being categorically removed, so retrieved-then-filtered adversarial coverage remains measurable.
- Exact-ID synthetic focus is not exhaustive semantic relevance, production retrieval quality, or universal prompt-injection resistance.
- No model, fine-tuning, multi-agent design, dependency, secret, paid service, external asset, or real-infrastructure connection is introduced.
