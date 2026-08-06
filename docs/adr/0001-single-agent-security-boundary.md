# ADR 0001: Single bounded agent with external enforcement

- Status: accepted
- Date: 2026-08-06

## Decision

Use one bounded incident agent. It can diagnose, request evidence, propose an action, or abstain. Approval, policy, execution, and postcondition verification remain deterministic and external. MCP exposes no approval or execution tool.

## Consequences

The architecture is easier to evaluate and audit. Model compromise can create a bad proposal but cannot directly mutate even the synthetic environment. Future real connectors require a new milestone and explicit approval.
