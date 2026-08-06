# Evaluation report

Status: baseline-0002 native candidate passed; clean-clone and publication gates remain.

The accepted immutable candidate is `artifacts/evaluations/runs/baseline-0002-attempt-003.json`, promoted to `artifacts/evaluations/latest.json`. It is bound to manifest SHA-256 `b724b9899ebdf4468cc44e3796e76274e910d795bb71e1933f635b8b65196eff`. Attempt 001 is the failed v0.0.1 control on the expanded cases. Attempt 002 passed graders but is superseded because its declared and emitted agent identities disagreed.

## Results

| Family | Result |
|---|---:|
| Scenarios | 16: 7 development, 9 test |
| Repeated attempts | 48 |
| Declared topology coverage | 8 of 8 domains |
| Expected evidence recall at 4 | 1.0 |
| Outcome accuracy | 1.0 |
| Diagnosis accuracy | 1.0 |
| Exact tool trajectory | 1.0 |
| Policy compliance | 1.0 |
| Benign utility | 1.0 |
| Adversarial safe outcome | 1.0 |
| Proposal attack success | 0.0 |
| `pass^3` | 1.0 |
| Median latency | 7.771 ms |
| p95 latency | 19.739 ms |
| Model calls / estimated spend | 0 / $0.00 |

Development and test split exact trajectory, retrieval, generation, policy, utility, and repeated-trial gates each pass independently. The catalog covers gateway, API, worker, database, cache, deployment, configuration, and observability. Exact structured graders were used; no LLM judge participated.

## Control comparison

| Metric | v0.0.1 control on 16 cases, attempt 001 | Candidate v2, attempt 003 |
|---|---:|---:|
| Exact trajectory | 0.5625 | 1.0 |
| `pass^3` | 0.5625 | 1.0 |
| Benign utility | 0.5556 | 1.0 |
| Adversarial safe outcome | 0.5714 | 1.0 |
| Policy compliance | 1.0 | 1.0 |
| Proposal attack success | 0.0 | 0.0 |
| Median latency | 7.305 ms | 7.771 ms |
| p95 latency | 14.461 ms | 19.739 ms |

The change closes the seven precommitted exact diagnostic gaps without adding an executor action or capability. The single-run latency values do not support a performance improvement claim; paired repeated benchmarking is still required before treating the difference as meaningful.

## Live verification

The isolated local API and human approval flow bound approval to the proposal hash, verified postconditions, returned the same result for the same idempotency key, and rejected a replay under a new key with HTTP 409. The model-facing MCP surface exposed diagnosis/proposal and read tools only. SQLite stored one hashed approval token rather than raw material, traces contained no token, and the rendered dashboard accurately displayed baseline 0002, deterministic v2, the execution boundary, and one persisted mitigation.

## Limitations

This is a deterministic control, not evidence for stochastic model reliability. It has 16 cases rather than the 48-case v0.1 target. The lexical retriever can still expose poisoned runbook text to the bounded agent, although the deterministic agent ignores prose as authority. No dense retriever or local model has passed its external-source gate. Container packaging remains deferred because all three tested official Python candidates had unresolved critical or runtime-relevant high findings.
