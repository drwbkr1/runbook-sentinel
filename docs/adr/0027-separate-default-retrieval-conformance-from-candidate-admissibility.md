# ADR 0027: Separate default retrieval conformance from candidate admissibility

- Status: accepted for BASELINE-0033 contract freeze
- Date: 2026-08-22

## Context

Verified public v0.0.32 is the exact starting checkpoint. Its fresh public-tag run passes 57 scenarios, 171 attempts, all 136 Boolean gates, and an anchored 261-event trace. Required evidence, generation, trajectory, policy, terminal state, benign utility, and repeated-trial reliability are exact; proposal and terminal attack success are zero. The selected/default retriever is still `freshness-priority-lexical-v3`.

The leading measured product weakness also remains: 87 of 153 eligible attempts carry 123 additional untrusted records, and mean expected-document share is 0.683006535948. Retained `bounded-trust-tier-lexical-v4` reduces those records to 93 and improves expected-document share to 0.709150326797 while preserving every required evidence ID and rank, downstream behavior, policy, utility, attack outcome, and repeated-trial result.

The retained comparison nevertheless rejects v4 partly because the full baseline gate set contains five exact v3 observational fingerprints. V4 changes guidance retrieved/not-retrieved counts, guidance ranks, expected-document share, and three retrieval-stage/outcome classifications. Required twenty-cell coverage remains 1.0 with no missing cell or cross-trial ambiguity; the three new classifications are safe `guidance_not_retrieved` supersets. All other 131 Boolean gates pass. Treating those five default fingerprints as universal candidate validity gates conflates release conformance with comparative evidence validity.

This does not mean v4 should be promoted. Its retained median latency is 65.443 ms versus 64.377 ms for v3, so the frozen latency non-inferiority rule still fails. V3 must remain selected.

## Decision

Add a project-authored, deterministic candidate-admissibility overlay. It reads only the exact retained v3 report, v4 report, and original comparison. It does not modify the evaluator, either report, either trace, the original contract, or the original excluded disposition.

The overlay may classify comparative candidate evidence as admissible only when:

1. the candidate's false Boolean gate inventory is exactly the five frozen v3 observational fingerprints;
2. all other 131 Boolean gates pass;
3. every required retrieval-stage cell remains covered, no required cell is missing, and cross-trial ambiguity is zero;
4. the safe-superset classification inventory equals the three frozen `guidance_not_retrieved` pairs;
5. required evidence and ranks remain exact;
6. scenario, terminal, trajectory, policy, utility, proposal and terminal attack, repeated-trial, and cost invariants remain exact; and
7. latency and cost selection rules remain separate and unchanged.

Candidate admissibility is not candidate selection. The successor result must retain the original BASELINE-0031 disposition and select v3 because median-latency non-inferiority is false. Future candidates require their own public preimplementation contract; this overlay is not a general waiver.

## Consequences

- Default-release conformance remains byte-for-byte unchanged and continues to require all 136 v3 gates.
- A non-default retriever cannot hide a policy, security, utility, terminal, trajectory, reliability, evidence, rank, coverage, ambiguity, latency, or cost failure behind the overlay.
- The original unfavorable v4 report, five false gates, remediate disposition, comparison, and exclusion remain immutable.
- The correction improves experimental validity but changes no retrieval, model, agent, policy, approval, executor, credential, authority, scenario, split, or real-infrastructure behavior.
- No dependency, external code, dataset, model, prompt, judge, service, secret, paid asset, or real-infrastructure connector is added.
- Runbook Sentinel remains synthetic-only and research-informed; no broad Pareto, semantic relevance, production-readiness, or universal-safety claim is authorized.
