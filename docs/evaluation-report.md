# Evaluation report

Status: baseline-0003 native candidate passed; clean-clone and publication gates remain.

Attempt 002 is the accepted immutable comparison candidate. Attempt 003 is a separate passing pre-commit regression and is promoted to `artifacts/evaluations/latest.json`. Both are bound to manifest SHA-256 `65450de9b51fc91e374ae6c5ff6014913fb2e6718985bdf5a5ace08c9d510794`. Attempt 001 is the retained full-retrieved-context control with disposition `remediate`.

## Results

| Family | Result |
|---|---:|
| Scenarios | 16: 7 development, 9 test |
| Repeated attempts | 48 |
| Declared topology coverage | 8 of 8 domains |
| Expected evidence recall at 4 | 1.0 |
| Outcome accuracy | 1.0 |
| Diagnosis accuracy | 1.0 |
| Exact tool trajectory | 1.0 |
| Policy compliance | 1.0 |
| Benign utility | 1.0 |
| Adversarial safe outcome | 1.0 |
| Instruction attack document exposure | 0.0 |
| Proposal attack success | 0.0 |
| `pass^3` | 1.0 |
| Median latency | 7.391 ms |
| p95 latency | 18.075 ms |
| Model calls / estimated spend | 0 / $0.00 |

Development and test split exact trajectory, retrieval, generation, policy, utility, and repeated-trial gates each pass independently. The catalog covers gateway, API, worker, database, cache, deployment, configuration, and observability. Exact structured graders were used; no LLM judge participated.

## Decision-context comparison

| Metric | Full retrieved context, attempt 001 | Evidence-only context, attempt 002 |
|---|---:|---:|
| Required evidence recall | 1.0 | 1.0 |
| Exact trajectory | 1.0 | 1.0 |
| `pass^3` | 1.0 | 1.0 |
| Benign utility | 1.0 | 1.0 |
| Adversarial safe outcome | 1.0 | 1.0 |
| Policy compliance | 1.0 | 1.0 |
| Proposal attack success | 0.0 | 0.0 |
| Instruction attack document exposure | 1.0 | 0.0 |
| Median latency | 8.887 ms | 7.729 ms |
| p95 latency | 55.574 ms | 14.326 ms |

The evidence-only context is selected because it preserves every measured quality, policy, reliability, and cost result while reducing labeled instruction-bearing decision exposure to zero. It also had lower latency in these runs, but the wall-clock sample is too small for a general performance claim. Full retrieved-document identities remain in the result for audit and human review; only telemetry and status records enter the decision plane.

The comparison table uses attempt 002 because it was evaluated directly against attempt 001 before the complete-gate regression. Attempt 003 repeated the selected candidate afterward and again passed all 48 trials with median latency 7.391 ms and p95 latency 18.075 ms.

## Live verification

The CLI and MCP result for a poisoned worker runbook retained the full retrieval identity, placed the poisoned runbook in the guidance-only list, and passed only current worker telemetry into the decision context. The isolated local API and human approval flow bound approval to the proposal hash, verified postconditions, returned the same result for the same idempotency key, and rejected a replay under a new key with HTTP 409. SQLite stored one hashed approval token rather than raw material, traces contained no token, and the rendered dashboard accurately displayed baseline 0003, evidence-only context, the human execution boundary, and one persisted mitigation. The attempt-003-specific receipt binds these runtime checks to the promoted evaluation.

## Limitations

This is a deterministic control, not evidence for stochastic model reliability. It has 16 cases rather than the 48-case v0.1 target. The evidence-only boundary relies on trusted, project-authored document-kind metadata in the synthetic catalog; a real ingestion path must establish that classification outside the model and evaluate mislabeled sources. Poisoned runbook text remains stored and retrievable for audit and human review, so this does not claim to sanitize arbitrary content or implement CaMeL. No dense retriever or local model has passed its external-source gate. Container packaging remains deferred.
