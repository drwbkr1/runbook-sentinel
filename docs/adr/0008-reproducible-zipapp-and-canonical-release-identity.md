# ADR 0008: Reproducible zipapp and canonical release identity

- Status: Accepted for the baseline-0012 release candidate
- Date: 2026-08-07

## Context

Public v0.0.10 passed its system and security gates but provided no portable release artifact. A default source-tree zipapp was not reproducible, included 17 cache entries, and could not load the frozen evaluation manifest. The first project-authored candidate corrected those package defects, but its first packaged real-surface run rendered `Baseline 0010` while health and evaluation reported baseline-0011. That v0.0.11 candidate was stopped and never published.

## Decision

Ship only a project-authored Python 3.12 zipapp built from an exact allowlist with fixed ZIP metadata, stored compression, copied source bytes, embedded frozen evaluation identity, and per-entry hashes. Verify it with a separate standard-library script that does not import the builder.

Use one canonical runtime checkpoint value for health and the rendered dashboard label. Source tests derive their expected label from that value and explicitly reject the two stale candidate labels. The known v0.0.11 failure is a regression test, not held-out evidence.

Skip public version 0.0.11. A new candidate uses version 0.0.12 and checkpoint baseline-0012. Publication requires repeated byte identity, source/package parity, clean-clone rebuild identity, and downloaded public release-asset checksum identity.

## Consequences

- The artifact is portable anywhere compatible Python 3.12 is already installed; it is not a standalone executable or container.
- No dependency, build backend, package registry, credential, connector, or execution authority is added.
- Archive bytes are intentionally uncompressed to reduce cross-runtime compression variability.
- Failed and superseded package attempts consume version and evidence history rather than being rewritten.
- Public availability remains a synthetic-only, research-informed preview and does not authorize production or real-infrastructure use.
