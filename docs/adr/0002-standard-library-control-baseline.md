# ADR 0002: Standard-library deterministic control baseline

- Status: accepted
- Date: 2026-08-06

## Decision

Build baseline-0001 with Python standard-library modules and project-authored synthetic data. Do not use the installed local models until their source gate passes.

## Consequences

This produces a portable lower bound, isolates policy and interface defects from model variance, and makes later retrieval/model comparisons meaningful. It is not evidence that a stochastic model satisfies the thesis.
