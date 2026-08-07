# ADR 0010: Authorize idempotency cache disclosure

- Status: Accepted for the baseline-0014 release candidate
- Date: 2026-08-07

## Context

The verified public v0.0.13 service checks its idempotency table before it validates approval material. After one authorized execution, a real loopback API probe retried the same proposal and key with a wrong token and then with no token. Both calls returned HTTP 200 and the exact cached execution result. Persisted SQLite, audit, and JSONL trace evidence proves neither call executed or mutated the incident a second time, but each disclosed a protected result and represented the request as successfully authorized.

The existing 84-attempt evaluation grades same-key idempotency only with the original valid approval token. It therefore reports perfect idempotency while measuring no cached-result authorization boundary.

RFC 9110 is approved only for narrow HTTP authentication and response-reuse terminology. The rule below is a project inference from that terminology plus the measured application behavior, not a claim that RFC 9110 standardizes Runbook Sentinel's body-carried approval token or idempotency store. The current official IETF page labels revision 07 of the Idempotency-Key draft expired and archived, so that draft is excluded.

## Decision

Before returning a same-proposal cached execution result, the deterministic service must require the supplied approval token to hash-match a consumed approval row for that proposal. Wrong, missing, or cross-proposal approval material raises the exact existing `ApprovalError` and cannot receive the cached result.

The original consumed approval token may retrieve its exact completed result under the original idempotency key even after the approval expiry timestamp. Expiry prevents a future direct execution; it does not retroactively invalidate authorization for an already completed operation. A new key after execution remains replay-rejected.

Freeze six cases before runtime implementation and fingerprint ordered SQLite rows plus trace bytes before and after every retry. Grade authorized cache utility, unauthorized denial, no mutation, replay rejection, and both splits separately from the existing scenario evaluator.

## Consequences

- Result disclosure now requires approval authorization even though the executor is not reinvoked.
- Authorized retry semantics stay useful and deterministic across transient response loss and later retry.
- The service performs one approval lookup on same-proposal cache hits; no schema or stored-result shape changes.
- Direct execution approval expiry, action-hash validation, capability policy, postconditions, agent and MCP authority, and real-infrastructure prohibition remain unchanged.
- The expired draft and released failure remain visible rather than being rewritten as favorable evidence.
- The checkpoint remains research-informed synthetic evidence, not a production-readiness or external-system safety claim.
