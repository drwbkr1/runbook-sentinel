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

The historical reports, traces, contracts, results, dispositions, release bytes, and selected-default evidence do not change. Only the candidate-admissibility and tier-cap validators may recognize the later current-tree identity; the release verifier remains byte-exact and is exercised against its frozen fixture. Unknown hashes, missing receipts, behavior mismatch, premature promotion, and malformed results fail closed.

## Consequences

The bridge is a prerequisite correction, not a second product improvement. Runtime bytes remain at the released v0.0.33 identity until the bridge freeze and implementation are each public and reconciled. The retained 131-test failure remains non-positive evidence. This adds checkpoint lifecycle machinery, but it avoids weakening frozen history or pretending a current source tree is byte-identical to an older release.

## Schema 1.2 fixture-phase correction

The first exact v5 retry exposed a test-only phase mismatch: the bridge correctly selected the frozen v0.0.33 release fixture, but the test passed the current implemented phase to that frozen fixture. Schema 1.2 freezes one exact replacement in `tests/test_release_identity_contract_0033.py`, from the variable `phase` argument to literal `"frozen"`, and precomputes the resulting byte identity. The immutable release verifier, both current-tree bridge validators, product runtime, selection rules, and security boundaries remain unchanged. Unknown test bytes still fail closed.

## Schema 1.2 revision 3 meta-test lifecycle correction

The first schema-1.2 implementation retry reached the exact corrected release-test identity and passed every inherited release check, but its new meta-test still assumed predecessor source bytes. Revision 3 freezes a phase-aware meta-test while retaining schema-version compatibility: when the release test is still public predecessor bytes it projects and verifies the exact corrected identity; when the release test is already corrected it validates those bytes directly. Unknown meta-test bytes fail closed. Runtime, release verifier, bridge validators, selection rules, and security boundaries remain unchanged.

## Revision 3 helper addendum

The first meta-test implementation exposed the same lifecycle assumption in the helper that proves the meta-test projection. The addendum freezes one exact phase-aware helper identity and allows the target plus helper to move together. It adds no further self-referential projection test: the independent lifecycle verifier accepts only the two precomputed identities for each path and rejects unknown bytes. Product and security boundaries remain unchanged.
