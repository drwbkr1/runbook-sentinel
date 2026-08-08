# ADR 0014: Classify model-output failures without widening acceptance

- Status: accepted
- Date: 2026-08-08
- Checkpoint: baseline-0018

## Context

The retained baseline-0004 local-model comparison had 49 `schema_invalid` outputs among 54 attempts, but the adapter exposed no stable machine-readable rejection reason. That made model failure measurable only as one opaque class and prevented targeted experimental comparison. Public v0.0.17 remained fully verified with the deterministic control.

## Decision

Add one closed 17-code taxonomy to content-parser exceptions, model metadata, immutable attempts, and aggregate/split generation metrics. Preserve parser acceptance, output schema, prompt, generation options, generic fail-closed abstention, raw-output digest-only retention, action semantics, policy, approval, executor, and deterministic default exactly. Valid output and non-content failures carry a null content code. A classified rejection remains rejected.

Freeze 19 development/test cases before implementation, seal the generic implementation before the first full reveal and current local-model call, and compare the local candidate with deterministic control on one identical manifest. Continue to require separate retrieval, generation, trajectory, terminal-state, policy, utility, security, reliability, latency, and cost evidence for selection.

## Evidence

Development attempt 001 passes 8/8. The first full reveal passes 19/19, with both splits, classification, and valid acceptance at 1.0 and zero unclassified failures. The current 84-call model attempt produces 9 valid and 75 schema-invalid outputs; every failure is classified as 67 invalid diagnosis identifiers, 7 invalid proposal-argument objects, or 1 out-of-context evidence citation.

On the same manifest, the deterministic control passes every gate with benign utility and `pass^3` 1.0 and median latency 47.675 ms. The model candidate has diagnosis accuracy, proposal exactness, utility, and `pass^3` 0.0 and median latency 10,173.578 ms. It accepts and executes no action. The exact comparison is `artifacts/evaluations/baseline-0018-model-comparison.json` and its independent verifier passes.

## Consequences

- Model failures are experimentally distinguishable without storing unparsed generated content or accepting more output.
- The dominant measured failure is now invalid diagnosis identifiers, but this checkpoint does not tune the prompt, schema, parser, or model.
- The model candidate remains excluded and `deterministic-control-v2` remains default.
- Zero attack success is attributed only to fail-closed parsing and deterministic enforcement; it is not a useful-model safety claim.
- Future model or prompt work requires a new frozen comparison and cannot rewrite this unfavorable result.
