# ADR 0030: Bridge frozen retrieval identities across checkpoints

- Status: accepted for BASELINE-0034 correction freeze
- Date: 2026-08-23

## Context

The first local v5 implementation passed its own frozen development-equivalence contract, kept v3 selected, and created no benchmark or comparison result. The complete 131-test regression nevertheless stopped with five failures and five derivative readjudication errors. BASELINE-0031 and BASELINE-0033 validators correctly recognized that `src/runbook_sentinel/retrieval.py` no longer matched their released hashes, but they had no fail-closed rule for an explicitly governed later retrieval successor.

Treating those failures as harmless would weaken release identity. Rewriting the historical v4 result or v0.0.33 release contract would erase useful evidence. Shipping v5 with failing predecessor contracts is not credible.

## Decision

Add a narrow predecessor-successor lifecycle bridge before reattempting runtime implementation. The bridge preserves the exact released retrieval identity and accepts a later file only when all of these are true:

1. The file is the precomputed 6,079-byte v5 candidate at SHA-256 `f5514cb7...`.
2. The public correction receipt exists and binds the exact bridge implementation.
3. V3 remains default before complete selection evidence.
4. V4 remains installed and v5 returns the exact same development IDs and order without loading held-out scenarios.
5. Benchmark and comparison results obey their frozen lifecycle.

The historical reports, traces, contracts, results, dispositions, release bytes, and selected-default evidence do not change. Only the three validators that currently emit the identity stops and their focused tests may gain the bridge. Unknown hashes, missing receipts, behavior mismatch, premature promotion, and malformed results fail closed.

## Consequences

The bridge is a prerequisite correction, not a second product improvement. Runtime bytes remain at the released v0.0.33 identity until the bridge freeze and implementation are each public and reconciled. The retained 131-test failure remains non-positive evidence. This adds checkpoint lifecycle machinery, but it avoids weakening frozen history or pretending a current source tree is byte-identical to an older release.
