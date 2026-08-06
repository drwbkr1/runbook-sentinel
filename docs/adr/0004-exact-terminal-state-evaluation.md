# ADR 0004: Exact terminal-state evaluation through the external authority boundary

- Status: accepted
- Date: 2026-08-06
- Checkpoint: baseline-0005

## Context

Baseline-0001 through baseline-0004 reported a field named `trajectory_exact`, but the evaluator assigned it from outcome, diagnosis, and proposed-action agreement. It did not approve or execute proposals and did not compare persisted incident state with an annotated goal state. The favorable score therefore could not establish real tool-trajectory or terminal-state reliability.

## Decision

Freeze an exact full terminal state, incident status, and one of two external-harness trajectories for every scenario before implementation. During evaluation only, after the agent result is persisted, an isolated harness may create a synthetic approval, invoke the existing executor, retry the same idempotency key, attempt a different-key replay, and inspect state, audit, and telemetry. Approval material remains temporary harness state and is absent from agent/model input and output, persisted run JSON, evaluation reports, and traces.

Grade proposal agreement, approval, execution, postconditions, idempotency, replay rejection, audit order, trace order, exact state/status, no-action no-mutation, proposal attack success, and executed terminal attack success separately. Do not add an approval or execution tool to MCP, automatic approval to the API or CLI, a new executor capability, or a real infrastructure connector.

## Consequences

- The evaluator now measures the real synthetic authority path and reports its latency rather than presenting diagnosis latency as end-to-end performance.
- Exact terminal-state evidence is deterministic and does not require an LLM judge.
- A policy-valid adversarial proposal can execute in disposable evaluation state, allowing terminal attack success to be distinguished from proposal attack success.
- The harness has synthetic authority and therefore becomes part of the trusted evaluation surface; its code and real-surface verifiers are manifest-bound.
- Historical favorable proxy results remain immutable and are not retroactively described as executed terminal-state evidence.
