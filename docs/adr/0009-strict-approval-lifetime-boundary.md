# ADR 0009: Strict approval lifetime boundary

- Status: Accepted for the baseline-0013 release candidate
- Date: 2026-08-07

## Context

The verified public v0.0.12 API coerced `ttl_seconds` with `int(...)`, and the approval broker accepted any resulting integer. A released real-API probe showed that `-1` returned HTTP 201, changed the proposal from pending to approved, and created an already-expired approval. Execution then failed as expired, while reapproval failed because the proposal was no longer pending. The incident remained open. Code inspection also showed that an arbitrarily long integer could outlive the intended short-lived authorization window.

The existing 84-attempt evaluation graded default-TTL approval, execution, idempotency, replay, postconditions, audit, trace, and exact terminal state, but it had no invalid-type, invalid-range, or lifetime-boundary cases.

## Decision

The deterministic approval broker accepts only a JSON integer, excluding booleans, from 1 through 300 seconds inclusive. Omitted TTL remains 300 seconds. The API preserves the raw JSON type instead of coercing it. Invalid values raise the exact project-authored `ValueError` and return HTTP 400 before proposal status, approval rows, approval audit events, approval trace events, or incident state can change.

Freeze nine cases before implementation: negative, above-maximum, and minimum in development; zero, fractional, string, boolean, maximum, and omitted in held-out test. Grade the real loopback HTTP API, SQLite state, audit log, JSONL trace, exact lifetime, and split results independently of the 84 scenario attempts. Retain the public v0.0.12 failure and every failed verifier attempt.

## Consequences

- A previously tolerated numeric string or fractional value is rejected instead of coerced.
- The maximum equals the existing 300-second default, so no longer-lived approval is introduced.
- Validation remains outside the agent and model; capabilities, executor actions, token hashing, idempotency, replay, preconditions, postconditions, and synthetic-only scope do not change.
- The bounded policy and cases are project-authored. No external code, data, paper, model, dependency, executable, or service is imported for this checkpoint.
- The result supports only a research-informed synthetic preview, not production reliability or safety for real infrastructure.
