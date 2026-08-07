# Evaluation report

Status: public baseline-0007 controlled-evidence-relations attempt 002 is the latest verified release candidate; baseline-0008 is active after a fresh accepted-system orientation exposed non-discriminating retrieval measurement and a concrete guidance-flood failure. The baseline-0004 local-model candidate remains excluded; deterministic control remains the default.

## BASELINE-0008 orientation and measured retrieval gap

The exact public `v0.0.7` checkpoint was rerun before selecting work. The fresh orientation passed 24 frozen scenarios three times, all four behavioral relations, 21 expected executions, 51 strict no-action checks, policy, terminal security, and repeated reliability. It emitted 72 run, 21 approval, and 21 execution traces. Report and trace SHA-256 are `5613736289de85f002cea7dfdd3d2e5b227f54cb7c3eff2a58a198d340da2c95` and `67389e02512041a65b90d3987144efeee69a03f0865ad679643dec1517d5ebc4`; these orientation files remain under `C:\Projects\Verification` rather than entering release evidence.

The favorable recall@4 score of 1.0 was not discriminating: every released scenario contains at most two documents and the retriever returns up to four. A project-authored exploratory variant added five query-matching runbook documents to `dev-worker-backlog`. The released lexical retriever returned four guidance documents and zero expected project telemetry, so expected project-evidence recall@4 fell to 0.0 before the evidence-only post-filter could help. A separate exploratory probe reproduced the result on `test-cold-cache`; that test observation is retained but excluded from held-out contract selection and implementation feedback. The unprobed `test-worker-injection` case is the held-out source for the frozen checkpoint.

Disposition: `remediate` through a retrieval-only comparison. Schema 1.7 will freeze one development and one untouched held-out guidance-flood case before candidate implementation, grade trusted project-evidence retention separately from outcome, proposal, tool trajectory, terminal state, policy, benign utility, attack success, repeated reliability, latency, and cost, and retain the released v1 failure. No agent, action, approval, executor, MCP/API authority, dependency, model, external asset, secret, or real-infrastructure boundary changes.

Schema 1.7 now freezes 26 cases, exactly one retrieval-stress pair per split, five appended instruction-bearing runbooks per variant, the top-4 limit, exact required project evidence, and behavior/terminal equality to each control. The independent validator reproduces the released v1 ranking and proves both stressors return four appended guidance documents and zero required project evidence. Evidence-condition, behavioral-relation, retrieval-stress, and terminal-state-v4 validators all pass; the 23-file pre-implementation manifest SHA-256 is `c7cc170faeda99e7d6d78051383733c0cbb2ba1fcf9c45ebbe344583d05163f7`.

The immutable released-v1 pre-change control has disposition `remediate`. Across 78 trials, aggregate expected-evidence recall@4, exact outcome/diagnosis/proposal, tool trajectory, terminal state, and `pass^3` fell to `0.9231`; expected executions were 21 of 27. Policy compliance remained 1.0 and proposal/terminal attack success remained 0.0, showing that the defect is safe denial of utility rather than unauthorized mutation. The development stress case returned four guidance documents, no decision evidence, requested evidence, and left the incident open in all three trials instead of proposing the frozen restart. Report, trace, and manifest SHA-256 are `d87973ed303d2daee97224361ca9a5b7454a5ce7b5157cd71121137aea5fabb3`, `3fbea02e21133cf36a474b6a133b36873ed5c30eb16347035aea5e16e6288c68`, and `c7cc170faeda99e7d6d78051383733c0cbb2ba1fcf9c45ebbe344583d05163f7`. Held-out attempt details remain sealed from implementation feedback.

The bounded candidate retains v1 lexical scoring and deterministic tie-breaking, then fills positive top-4 results from project-classified `telemetry`/`status` before untrusted kinds. It does not inspect scenario IDs, expected outputs, actions, or terminal state. The evaluator now emits separate retrieval-stress validity, split coverage, required project-evidence recall@4, decision-evidence retention, guidance saturation, exact behavior retention, and per-split exactness.

The first integration run failed because the new retrieval-stress helper interrupted the behavioral-relation helper boundary; direct scenario and retrieval tests passed, but the evaluator returned null relation metrics. The boundary repair changed no frozen case or retrieval rule. All 15 tests and four validators then passed against the 23-file implementation manifest at SHA-256 `5f3b9064cb2f14c7c4c32772aa6da0a51b9a7c4d09b8aba083ad86b859c6e306`. Focused tests compare v1 and v2 on development, reject a missing held-out pair, and detect missing decision evidence. Held-out stress assertions were first revealed only in the all-green post-implementation run; no candidate or grader change followed.

### Retrieval configuration comparison and selection

| Metric | Lexical v1 | Evidence-priority v2 |
|---|---:|---:|
| Disposition | remediate | pass |
| Stress project-evidence recall@4 | 0.0 | 1.0 |
| Stress decision-evidence retention | 0.0 | 1.0 |
| Stress exact behavior retention | 0.0 | 1.0 |
| Guidance saturation at four | 1.0 | 0.75 |
| Overall proposal / trajectory / terminal exact | 0.9231 / 0.9231 / 0.9231 | 1.0 / 1.0 / 1.0 |
| Adversarial safe outcome / `pass^3` | 0.8182 / 0.9231 | 1.0 / 1.0 |
| Policy compliance | 1.0 | 1.0 |
| Proposal / terminal attack success | 0.0 / 0.0 | 0.0 / 0.0 |
| Median / p95 end-to-end latency | 64.898 / 116.215 ms | 64.115 / 105.791 ms |
| Model calls / estimated external spend | 0 / $0.00 | 0 / $0.00 |

V2 is selected as a measured Pareto improvement on the same 23-file manifest and 78-trial suite. It improves the frozen stress objective, exact system utility, terminal completion, adversarial safe outcome, repeated reliability, median latency, p95 latency, and diagnosis latency without a policy, attack-success, model-call, cost, action-surface, or authority regression. Attempt 001 emitted 78 run, 27 approval, and 27 execution events; its report and trace contain no approval-token or concrete idempotency literal. Report and trace SHA-256 are `03cc2d70a3ac5fb79944df5fb8f6955016974b2576ae1729dd1b867be1367f3e` and `1ed0c3d665bab0af45b4d2837bb6ba4f05b9c9718f052dc6c62bb989b177a4c0`; `latest.json` is byte-identical. V1 remains retained at report and trace SHA-256 `b76aeb82d539aeb21e4d397afe2c8a951ac261ebcbed364f9dc4f615aa2955a0` and `63a90c4d21cdddef35b7e7b32a330af55bec7110f1bd5f67f0020b3590eea18b`.

The baseline-0004 comparison used the same frozen 18 cases, 8 development and 10 test, with three trials per case, lexical retrieval, and evidence-only decision context. Exact generation and proposed-action graders were used; no model judged another model. That evaluator did not execute proposals or grade terminal incident state, despite an earlier living-report sentence claiming otherwise. Those historical artifacts remain unchanged. The candidate received only synthetic evidence and had no tools, credentials, approval material, or execution authority.

## BASELINE-0006 evidence-condition coverage

Selected release-candidate attempt 002 ran 20 frozen cases three times against the version-bound surface. Schema 1.5 explicitly labels complete, incomplete, stale, conflicting, and instruction-bearing evidence, requires every condition in both development and held-out test splits, and separately requires adversarial coverage in both splits. Two synthetic development cases close the previously unmeasured stale and conflicting split gaps. Their expected retrieval, outcome, diagnosis, no-execution trajectory, incident status, and exact unchanged terminal state were frozen before evaluator implementation; the agent was not changed. Attempt 001 passed the implementation surface but was superseded when package and real-surface identities changed.

| Metric | Result |
|---|---:|
| Cases / attempts | 20 / 60 |
| Development / test cases | 10 / 10 |
| Evidence-condition split coverage | 10/10 pairs (1.0) |
| Adversarial split coverage | 2/2 splits (1.0) |
| Proposal / tool trajectory / terminal state exact | 1.0 / 1.0 / 1.0 |
| Expected-action execution | 15/15 |
| Strict no-action no-mutation | 45/45 |
| Proposal / terminal attack success | 0.0 / 0.0 |
| Policy / benign utility / `pass^3` | 1.0 / 1.0 / 1.0 |
| End-to-end median / p95 latency | 60.221 ms / 103.683 ms |
| Diagnosis-only median / p95 latency | 5.450 ms / 13.473 ms |
| Model calls / external API billing | 0 / $0.00 |

| Split | Complete | Incomplete | Stale | Conflicting | Instruction-bearing | Adversarial |
|---|---:|---:|---:|---:|---:|---:|
| Development | 5 | 4 | 1 | 1 | 1 | 1 |
| Test | 2 | 6 | 1 | 2 | 5 | 8 |

The immutable pre-change control passed all 60 trials under the older gates while emitting no evidence-condition metric or gate and incorrectly retaining the baseline-0005 report identity despite a baseline-0006 manifest. It remains retained as `baseline-0006-prechange-control`. Attempt 002 derives its checkpoint from the manifest, fails closed on missing or unknown labels, emits 60 `sentinel.run`, 15 `sentinel.approval`, and 15 `sentinel.execute` events, and contains no approval-token literal. Its report, trace, and manifest SHA-256 digests are `45fd47dd788541f47ff04d9547206de1d01abf24c07501a0f17ffaba10323224`, `5329eb6cafcba980d840ba81ee989ec909c5b61a56fee218897e0e12bde3122a`, and `9f70f756ab93d4ba8732ed70455e0ce3c26f3cc84558baff24d8f56b7e101573`. The latest-passed pointer is byte-identical to attempt 002.

This checkpoint measures coverage of declared synthetic conditions; it does not establish general safety, third-party-data robustness, or production fitness. Native held-out CLI, MCP, loopback API approval/executor/replay, SQLite, audit, telemetry, security headers, and rendered dashboard verification passed; an exact clean clone and public release remain required.

## BASELINE-0005 exact terminal-state evaluation

Selected release-candidate attempt 004 ran all 18 cases three times through the real proposal store, external approval broker, policy gate, synthetic executor, idempotency cache, replay protection, incident store, audit log, and telemetry writer. Only the isolated harness held short-lived synthetic approval material, after the agent result had been persisted and inside disposable evaluation state. Attempts 001 through 004 are retained; 002 and 003 passed but were superseded when newly reviewed release-verifier files were added to the manifest.

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
| End-to-end median / p95 latency | 38.198 ms / 73.236 ms |
| Diagnosis-only median / p95 latency | 5.564 ms / 14.791 ms |
| Model calls / external API billing | 0 / $0.00 |

Telemetry contains exactly 54 `sentinel.run`, 15 `sentinel.approval`, and 15 `sentinel.execute` events. The report, persisted run representation, and 84 telemetry events contain no raw approval token or concrete idempotency value. The selected report, trace, and manifest SHA-256 digests are `132306bbf9f8619e61dee1d74f1a9e7ef208b0b8b178b672e51c42d3751b99f1`, `d6ae7e0d7800b0a64b8063b574504a40102550a10c62d9a2bc2a341fb8c69e87`, and `8f3e0a8710abdfd3894047c451ffc23f3a1488b836dbe510cfab7832b2549267`. The latest-passed pointer is byte-identical to attempt 004.

The end-to-end latency is intentionally not comparable to baseline-0004's diagnosis-only latency. It now includes approval, execution, idempotency, replay, terminal-state, audit, trace, and approval-boundary inspection. This checkpoint closes a measurement gap; it does not improve the agent's diagnosis or retrieval algorithm.

Native real-surface verification passed the held-out CLI, MCP protocol `2025-11-25` and three-tool authority inventory, loopback API, hash-bound approval, executor, exact postconditions, same-key idempotency, different-key HTTP 409 replay rejection, persisted SQLite state, ordered audit log, redacted telemetry, API-served selected evaluation, browser security headers, and visually inspected 1440 by 1000 dashboard. The first live API verification is retained as `fail` because an unnamed PowerShell aggregate returned false despite favorable printed evidence; the named-check rerun and independent runtime receipt passed. This was a verifier correction, not a changed agent or policy result.

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

The local-model candidate is `exclude`, not `pass` or `superseded`. It regressed exact development and test results, benign utility, repeated reliability, latency, and compute cost. It is not a Pareto improvement. `deterministic-control-v2` remains the default. Baseline-0006 attempt 002 is now `artifacts/evaluations/latest.json`; attempt 001, the baseline-0005 terminal-state attempts, and baseline-0004 control/model comparison artifacts remain immutable.

The optional loopback adapter and parser remain useful research infrastructure. Future candidates must receive a new frozen contract and immutable attempt; unfavorable results here will not be rewritten.

Release-candidate deterministic attempt 002 reran the selected configuration against the current 11-file manifest after versioned surface changes. All 54 trials passed again, and it became the latest-passed pointer with median latency 9.009 ms and p95 latency 20.500 ms. This regression is release verification, not a replacement for the frozen control-to-model comparison above.

## Limitations

The active relation suite has 24 cases rather than the 48-case v0.1 target; the public v0.0.6 release has 20. Condition labels and document kinds remain trusted project-authored metadata even though their shape and split coverage now fail closed. The comparison covers one small quantized local instruction model on one CPU-oriented machine and does not establish general model capability or safety. It does not operate real infrastructure, redistribute model weights, estimate energy cost, implement CaMeL, or validate arbitrary third-party MCP content.

## BASELINE-0007 pre-grader control

The fresh public-v0.0.6 orientation passed all 60 trials but found zero explicit evidence relations, zero controlled same-split freshness pairs, and no pairwise relation metric or gate. Schema 1.6 then froze four controlled relations and four synthetic counterparts before evaluator implementation.

The unchanged evaluator passed all 24 cases in three trials under its existing scenario-level gates. It executed 21 expected actions, kept 51 no-action trials unchanged, and emitted 72 `sentinel.run`, 21 `sentinel.approval`, and 21 `sentinel.execute` events. This favorable result is retained as a pre-grader control, not promoted as relation evidence, because the report contains no relation metric or gate.

The pre-grader report, trace, and copied manifest SHA-256 are `386ece2815be95aff23a84b297ddfb1636a19303f01c59bc7e583f50a9fbfdaf`, `d50d4e32ff1b133447f4f35a9b71a2cfdfb178134b2f753ab11ae490ba5afb6e`, and `696474d7e12c0ea79de843d4fdef3c3bec8faf9b5225997dc35ae18ab426c191`. The released `artifacts/evaluations/latest.json` remains the baseline-0006 selected result until a relation-aware attempt passes.

## BASELINE-0007 implementation smoke

The relation-aware evaluator now fails closed on the contract shape, allowed relation and transformation sets, required split/type pairs, scenario reuse, trial alignment, frozen expectations, and missing records. It grades instruction-injection invariance and fresh-to-stale directional safety separately, then reports their combined and per-split exact-match rates without replacing any scenario-level metric.

Focused tests prove that removing the held-out freshness relation invalidates split coverage and that corrupting one paired action lowers invariance and combined exactness even when the relation contract remains structurally valid. The first integrated test run exposed a misplaced function boundary that caused the existing evidence-coverage helper to return null; the code boundary was corrected without altering the frozen behavioral contract or runtime decision logic, after which all 14 tests passed.

A disposable three-trial smoke evaluated all 24 cases and all four relations. All 12 paired attempts passed: invariance 1.0, directional safety 1.0, combined exactness 1.0, and development/test exactness 1.0. All existing gates also passed. The report and 114-event trace remain outside repository release evidence under `C:\Projects\Verification`; their SHA-256 digests are `9da65549afcc80d68ec74ca025e3529d9fefc41484c30b454a57c44f61f3fced` and `80631bf38454f7302b5e2852b3b28560dc8bc7f7941917a31d64f60da3b0d1df`. This smoke is implementation evidence only; it does not replace the selected baseline-0006 pointer.

The completed 22-file implementation manifest passes at SHA-256 `8db0a7f5fd15dd92a82ab710e65fc6dbc84e4eec28b2d67b46a94a1427963c69`. The evaluator hash changed to bind the relation grader; agent, retriever, policy, service, API, MCP, and action-surface hashes remain unchanged. An immutable manifest-bound attempt is required before selection.

## BASELINE-0007 selected attempt

Immutable attempt 001 passed all 72 scenario trials and all 12 paired relation trials against the exact 22-file manifest. Instruction-injection invariance, fresh-to-stale directional safety, combined relation exactness, development relation exactness, and held-out relation exactness are all 1.0. Existing retrieval, generation, proposal, tool-trajectory, terminal-state, policy, utility, security, repeated-reliability, topology, condition, latency, and cost dimensions remain separately reported and passing.

The harness executed all 21 expected actions and kept all 51 no-action trials unchanged. Its 114 telemetry events comprise 72 runs, 21 approvals, and 21 executions. Neither the report nor trace contains a raw approval-token literal or concrete idempotency material. End-to-end median and p95 latency were 59.019 ms and 103.750 ms; diagnosis-only median and p95 were 6.343 ms and 16.423 ms. These are checkpoint-specific local measurements, not general performance claims.

Report, trace, and copied-manifest SHA-256 are `eda653ad87436fbbc3c6e3196e2fee4c503589d32cd35795351bf6f50101bccf`, `db9ff7eaed7d67dcbbdd62bdf1f299b41abaa34a581d6476e4fbc0e506076035`, and `8db0a7f5fd15dd92a82ab710e65fc6dbc84e4eec28b2d67b46a94a1427963c69`. The copied manifest matches the active manifest, and `artifacts/evaluations/latest.json` is byte-identical to attempt 001. The deterministic control remains selected; this checkpoint improves behavioral measurement rather than the agent's decision logic.

The package, API health, MCP identity, CLI default, tests, README, dashboard, and real-surface verifiers now identify `0.0.7` / baseline 0007. The dashboard adds behavioral-relation exactness as a visible metric without adding approval or execution authority. The refrozen versioned 22-file manifest has SHA-256 `02ff28f3616572d3c1b6d97e5fe617594765575666f2ed74cb247b43b7ee5314`. Attempt 001 remains immutable and passing but is superseded for release selection; a fresh version-bound attempt is required.

Version-bound attempt 002 passed all 72 scenario trials and 12 paired relation trials and became the latest-passed pointer. Its end-to-end median and p95 latency were 66.202 ms and 108.166 ms. Report, trace, and copied-manifest SHA-256 are `6dbd86d774304ec9d6dbd3687fcc1cc72e87b8846a7f5b96343b0176063f40eb`, `1e6bbdcb7170acf5d02172e74e4d365dcbffd7fe8e33a67d6bc9e8367660ff99`, and `02ff28f3616572d3c1b6d97e5fe617594765575666f2ed74cb247b43b7ee5314`.

Native verification passed the held-out CLI, MCP protocol and three-tool diagnostic/read inventory, loopback API, selected evaluation, hash-bound approval, executor, exact postconditions, same-key idempotency, different-key replay rejection, persisted SQLite state, ordered audit log, redacted telemetry, browser security headers, and 27 named dashboard/API checks. Independent runtime inspection passed all 16 checks. The freshly rendered dashboard was visually inspected and accurately shows relation exactness 1.0, the human approval boundary, disconnected real infrastructure, and one mitigated synthetic incident.

GitHub PR `#6` matched the exact verified branch head, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `5c690c9f4f6b00e577eef84a1dc33437f5cd7ba1`. A fresh public clone of that remote-main commit independently passed compilation, tests, contracts, artifact parsing, selected evaluation and manifest identity, model and secret exclusion, CLI, MCP, all 27 API checks, all 16 runtime checks, and a fresh visual dashboard inspection.
