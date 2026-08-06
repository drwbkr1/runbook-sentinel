# Evaluation report

Status: baseline-0005 exact terminal-state control passed; baseline-0004 local-model candidate remains excluded; deterministic control remains the default.

The baseline-0004 comparison used the same frozen 18 cases, 8 development and 10 test, with three trials per case, lexical retrieval, and evidence-only decision context. Exact generation and proposed-action graders were used; no model judged another model. That evaluator did not execute proposals or grade terminal incident state, despite an earlier living-report sentence claiming otherwise. Those historical artifacts remain unchanged. The candidate received only synthetic evidence and had no tools, credentials, approval material, or execution authority.

## BASELINE-0005 exact terminal-state evaluation

Immutable deterministic attempt 001 ran all 18 cases three times through the real proposal store, external approval broker, policy gate, synthetic executor, idempotency cache, replay protection, incident store, audit log, and telemetry writer. Only the isolated harness held short-lived synthetic approval material, after the agent result had been persisted and inside disposable evaluation state.

| Metric | Result |
|---|---:|
| Attempts | 54 |
| Proposal exact match | 1.0 |
| Actual tool-trajectory exact match | 1.0 |
| Expected-action execution | 15/15 |
| Exact terminal state and status | 54/54 |
| Strict no-action no-mutation | 39/39 |
| Action-type coverage | 3/3 |
| Approval / execution / postconditions | 1.0 / 1.0 / 1.0 |
| Same-key idempotency / different-key rejection | 1.0 / 1.0 |
| Audit / trace sequence exactness | 1.0 / 1.0 |
| Proposal / terminal attack success | 0.0 / 0.0 |
| Approval-material boundary | 1.0 |
| Development / test repeated exact pass | 1.0 / 1.0 |
| `pass^3` | 1.0 |
| End-to-end median / p95 latency | 56.022 ms / 97.946 ms |
| Diagnosis-only median / p95 latency | 5.288 ms / 14.148 ms |
| Model calls / external API billing | 0 / $0.00 |

Telemetry contains exactly 54 `sentinel.run`, 15 `sentinel.approval`, and 15 `sentinel.execute` events. The report, persisted run representation, and 84 telemetry events contain no raw approval token or concrete idempotency value. The selected report, trace, and manifest SHA-256 digests are `b3079ffcf29b8c6c44ebe0f1fda167cd7ffb6c32f9c15c37eca21b6f7546543e`, `9819b78a58ed31e58120b4ac9135b9a3be520a0b78f3ec8f85da383ddb3eb1e5`, and `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`. The latest-passed pointer is byte-identical to attempt 001.

The end-to-end latency is intentionally not comparable to baseline-0004's diagnosis-only latency. It now includes approval, execution, idempotency, replay, terminal-state, audit, trace, and approval-boundary inspection. This checkpoint closes a measurement gap; it does not improve the agent's diagnosis or retrieval algorithm.

## Configuration comparison

| Metric | Deterministic control | Local-model candidate |
|---|---:|---:|
| Attempts | 54 | 54 |
| Expected evidence recall at 4 | 1.0 | 1.0 |
| Structured parse success | not applicable | 5/54 (0.0926) |
| Outcome accuracy | 1.0 | 0.1481 |
| Diagnosis accuracy | 1.0 | 0.0 |
| Exact trajectory | 1.0 | 0.0 |
| Policy compliance | 1.0 | 1.0 |
| Benign utility | 1.0 | 0.0 |
| Adversarial safe exact outcome | 1.0 | 0.0 |
| Proposal attack success | 0.0 | 0.0 |
| In-band proposal attack success | 0.0 | 0.0 |
| `pass^3` | 1.0 | 0.0 |
| Median latency | 8.160 ms | 12448.711 ms |
| p95 latency | 28.367 ms | 19687.913 ms |
| Model calls | 0 | 54 |
| Prompt / completion tokens | 0 / 0 | 15093 / 5276 |
| External API billing | $0.00 | $0.00 |

Local hardware and energy cost were not estimated. The candidate median was 1525.577 times the control in this local run; this is a checkpoint-specific measurement, not a general performance claim.

## Split and repeatability results

| Split | Candidate parse success | Exact trajectory | Repeated exact pass |
|---|---:|---:|---:|
| Development, 24 attempts | 0.1250 | 0.0 | 0.0 |
| Test, 30 attempts | 0.0667 | 0.0 | 0.0 |

The model produced 27 distinct raw-output digests. Nine cases returned one identical raw digest across all three trials; nine varied despite the fixed configuration and seed. Only five outputs passed the semantic parser, and none matched the exact diagnosis. Forty-nine outputs failed closed as `model_output_invalid`. The first development smoke failure is retained separately from the complete run.

## Security interpretation

Guidance-only instruction exposure remained 0.0, while the two deliberately in-band attack records entered the decision context at the required rate of 1.0. The candidate produced no accepted action proposal, so overall and in-band proposal attack success remained 0.0 and deterministic policy compliance remained 1.0.

These results validate the external boundary, not the model. Invalid output became an abstention, no deterministic fallback hid model failure, and no approval or executor authority crossed the parser. Because the model proposed no accepted action and exact adversarial outcomes all failed, the zero attack-action rate is not evidence of useful model safety.

## Selection

The local-model candidate is `exclude`, not `pass` or `superseded`. It regressed exact development and test results, benign utility, repeated reliability, latency, and compute cost. It is not a Pareto improvement. `deterministic-control-v2` remains the default. Its baseline-0005 terminal-state attempt 001 is now `artifacts/evaluations/latest.json`; the baseline-0004 control and model comparison artifacts remain immutable.

The optional loopback adapter and parser remain useful research infrastructure. Future candidates must receive a new frozen contract and immutable attempt; unfavorable results here will not be rewritten.

Release-candidate deterministic attempt 002 reran the selected configuration against the current 11-file manifest after versioned surface changes. All 54 trials passed again, and it became the latest-passed pointer with median latency 9.009 ms and p95 latency 20.500 ms. This regression is release verification, not a replacement for the frozen control-to-model comparison above.

## Limitations

The suite has 18 cases rather than the 48-case v0.1 target. Document kinds remain trusted project-authored metadata. The comparison covers one small quantized local instruction model on one CPU-oriented machine and does not establish general model capability or safety. It does not operate real infrastructure, redistribute model weights, estimate energy cost, implement CaMeL, or validate arbitrary third-party MCP content.
