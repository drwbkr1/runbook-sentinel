# ADR 0005: Prioritize project-classified evidence within bounded retrieval

- Status: accepted for BASELINE-0008 evaluation
- Date: 2026-08-07
- Decision owner: Runbook Sentinel technical, AI-systems, and reliability director under the active milestone authority

## Context

The released `lexical-token-overlap-v1` retriever ranks every document kind in one top-4 list and applies only a small telemetry bonus. Every v0.0.7 case contained at most two documents, so recall@4 remained 1.0 without testing competition for the retrieval budget. The frozen BASELINE-0008 development stressor proves that five query-matching, instruction-bearing runbooks displace all expected telemetry, causing a safe but incorrect request for evidence and preventing the intended bounded proposal.

Document prose is untrusted. The project assigns `telemetry` and `status` kinds outside the model; real intake would require authenticated provenance and classification before this policy could apply. Kind priority therefore does not make content authoritative and does not replace freshness, conflict, allowlisted-fact, policy, approval, executor, idempotency, replay, or postcondition checks.

## Decision

Retain the exact lexical scoring and deterministic tie-breaking from v1. For `evidence-priority-lexical-v2`, partition positively scored documents by project-assigned kind, fill the bounded result from `telemetry` and `status` first, and then fill remaining slots from all other kinds. Keep the v1 configuration callable for experimental comparison. The default candidate changes only retrieval order; it does not inspect scenario IDs, expected outcomes, actions, or terminal states.

The evaluator separately grades frozen project-evidence recall@4, decision-evidence retention, guidance saturation, exact behavior retention, development and held-out stress results, generation, proposals, real tool trajectories, terminal state, policy, benign utility, attack success, repeated reliability, latency, and cost. The held-out pair is not implementation feedback.

## Alternatives considered

- Increase the retrieval limit: rejected because it hides rather than measures bounded-resource contention and increases untrusted context exposure.
- Filter out all runbooks before retrieval: rejected because it destroys the retained retrieval audit and prevents later evidence-backed comparison of guidance utility.
- Add dense or hybrid retrieval: deferred because it would introduce external models, dependencies, source gates, and non-determinism before the lexical failure is addressed.
- Tune query terms or scenario-specific weights: rejected as test fitting.

## Consequences

The candidate should retain required project evidence under the frozen five-document flood while leaving three result slots available for auditable guidance. A compromised or incorrect upstream kind assignment remains a security risk and is an explicit non-claim. The candidate is selected only if repeated development and sealed held-out evidence show a Pareto improvement without regression in authority, security, reliability, latency, or cost.
