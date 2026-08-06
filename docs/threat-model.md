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
| Indirect prompt injection or poisoned runbook | Only allowlisted facts from fresh telemetry/status enter deterministic decisions; prose is data |
| Stale or conflicting evidence | One-hour freshness window; missing evidence request; conflict abstention |
| Unauthorized action or capability escalation | Server-side allowlist and exact capability match; no model-controlled arguments |
| Forged or changed proposal | Canonical SHA-256 action hash bound to approval |
| Replay or duplicate mutation | One-time approval consumption plus idempotency record |
| TOCTOU and invalid transition | SQLite immediate transaction, precondition check, atomic state update, postcondition check |
| Credential exposure | No credentials or secrets exist; tokens are hashed at rest and omitted from traces |
| MCP overreach | No approval or execution tool; closed-world annotations; enforcement ignores annotations as authority |
| XSS or dashboard injection | Escaped dynamic values and restrictive browser security headers |
| Supply-chain compromise | Standard-library baseline; external-source gate and ledger before import |
| Real infrastructure impact | No real adapter or network connector; executor accepts only synthetic actions |

## Explicit non-claims

The baseline does not prove safety for a stochastic model, hostile operating system, compromised policy process, real production connector, or arbitrary third-party MCP server. Those require new threat analysis and gates.
