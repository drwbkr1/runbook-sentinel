# Threat model

## Protected assets

- Operator intent and approval authority
- Integrity of proposals, synthetic state, evaluation evidence, and release records
- Confidentiality of any future credentials or sensitive evidence
- Availability and auditability of the incident workflow

## Trust boundaries

The model, retrieved content, user artifacts, MCP payloads, external packages, model artifacts, and rendered evidence are untrusted. The deterministic policy reference monitor, approval store, executor, immutable evaluation manifests, and repository controls form the trusted computing boundary for this baseline.

## Principal threats and controls

| Threat | Baseline control |
|---|---|
| Indirect prompt injection or poisoned runbook | Full retrieval is retained for audit, but only trusted-kind telemetry/status enter the decision context; the agent then extracts allowlisted facts only; prose is never authority |
| Stale or conflicting evidence | One-hour freshness window; missing evidence request; conflict abstention |
| Unauthorized action or capability escalation | Server-side allowlist and exact capability match; no model-controlled arguments |
| Forged or changed proposal | Canonical SHA-256 action hash bound to approval |
| Replay or duplicate mutation | One-time approval consumption plus idempotency record |
| TOCTOU and invalid transition | SQLite immediate transaction, precondition check, atomic state update, postcondition check |
| Credential exposure | No credentials or secrets exist; tokens are hashed at rest and omitted from traces |
| MCP overreach | No approval or execution tool; closed-world annotations; enforcement ignores annotations as authority |
| XSS or dashboard injection | Escaped dynamic values and restrictive browser security headers |
| Supply-chain compromise | Standard-library baseline; external-source gate and ledger before import |
| Model output is malformed, over-broad, or capability-confused | Exact schema and identifier parser; server-side action/capability binding; invalid output becomes abstention with no fallback |
| Loopback model request is redirected or proxied off-machine | Literal `127.0.0.1:11434` endpoint validation; redirects and environment proxies disabled; streaming and tools disabled |
| Model failure is hidden by a stronger deterministic fallback | Configurations are evaluated separately; candidate failure is retained and never replaced with the control result |
| Raw generated text contaminates telemetry | Trace stores contract, prompt, request, and output digests plus parse status and counts; validated semantics live only in the immutable evaluation record |
| Evaluation authority leaks into the agent or runtime | The harness runs only after the agent result is persisted, keeps raw approval material in temporary evaluation variables, uses disposable SQLite state, writes no token or idempotency key to evaluation artifacts, and adds no API, MCP, CLI, or dashboard authority |
| A proposal-only score hides unsafe or failed execution | Proposal, approval, execution, postconditions, idempotency, replay rejection, terminal state, audit sequence, trace sequence, and terminal attack success are independently exact-graded |
| Aggregate case coverage hides incorrect sensitivity to evidence changes | Frozen control/variant relations allow only one declared transformation and grade invariance or directional safety at exact outcome, action, trajectory, and terminal-state levels in both splits |
| Forged evidence classification | Synthetic kinds are project-authored; any real intake must authenticate source identity and assign kind outside the model before this boundary can be claimed |
| Real infrastructure impact | No real adapter or network connector; executor accepts only synthetic actions |

## Explicit non-claims

The measured candidate validates fail-closed boundaries but does not prove useful stochastic-model safety. The baseline does not prove safety for a hostile operating system, compromised policy process, real production connector, or arbitrary third-party MCP server. Those require new threat analysis and gates.
