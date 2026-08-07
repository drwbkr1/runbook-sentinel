# ADR 0011: Authenticate the external operator with a per-launch capability

- Status: accepted
- Date: 2026-08-07
- Checkpoint: baseline-0015

## Context

Public v0.0.14 accepts any nonblank caller-declared `actor` on its loopback approval endpoint. A real package probe declared `sentinel-agent-self-declared`, received an approval token, executed `restart_worker`, and satisfied postconditions. The model and MCP still have no approval tool or material, but the rendered `human approval` label is not backed by authenticated identity.

The user explicitly approved the recommended architecture in Codex task `019fd836-f77d-70f3-b529-fe691c8e6de2`: “yes, implement the recommended option.” The exact response is locked and reconciled by `contracts/human-review-baseline-0015-approval-architecture.json` and `artifacts/verification/human-review-reconciliation-baseline-0015.json`.

RFC 9110 is fit for generic HTTP challenge and `Authorization` semantics. RFC 6750 requires TLS for Bearer tokens, so direct Bearer use is excluded on the current bare loopback HTTP surface. OAuth roles and flows are also excluded as unnecessary complexity. The existing Python 3.12 standard library provides the required random-token, hashing, and comparison primitives without a dependency.

## Decision

Protect only approval creation with the project-specific `Sentinel-Capability` HTTP authentication scheme. Each server launch receives one high-entropy URL-safe capability through a hidden prompt or standard input. The capability is never accepted as a command-line value, environment variable, repository or package file, database value, audit field, trace field, model input, MCP value, dashboard value, or structured log field.

The server immediately derives an in-memory SHA-256 verifier and a launch-scoped pseudonymous operator identifier using a fresh in-memory nonce. It discards its reference to the raw input after construction and compares presented verifier bytes with `hmac.compare_digest`. Exactly one matching `Authorization` field is required before the request body is parsed. Missing, wrong, malformed, Bearer, duplicate, and prior-launch credentials fail uniformly with HTTP 401 and the exact project challenge.

The approval body cannot contain `actor`; identity comes only from the authenticated server result. Persisted state, audit, and traces may record the launch-scoped `operator-[0-9a-f]{16}` identifier. The dashboard calls the boundary `authenticated external operator`, which does not claim proof of human presence.

The public `approve` CLI becomes a loopback HTTP client. It accepts no actor, reads the capability from a hidden prompt or standard input, and cannot call the approval store directly. The agent, model, and MCP continue to have no approval or execution authority.

## Consequences

- Arbitrary loopback callers can no longer create approvals by declaring an actor.
- A new server launch requires a newly supplied capability; the old launch capability is rejected by a server using a different capability.
- Raw capability exposure is confined to operator-client and server request-processing memory plus the loopback `Authorization` field in transit. Python cannot guarantee memory zeroization, and a hostile OS or compromised same-process policy component remains out of scope.
- Bare loopback HTTP does not protect against a hostile local operating system. The project makes no Bearer, OAuth, human-presence, or production-identity claim.
- Frozen development and held-out cases exact-grade authorization, body ordering, actor rejection, restart recovery, no-mutation, full approved execution, secret exclusion, and prior security boundaries before release.
