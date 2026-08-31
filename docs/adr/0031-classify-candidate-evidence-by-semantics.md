# ADR 0031: Classify retrieval candidate evidence by semantics

- Status: accepted for BASELINE-0035 contract freeze
- Date: 2026-08-31

## Context

The exact public BASELINE-0034 closure retains v5 as excluded and keeps `freshness-priority-lexical-v3` selected. A fresh v3 orientation still passes 57 scenarios, 171 attempts, all 136 Boolean gates, and an anchored 261-event trace. Required evidence, generation, trajectory, policy, terminal state, benign utility, attack outcomes, repeated-trial reliability, and zero external cost remain exact.

BASELINE-0034 nevertheless exposed an evaluation-contract reliability defect. Its candidate returns exactly the retained v4 IDs and ranks, passes the five-process benchmark, improves retrieval focus and whole-system latency, and preserves every downstream behavior and safety result. Nine of ten selection checks pass. The only failure is an exact hand-authored false-gate inventory: the frozen list expected `retrieval_quality_extra_document_attempt_rate_exact` to be false, but that observation stayed true, while `adversarial_retrieval_stage_outcome_split_contract_valid` became false because three safe `guidance_not_retrieved` stage/outcome supersets appeared. Required cells remained complete in both splits and ambiguity remained zero.

BASELINE-0033 had already established the distinction between selected-default observational conformance and candidate evidence admissibility, but only as an exact v4 overlay. BASELINE-0034 copied names into another exact inventory instead of making the distinction reusable.

Current primary RAG evaluation research supports fine-grained module diagnostics and reproducible configuration comparison; behavioral testing research supports explicit capability checks when aggregate results hide failures. Those sources do not define this project's gate categories or authorize waivers. The exact semantics and mutation oracle remain project-authored, and no external asset is imported.

## Decision

Freeze a configuration-neutral semantic classifier for comparative retrieval evidence. Five selected-v3 exact-value gates are explicitly observations, not universal candidate invariants. A sixth gate, `adversarial_retrieval_stage_outcome_split_contract_valid`, may be treated as a contextual observation only when its complete error set consists of closed stage/outcome supersets whose scenarios exist, are adversarial, pass every trial, and produce the declared outcome; required coverage must stay 1.0 in both splits, missing cells must remain empty, and ambiguity must remain zero.

Every other false Boolean gate is a hard failure. Required evidence must remain complete. The classifier cannot waive policy, attack, behavior, terminal state, trajectory, utility, reliability, trace integrity, latency, cost, coverage, ambiguity, or malformed-evidence failures. It does not choose a candidate; explicit selection rules remain separate.

Use the exact retained BASELINE-0034 reports only to prove the classifier and preserve the historical v5 exclusion. Do not modify the evaluator, retriever, scenario catalog, manifest, reports, comparison, selected default, or release. A deliberately changed selected-default observation must remain admissible when hard invariants still pass; mutations to policy, coverage, ambiguity, evidence completeness, or contextual proof must fail closed.

## Consequences

- Future comparison contracts can consume semantic categories instead of guessing an exact false-gate inventory.
- Candidate evidence admissibility remains strictly weaker than selection and cannot repair or rewrite BASELINE-0034.
- Revealed held-out evidence is used only to diagnose and verify evaluation machinery; no retriever is tuned or selected from it.
- Runtime, model, agent, prompt, policy, approval, executor, credential, capability, API, MCP, telemetry, and real-infrastructure boundaries remain unchanged.
- No dependency, external code, dataset, model, prompt, judge, service, secret, paid asset, multi-agent system, fine-tuning, or Kubernetes component is added.
- Runbook Sentinel remains synthetic-only and research-informed.
