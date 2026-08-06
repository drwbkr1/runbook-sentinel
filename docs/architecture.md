# Architecture

## Baseline topology

1. A frozen scenario catalog provides a closed synthetic SRE environment, explicit topology domain, development or test split, evidence, expected terminal disposition, and mutable synthetic state.
2. A deterministic lexical retriever returns a full ranked set as untrusted data. The complete document identities remain in audit-facing results.
3. A deterministic decision-context policy passes only documents classified as telemetry or status into the agent and records excluded documents as guidance-only. In the synthetic catalog, document kind is trusted project-authored metadata; any real intake must assign and verify it outside the model.
4. A bounded control agent independently extracts only allowlisted facts from fresh decision-context records. Retrieved prose never controls program flow. Version 2 includes non-action diagnoses for gateway, API latency, worker capacity, configuration, and observability gaps.
5. The agent returns exactly one outcome: `diagnose`, `request_evidence`, `propose_action`, or `abstain`.
6. Proposals are typed, hashed, and persisted. No agent interface exposes approval or execution.
7. A human-facing API or CLI creates a short-lived approval bound to the proposal hash and actor.
8. A deterministic policy gate validates capability and arguments, consumes the approval once, applies an allowlisted synthetic state transition, verifies postconditions, and records idempotency and audit evidence.
9. SQLite persists operational state. JSONL traces record redacted runtime events and decision-context configuration. The dashboard renders current checkpoint, boundaries, evaluation disposition, and persisted incidents.

The executor action surface remains exactly `restart_worker`, `rollback_deployment`, and `warm_cache`; baseline-0003 adds no capability or state mutation.

## Ports and trust boundaries

- CLI and HTTP API are local operator surfaces.
- MCP uses standard input/output and exposes scenario listing, diagnosis/proposal, and incident reading only.
- Full retrieval identity and guidance-only identity are audit data, not authority.
- The model boundary ends at typed output. It cannot call the approval broker or executor.
- The executor can mutate only repository-local synthetic state.
- No outbound connector, credential store, arbitrary shell, or real-infrastructure adapter exists.

## Configuration seams

Retriever and agent implementations are explicit objects with stable names in evaluation output. Later cycles may add approved dense, hybrid, or model-backed configurations without changing the policy/executor boundary.
