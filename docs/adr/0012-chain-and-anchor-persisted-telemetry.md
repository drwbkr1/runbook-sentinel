# ADR 0012: Chain and anchor persisted telemetry

- Status: accepted; candidate verification passing
- Date: 2026-08-08
- Checkpoint: baseline-0016

## Context

The public v0.0.15 trace is valid line-delimited JSON but has no sequence or digest continuity. Changing an execution event from verified to failed postconditions leaves a parseable stream and does not change the completed evaluation disposition. The report also contains no identity for its companion trace.

## Decision

Each `trace-chain/v1` event carries a contiguous one-based sequence, the preceding event digest, and a SHA-256 digest over exact canonical JSON for every field except the digest itself. The genesis predecessor is 64 zeroes. A writer validates every existing nonempty event before append, refuses a corrupt prefix, and resumes from the exact next sequence and final digest. A completed evaluation records the companion trace event count and final event digest; an independent verifier requires both to match.

Canonical JSON uses UTF-8, sorted keys, compact separators, ASCII escaping, and rejects non-finite numbers. The implementation uses only the Python 3.12 standard library.

## Consequences

Uncoordinated content changes, insertion, deletion, duplication, reordering, malformed records, and anchored tail truncation become detectable under the frozen cases. Source and packaged evaluations can bind their exact, runtime-varying traces without requiring identical trace bytes.

This unkeyed chain does not authenticate the writer and cannot resist an attacker who can recompute the chain and its external anchor. It is not a digital signature, immutable storage, non-repudiation, an external collector, or RFC 5848 conformance. Adding a key, signer, credential, collector, or real-infrastructure integration remains outside this decision.
