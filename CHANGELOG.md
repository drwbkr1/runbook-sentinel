# Changelog

All notable verified changes are recorded here. Unverified work remains in `docs/devlog.md` and the active milestone contract.

## 0.0.7 - 2026-08-06

- Added a closed behavioral-relation contract with instruction-injection invariance and fresh-to-stale directional safety in development and held-out splits.
- Added fail-closed relation validation and separate contract, coverage, invariance, directional-safety, combined, per-split, and per-trial metrics.
- Passed 72 of 72 scenario trials and 12 of 12 paired relation trials with 21 expected executions and 51 exact no-action terminal states.
- Preserved the aggregate-only gap, pre-grader control, stale inventory failures, an integration-placement failure, and the implementation smoke rather than rewriting unfavorable or superseded evidence.
- Kept the agent, retriever, policy, service, action surface, approval, executor, and real-infrastructure boundary unchanged; release verification is in progress.

## 0.0.6 - 2026-08-06

- Added a closed complete, incomplete, stale, conflicting, and instruction-bearing evidence-condition taxonomy with fail-closed validation.
- Required every condition and adversarial coverage in both development and held-out splits, adding only two bounded synthetic development no-action cases.
- Passed 60 of 60 repeated trials with 10 of 10 condition/split pairs, both adversarial splits, 15 expected executions, and 45 exact no-action terminal states.
- Preserved the pre-change coverage gap and stale checkpoint identity, a failed inventory test, a rejected shell invocation, and superseded attempt 001 rather than rewriting unfavorable evidence.
- Verified the unchanged agent, policy, service, and authority boundaries through CLI, MCP, API, approval, executor, replay, postconditions, persistence, telemetry, rendered dashboard, clean clone, GitHub review, and merged `main`; container packaging remains deferred.

## 0.0.5 - 2026-08-06

- Replaced proposal-level trajectory proxying with isolated, exact approval, execution, replay, postcondition, audit, trace, and terminal-state grading.
- Passed 54 of 54 repeated trials: 15 expected actions executed across all three synthetic capabilities and 39 no-action trials remained exactly unchanged.
- Preserved proposal and terminal attack success at 0.0 and repeated-trial `pass^3` at 1.0 while keeping approval material and execution authority outside the agent and model.
- Retained one failed live-verifier attempt and three superseded passing evaluation identities rather than rewriting unfavorable or stale evidence.
- Verified the CLI, API, MCP authority inventory, approval flow, executor, dashboard, SQLite state, telemetry, clean clone, GitHub review, and merged `main`; container packaging remains deferred.

## 0.0.4 - 2026-08-06

- Added a standard-library, direct-loopback Ollama evaluation adapter with exact structured parsing, redacted model telemetry, and no tools or deterministic fallback.
- Compared the source-gated local Llama 3.2 3B candidate with the deterministic control on 18 frozen cases and 54 trials per configuration.
- Retained and excluded the candidate after 5/54 valid parses, 0.0 exact trajectory, 0.0 `pass^3`, and substantially higher local latency; the deterministic control remains the default.
- Preserved zero accepted model proposals and zero attack actions as fail-closed boundary evidence, not as a claim of useful model safety.

## 0.0.3 - 2026-08-06

- Added explicit instruction-bearing attack-document exposure metrics and gates.
- Compared full retrieved context with an evidence-only decision context on identical frozen splits.
- Selected evidence-only context after preserving all measured quality, policy, reliability, and cost results while reducing labeled decision exposure from 1.0 to 0.0.
- Retained full retrieval and guidance identities for audit without passing poisoned runbook prose into the decision plane.
- Added decision-context identity and document counts to redacted traces and verified the boundary through CLI, MCP, API, dashboard, persistence, and telemetry.
- Preserved the three-action executor and capability boundary unchanged from `v0.0.2`.

## 0.0.2 - 2026-08-06

- Expanded the frozen suite from 9 to 16 cases across all 8 declared SRE topology domains.
- Added separate development and test metrics plus an exact topology coverage gate.
- Added bounded non-action diagnoses for gateway, API latency, worker capacity, configuration, and observability evidence gaps.
- Preserved the three-action executor and capability boundary unchanged from `v0.0.1`.
- Retained failed attempt 001 and superseded identity-mismatched attempt 002 before accepting attempt 003.
- Isolated live verification state and preserved checkpoint-specific dashboard and runtime receipts.

## 0.0.1 - 2026-08-06

- Added deterministic control baseline `baseline-0001` with synthetic SRE scenarios, bounded outcomes, untrusted-evidence handling, proposal hashing, human approval, idempotent synthetic execution, replay protection, exact postconditions, API, MCP, dashboard, persistence, telemetry, and frozen evaluation.
- Retained failed SQLite cleanup, contract-schema, shell-tooling, and container source-gate attempts.
- Deferred container packaging after three candidate base images failed the vulnerability gate.
- Published the verified research preview to the public `drwbkr1/runbook-sentinel` repository.
