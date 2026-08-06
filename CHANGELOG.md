# Changelog

All notable verified changes are recorded here. Unverified work remains in `docs/devlog.md` and the active milestone contract.

## Unreleased

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
