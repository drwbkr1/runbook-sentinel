# ADR 0028: Release adjudicated checkpoints through an identity-only transition

- Status: accepted for BASELINE-0033 release-identity freeze
- Date: 2026-08-22

## Context

The immutable BASELINE-0033 adjudication is public and exact. It establishes that the bounded-trust-tier lexical v4 evidence is admissible for comparison, but it does not select or promote v4. Freshness-priority lexical v3 remains the product default, and the original median-latency non-inferiority failure and exclusion remain retained.

The release surfaces still identify v0.0.32 and BASELINE-0032. Advancing those labels is necessary for a truthful v0.0.33 package, API, MCP server, dashboard, container, tag, and release. It is not a second product improvement and must not become a route for changing runtime behavior or importing a new container base.

## Decision

Freeze a separate, independently verified release-identity transition before any v0.0.33 identity is implemented.

The transition permits exactly four product-source substitutions: the package version in `__init__.py`, the default evaluation output checkpoint in `cli.py`, the API checkpoint, and the MCP server version. Their predecessor and successor byte hashes are precomputed in the contract. Every other Python or JSON file under `src/runbook_sentinel` remains byte-identical, and the complete 24-file product inventory is closed against additions.

The successor package must retain the exact predecessor 43-entry allowlist, archive metadata, content exclusions, parity contract, release gates, and no-go boundaries. The successor container contract must inherit the exact v12 contract and verified receipt, reuse the same source-gated digest-pinned Chainguard base, retain its required checks and security controls, and remain local-only. No new external source access or intake is justified because the external asset identity does not change.

The mechanical transition is not sufficient for release. Source, two reproducible packages, clean clone, two local container builds, clean-clone container reconstruction, CLI, MCP, authenticated API, approval, executor, replay protection, postconditions, persisted state, telemetry, complete rendered dashboard, current image scan, audits, review, merge, tag, assets, and public surfaces must all pass independently. A missing or stale required surface stops release.

## Consequences

- Candidate evidence admissibility cannot be confused with candidate selection or a default change.
- Runtime behavior outside the four enumerated identity bytes fails closed before package or container construction.
- v0.0.33 can truthfully describe the adjudicated checkpoint while keeping the container base and all security boundaries unchanged.
- The additional freeze adds lifecycle work, but it gives the release a public, reviewable boundary before identities or artifacts exist.
