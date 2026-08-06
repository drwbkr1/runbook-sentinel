# Architecture

## Baseline topology

1. A frozen scenario catalog provides a closed synthetic SRE environment, evidence, expected terminal disposition, and mutable synthetic state.
2. A deterministic lexical retriever returns evidence as untrusted data.
3. A bounded control agent extracts only allowlisted facts from fresh telemetry and status records. Retrieved prose never controls program flow.
4. The agent returns exactly one outcome: `diagnose`, `request_evidence`, `propose_action`, or `abstain`.
5. Proposals are typed, hashed, and persisted. No agent interface exposes approval or execution.
6. A human-facing API or CLI creates a short-lived approval bound to the proposal hash and actor.
7. A deterministic policy gate validates capability and arguments, consumes the approval once, applies an allowlisted synthetic state transition, verifies postconditions, and records idempotency and audit evidence.
8. SQLite persists operational state. JSONL traces record redacted runtime events. The dashboard renders current checkpoint, boundaries, evaluation disposition, and persisted incidents.

## Ports and trust boundaries

- CLI and HTTP API are local operator surfaces.
- MCP uses standard input/output and exposes scenario listing, diagnosis/proposal, and incident reading only.
- The model boundary ends at typed output. It cannot call the approval broker or executor.
- The executor can mutate only repository-local synthetic state.
- No outbound connector, credential store, arbitrary shell, or real-infrastructure adapter exists.

## Configuration seams

Retriever and agent implementations are explicit objects with stable names in evaluation output. Later cycles may add approved dense, hybrid, or model-backed configurations without changing the policy/executor boundary.
