# Changelog

All notable verified changes are recorded here. Unverified work remains in `docs/devlog.md` and the active milestone contract.

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
