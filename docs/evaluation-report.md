# Evaluation report

Status: native control baseline passed; container packaging deferred.

The accepted immutable run is `artifacts/evaluations/runs/baseline-0001-attempt-003.json`, promoted to `artifacts/evaluations/latest.json`. It is bound to the SHA-256 identity in `eval/manifest.json`. Attempts 001 and 002 and their manifests remain as superseded evidence.

## Results

| Family | Result |
|---|---:|
| Scenarios | 9 |
| Repeated attempts | 27 |
| Expected evidence recall at 4 | 1.0 |
| Outcome accuracy | 1.0 |
| Diagnosis accuracy | 1.0 |
| Exact tool trajectory | 1.0 |
| Policy compliance | 1.0 |
| Benign utility | 1.0 |
| Adversarial safe outcome | 1.0 |
| Proposal attack success | 0.0 |
| `pass^3` | 1.0 |
| Median latency | 21.411 ms |
| p95 latency | 39.202 ms |
| Model calls / estimated spend | 0 / $0.00 |

The nine scenarios include fresh benign evidence, missing database evidence, stale deployment evidence, poisoned runbooks, conflicting fresh reports, and injection without telemetry. Exact structured graders were used; no LLM judge participated.

## Live verification

The local API and human approval flow bound approval to the proposal hash, verified postconditions, returned the same result for the same idempotency key, and rejected a replay under a new key with HTTP 409. The model-facing MCP surface exposed diagnosis/proposal and read tools only. SQLite stored token hashes rather than raw approval tokens, traces contained no approval token, and the rendered dashboard accurately displayed the security boundary and persisted mitigations.

## Limitations

This is a deterministic control, not evidence for stochastic model reliability. It has nine cases rather than the 48-case v0.1 target. No dense retriever or local model has passed its external-source gate. Container packaging is deferred because all three current official Python candidates tested had unresolved critical or runtime-relevant high findings.
