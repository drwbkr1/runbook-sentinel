# Evaluation report

## BASELINE-0014 pre-change and isolated candidate result

The downloaded public v0.0.13 zipapp passes the frozen 28-scenario, 84-attempt evaluation and every existing gate. Its 150-event trace contains 84 run, 33 approval, and 33 execute events. Same-key idempotency is 1.0 only because the released evaluator retries with the original valid approval token; it has no cached-result authorization metric.

A development probe through the released real loopback HTTP API first executed one proposal correctly, then retried the same proposal and idempotency key with a wrong token and with no token. Both retries returned HTTP 200 and the exact cached successful execution result. SQLite, audit, and trace evidence proves there was no second executor or state mutation. The measured issue is unauthorized result disclosure and false authorization success, not duplicate execution.

Disposition: `remediate`. The frozen contract defines six cases across separate development and held-out splits. A same-proposal cache hit requires a supplied token hash matching a consumed approval for that proposal. The original consumed token remains valid for its exact completed retry even after expiry, while a new key remains replay-rejected. Ordered incident, run, proposal, approval, idempotency, and audit rows plus trace bytes must remain identical around every retry.

The generic service correction and development tests were committed after the freeze and before held-out reveal. The first isolated reveal then passed all six real-loopback cases without a contract, candidate, expected-result, or grader change. Authorized cache utility, unauthorized cache denial, retry no-mutation, new-key replay rejection, development exactness, test exactness, and overall exactness are all 1.0. The immutable result SHA-256 is `90ec001f063d97755014d32c84832687c67b5a3130aca89e57b3c427a26d3306`; it contains no raw approval-token field.

The schema 2.1 evaluator now reports this plane separately from the 84 repeated scenario attempts and nine approval-lifetime cases. All 22 tests pass. Version-bound evaluation, real surfaces, package, clean clone, review, merged main, and public release remain pending; therefore this is candidate evidence, not a release claim.

## BASELINE-0013 pre-change result

The downloaded public v0.0.12 zipapp still passes the frozen 28-scenario, 84-attempt evaluation with every existing gate passing. Its trace contains 84 run, 33 approval, and 33 execute events, but the existing contract contains no invalid approval-lifetime case.

A development probe through the released real loopback HTTP API supplied `ttl_seconds: -1`. The API returned HTTP 201, persisted the proposal as approved, and issued an already-expired approval; execution then returned HTTP 409, a second approval returned HTTP 409 because the proposal was no longer pending, and the incident remained open. This is a measured benign-liveness failure. The same missing upper bound also permits approvals to outlive the intended short-lived authorization window.

Disposition: `remediate`. The frozen approval-lifetime contract defines nine exact cases, separate development and held-out splits, strict no-mutation results for six invalid values, and exact one-, 300-, and default-300-second results for three valid values. Only `dev-negative-ttl` is revealed as a pre-change failure. Candidate held-out results remain sealed until the generic implementation and independent validator exist.

The generic candidate was committed before reveal. The first and only frozen reveal then passed all nine isolated real loopback HTTP cases: six invalid values returned the exact HTTP 400 `ValueError` with proposal status pending, zero approval rows, zero approval audit events, zero approval trace events, and unchanged open incidents; the minimum, maximum, and omitted values returned HTTP 201 with exact lifetimes of 1, 300, and 300 seconds. Invalid no-mutation, valid-lifetime exactness, development exactness, test exactness, and overall exactness are all 1.0.

The integrated schema 2.0 evaluator retains the approval-lifetime plane separately from the 28 scenarios and 84 repeated attempts. All 21 tests pass after preserving and correcting two verifier false positives that matched the safe field name `approval_token_hashed` as if it were a raw token value.

Version-bound attempt 001 passed under its 40-file manifest, but the subsequent live HTTP verifier failed while parsing a PowerShell 5.1 error response and did not grade the product. After retaining that failure and freezing a corrected manifest, attempt 002 passes eight validators, 21 tests, 84 scenario attempts, and nine approval-lifetime cases. Its report and trace SHA-256 values are `288b8e416a8d259b05b0162df42f1b598d50605dcbf9f54f1439f81406c1d9f4` and `599189f103df0a5797c44bccc909460135f0bbc9a351511c873807fb45834c1f`.

The selected source and package results both pass. Their non-latency fields are exact; both retain policy and `pass^3` at 1.0, proposal and terminal attack success at 0.0, approval-lifetime exactness at 1.0, invalid no-mutation at 1.0, valid-lifetime exactness at 1.0, and zero model calls or estimated external cost. Source/package live MCP, 58 HTTP/dashboard checks, 31 persistence/telemetry checks, and rendered visual inspection pass independently.

A no-local-object public-branch clone of exact commit `2f50f5e8d2098d593fea1d5fefa2ca846422fe9f` independently passes the same eight validators and 21 tests, a new source evaluation, exact archive rebuild, a new package evaluation, MCP authority inventory, 58 HTTP/dashboard checks, 31 runtime checks, and visual dashboard inspection. Its source and package reports remain exact after excluding only declared latency fields.

Final reviewed head `5c4a358a3f85c21ccb27c19efcb791e5b06be283` contained 50 expected paths and merged with history preserved as `54c56411ea0ff3e1b17743fcbd8ebc225dabaabb`. A fresh no-alternates public-main clone passes eight validators, 21 tests, source and package 84+9 evaluations, exact selected-archive rebuild, packaged MCP, 58 HTTP/dashboard checks, 31 state/telemetry checks, secret/model exclusion, and visual inspection. The public annotated `v0.0.13` tag, selected zipapp and checksum assets, downloaded bytes, rendered pages, and fresh tag clone reconcile to the release closure.

Status: public baseline-0013 v0.0.13 is the latest verified checkpoint. Baseline-0011 remains stopped and unpublished. `fresh-content-stale-metadata-context-v3` remains selected, the baseline-0004 local-model candidate remains excluded, and deterministic control remains the default. The project remains synthetic-only and research-informed; no production, universal prompt-injection-resistance, strict latency-dominance, or external-system superiority claim is made.

## BASELINE-0012 reproducible package and canonical dashboard identity

The public v0.0.10 orientation passed all 84 trials and every declared gate, but the release had no package asset. A default zipapp control produced two equal-length but byte-different archives, included 17 cache/bytecode entries, and failed evaluation because the frozen manifest was unavailable. BASELINE-0011 then produced a clean reproducible package, but its first packaged real-surface run passed 49 of 50 checks and visibly rendered the stale label `Baseline 0010`. That fixed candidate was rejected and never published.

BASELINE-0012 treats that label as a known regression, not held-out evidence. Its dashboard and source test derive `Baseline 0012` from the canonical runtime checkpoint. A pre-merge audit then caught manually entered evidence and manifest times that were later than the live UTC clock. The earlier 239,184-byte archive and its passing clean-clone receipt remain retained with disposition `superseded`; no merge, tag, or release used those bytes. After correcting only project-authored provenance metadata and the embedded manifest identity, two independent 239,183-byte package builds are byte-identical at SHA-256 `679f7ad301689bee62a5bcb33df8c4778f9f0307135cf30632b13408e2f31083`. The archive contains 21 exact entries, fixed timestamps and permissions, no cache, bytecode, runtime state, dependency, or secret, an embedded frozen evaluation manifest, and per-entry hashes bound to the frozen package contract.

Corrected source and package runs each pass 28 scenarios and 84 attempts under manifest SHA-256 `63a02909d62c0bb6f156d6700df7b2b9453a7b9e7385e9bf524243c184ccd028`. Every gate and non-latency metric family is exact across runtimes. Source end-to-end median/p95 latency is 151.838/286.728 ms and package latency is 151.586/280.487 ms; diagnosis median/p95 is 22.489/59.960 ms and 22.346/70.268 ms respectively. These are local observations, not a general performance or dominance claim. Both runs make zero model calls and incur zero estimated cost.

Packaged MCP exposes only three diagnostic/read tools and no approval or execution authority. Packaged HTTP/dashboard passes all 51 checks; persisted SQLite, audit, trace, manifest, redaction, and telemetry pass all 27 checks. The rendered 1440 by 1000 dashboard visibly reports Baseline 0012 and the expected security boundaries. The earlier no-local-object clone of `329767a6995aa261509d44e806729f94d166f180` remains retained but superseded for provenance. A renewed clone of corrected commit `59bb7d7763ad3f132d443a79359a05fd60648c44` has no object alternates, reproduces the corrected archive twice, and passes the full source/package, MCP, API, persistence, telemetry, model/secret-exclusion, and visual suite. Final PR `#10` merged with history preserved as `e4dcde1227d0f235f8725df3e15f91ad5675e7ab`; a fresh public-main clone reran the complete stack and reproduced the selected archive. The annotated public `v0.0.12` release, selected zipapp and checksum assets, downloaded bytes, rendered pages, and public-tag clone reconcile to the release closure. Runbook Sentinel remains a synthetic-only, research-informed preview rather than a production, universal prompt-injection-resistance, strict latency-dominance, or external comparative claim.

## BASELINE-0010 stale-payload decision boundary

The fresh v0.0.9 orientation passed all 84 trials, then a field-level trace audit found that `evidence-only-context-v2` forwarded 27 stale project documents across 15 attempts and 5 scenarios. This exposed 2,913 stale title/content characters at the decision boundary even though no stale record supplied agent facts. The retained gap is `artifacts/verification/stale-payload-gap-baseline-0010.json`.

Schema 1.9 freezes one development and one sealed held-out projection case. The contract requires complete retrieval/audit records, complete fresh decision records, exact stale fields `id`, `kind`, and `observed_at`, no stale `title` or `content`, and unchanged behavior. A naive drop-all-stale development probe was rejected because it lost the exact replacement identifier. The metadata-only development probe passed all 14 exact checks and removed 418 stale payload characters. The independent validator rejects field, freshness, split, and behavior corruption.

The immutable v2 pre-change control preserves identity, fresh payload, and behavior at 1.0 but has metadata projection 0.0 and stale payload exposure 1.0. The first complete candidate suite exposed a generic model-adapter assumption that every document had `content`; the field-preserving serializer and focused regression fixed it without changing any frozen case, expectation, or grader. The held-out boundary passed on first reveal after the candidate was complete.

Six same-manifest 84-trial runs per configuration produced 1,008 attempts. V3 passes identity retention, exact metadata projection, fresh payload retention, exact behavior, and both splits at 1.0 with stale payload exposure 0.0 in every run. V2 remains `remediate` with exposure 1.0 and projection 0.0 in every run. Retrieval, generation, proposals, actual tool trajectories, terminal states, behavioral relations, both stress families, policy, benign utility, attack success, repeated reliability, model-call count, and estimated cost are otherwise exact and equal.

The selected configuration is a security-gated Pareto-frontier choice, not a strict numeric Pareto improvement. Relative to v2, V3's median of diagnosis medians is 0.141 ms lower; its median diagnosis p95, end-to-end median, and end-to-end p95 are 2.265, 1.794, and 4.778 ms higher. V2 attempt 005's large latency outlier remains retained and contributes to the comparison record. These local timings support no general performance claim.

The 27-file version-bound manifest has SHA-256 `4b22c5dbd99dd778c5dcca5bb6bbd230178170775b22dcc5b579872e6c9b0ce4`. Immutable attempt 001 passed all 84 trials and every gate; report and trace SHA-256 are `55d1b5be051e8985c0235ad64e1bba88171484e2f1c425360ae03b5962e81cc7` and `3b3e3688918a552886beaba6e45edd60a17ec8174e8ea0127e5950aa0d81747b`. The latest pointer is byte-identical.

The held-out CLI and real MCP paths retain exact stale metadata, complete fresh payload, and zero stale payload characters; MCP 2025-11-25 reports version 0.0.10 and exposes no approval or execution tool. The real loopback API passes all 50 selected-evaluation, projection, approval, execution, postcondition, idempotency, replay, redaction, CSP, and dashboard checks. Independent SQLite, audit, trace, manifest binding, and image checks pass all 27 checks. The native receipt and 1440 by 1000 dashboard SHA-256 are `54c3f7709fb6e52a0d1f1c6fc34e4559078bb204bb98e5768737b7a3831aeef7` and `a4a15564f7a1d4523cc6f0cdfefe8152497ea265f4319176fd7c82fb781cb241`.

An exact no-local-object clone of candidate `1fafe2c99e96d84693a4ba54271694611b3602e4` passed compilation, 19 tests, all seven validators, the 16-criterion source gate, ten milestone contracts, 152 tracked JSON files, 47 tracked JSONL files with 5,085 records, selected-manifest identity, unchanged authority files, model/secret exclusion, held-out CLI, MCP, all 50 API checks, all 27 persistence/telemetry checks, and fresh visual dashboard inspection. Its receipt is `artifacts/verification/clean-clone-baseline-0010.json`.

GitHub review, merged main, and public-release reconciliation remain pending and must pass before this section can claim a verified release. Docker is currently off, but container packaging remains independently deferred because all reviewed bases are excluded; no image was imported or run. A non-gating wheel probe found no local `setuptools.build_meta`; no unreviewed dependency was downloaded or added, and this release makes no package-registry claim.

Final GitHub PR `#9` head `914a719a9f26e555ccc70f02ea4fe056ed675759` contained three expected commits and 90 expected changed files, remained `CLEAN` and `MERGEABLE` after draft promotion, and merged with history preserved as `ccbdafc40777ce7b20ed1375463193ecdbaa7d6c`. A fresh public clone of that merge independently passed compilation, 19 tests, every frozen validator and milestone contract, the source gate, artifact parsing and selected-manifest identity, unchanged authority files, model/secret exclusion, held-out CLI, MCP, 50 API checks, 27 persistence/telemetry checks, and visual dashboard inspection. The public `v0.0.10` tag and non-draft release bind the release-closure commit; Runbook Sentinel remains a synthetic-only, research-informed preview rather than a production, universal prompt-injection-resistance, strict numeric Pareto/latency-dominance, or external comparative claim.

## BASELINE-0009 stale-evidence retrieval resilience

The exact public `v0.0.8` checkpoint was rerun before work selection. The fresh orientation passed all 26 frozen scenarios three times, all six guidance-flood attempts, all 12 behavioral-relation attempts, 27 expected executions, 51 strict no-action trials, policy, terminal security, and repeated reliability. The report and trace are retained outside the repository under `C:\Projects\Verification`; their SHA-256 values are `ab33e17a74e8dcc64c76d4680f4a241495297fb5bc6e0b24f61fa6e1117ba92` and `9c0ba0c90bffb7e4d663fdb01329b0a9d4bd4848afe4a2ea6df5d421d5e62fc`.

The highest-leverage measured weakness was stale project evidence crowding out current project evidence. A development probe appended five 24-hour-old, query-matching telemetry records to `dev-worker-backlog`. V2 filled the top four with stale records, dropped `telemetry-worker-current`, produced fresh-evidence recall@4 of 0.0, and safely requested evidence instead of proposing the frozen `restart_worker`. The development gap is preserved at `artifacts/verification/stale-evidence-gap-baseline-0009.json`; no held-out candidate result was inspected before the generic candidate was complete.

Two primary ACL sources were reviewed through the 16-criterion source gate at `artifacts/verification/research-source-gate-baseline-0009.json`. The gate permits citation, narrow paraphrase, project-authored synthetic tests, and publication only. It imports no paper, code, data, model, dependency, executable, service, or externally controlled asset.

Schema 1.8 freezes 28 scenarios, one development and one held-out stale-evidence pair, five declared stale telemetry records per variant, exact current evidence, and unchanged behavior, trajectory, and terminal state. Terminal-state-v5 requires 11 actionable and 17 no-action cases. All five independent validators pass. The version-2 pre-change attempt 002 remains immutable with disposition `remediate`: across 84 trials, fresh-evidence recall, current decision-evidence retention, and exact stale-stress behavior are 0.0; stale saturation is 1.0; `pass^3` is 0.928571; 27 of 33 expected actions execute; all 51 no-action trials remain unchanged; policy is 1.0; proposal and terminal attack success are 0.0. Its report and trace SHA-256 are `834dcca5a13051c72633282af651b3c4035edf4c5bcc659e7f9aeccfefe22612` and `033f9f6fdf8fe384e47c0471a748bb47daced5b957a48c57b5e5fab170651933`.

V3 retains lexical scoring and deterministic tie-breaking, uses the scenario's explicit `as_of`, and ranks fresh project evidence before stale project evidence and guidance. The retriever and bounded agent share a fail-closed one-hour predicate: missing, malformed, timezone-naive, or future timestamps receive no fresh treatment. The rule does not inspect scenario IDs, expected results, actions, trajectories, or terminal state. The held-out cache pair passed on first reveal after implementation completion; no candidate, case, expectation, or grader changed afterward. All 16 tests passed.

### V2 and v3 same-manifest comparison

| Metric | Evidence-priority v2, two runs | Freshness-priority v3, three runs |
|---|---:|---:|
| Disposition per run | remediate | pass |
| Fresh project-evidence recall@4 | 0.0 | 1.0 |
| Current decision-evidence retention | 0.0 | 1.0 |
| Exact stale-stress behavior | 0.0 | 1.0 |
| Stale saturation at four | 1.0 | 0.75 |
| Proposal / trajectory / terminal exact | 0.928571 / 0.928571 / 0.928571 | 1.0 / 1.0 / 1.0 |
| Policy compliance | 1.0 | 1.0 |
| Proposal / terminal attack success | 0.0 / 0.0 | 0.0 / 0.0 |
| `pass^3` | 0.928571 | 1.0 |
| Mean of run median / p95 latency | 63.812 / 97.072 ms | 71.261 / 109.547 ms |
| Mean diagnosis median / p95 | 6.184 / 13.558 ms | 6.638 / 15.314 ms |
| Model calls / estimated external spend | 0 / $0.00 | 0 / $0.00 |

All compared runs use the same 25-file manifest at SHA-256 `3f7ca71d8425a5d0101a398ede21b958474aaca8989b56d6bd9edfc489584a49`. V2 reports are `e33d9a33d35f159b7575db1ee686a68b24141869d2f6f9953c09f4edb9e20620` and `bb86d1d77c644aa95925f162b282bc66e230eacc566ff93a68117f23c854f10f`; v3 reports are `6efde86f495f5d8d03392f507d745904c3552ccef00e6532335a8102c073a9d8`, `0bee10bba4aa4447d38ecb268d97578d4e8417ca3c7bf309ff014d06aba97ef1`, and `41e2d202ee5f1f3df9c2be5dfcc39b9a1278391884b00b71190d2b723088d0a4`.

Aggregate end-to-end latency is not work-equivalent because v3 completes six additional correct approval and execution trajectories per run. On the 26 original cases, v2 and v3 diagnosis medians are 6.170 and 6.301 ms, and end-to-end medians are 63.826 and 68.507 ms. The 0.131 ms and 4.681 ms increases are explicit tradeoffs. With no frozen non-inferiority margin, strict numeric Pareto dominance is false. V3 is selected as a reliability-gated Pareto-frontier choice because it is the only configuration passing every hard correctness, security, policy, reliability, and cost gate. This supports selection on the frozen synthetic suite only, not production readiness, universal temporal robustness, strict latency dominance, or comparative superiority to external systems.

The versioned 25-file manifest passes at SHA-256 `5d18d47df8ad9f74bbc483864e31de7a85d637a67773c1555de18b05386afd85`. Version-bound attempt 002 passed all 84 trials and became `artifacts/evaluations/latest.json`; median/p95 end-to-end latency is 72.339/104.912 ms and diagnosis median/p95 is 6.821/14.939 ms. Report and 150-event trace SHA-256 are `2cc4fbb816e04d918bc42d9bb818f64c71e294d670de8ee8776d9598f9e1a61d` and `cdd5567bc563f43db7b5cdb53ec2779364ccc057ceed18769ef77c8c80bfeb90`. Model calls and external spend remain zero.

The direct held-out CLI and MCP stdio paths used v3, ranked the current telemetry ahead of three stale telemetry records, proposed the exact frozen action, retained all four identities for audit, and exposed no approval or execution MCP tool. The real loopback API passed 40 named checks for health, selected evaluation, stale and guidance stress metrics, hash-bound approval, execution, postconditions, same-key idempotency, different-key HTTP 409 replay rejection, token redaction, CSP, and dashboard content. Independent SQLite, audit, telemetry, manifest binding, and screenshot inspection passed 23 checks. Native receipt and dashboard SHA-256 are `fef021cea1a5a58536f684bec2a99017837239f1eea89d3d10d2a0657dac743d` and `934b13fb481b2566730aeab62e7484244edaf478d3aba0ee53d9127d5de85099`.

Visual inspection confirmed the 1440 by 1000 dashboard accurately reports baseline 0009, passing deterministic v2 agent behavior, freshness-priority v3 retrieval, guidance and fresh-evidence recall 1.0, human approval, disconnected real infrastructure, and one mitigated synthetic stale-evidence incident. The headless browser emitted a renderer task-manager warning only after writing the verified PNG; it is retained as tooling evidence.

Docker 29.4.3 is live. Container packaging remains deferred because all three locally cached official Python base candidates remain excluded by the current source gate for unresolved high or critical findings; no excluded image was run and no new image was imported.

An exact no-local-object clone of candidate `f3d882a6e92d4bfe0b4d1803e8b9b214dac362eb` passed compilation, 16 tests, all five validators, the 16-criterion research gate, nine milestone contracts, 114 tracked JSON files, 34 JSONL files with 3,135 records, selected-evaluation and manifest identity, unchanged policy, model-weight and high-signal-secret exclusion, held-out CLI, MCP, all 40 API checks, all 23 native checks, persistence, telemetry, and a fresh visual dashboard inspection. The receipt is `artifacts/verification/clean-clone-baseline-0009.json`.

Draft GitHub PR `#8` matched reviewed head `d80426a7ef0736b04303d568bcd93580fb07d345`, contained five expected commits and 62 expected changed files, and was `CLEAN` and `MERGEABLE` with no configured checks. A receipt-only final head must be reconfirmed before review promotion or merge. Tag, release, and rendered-public-page evidence must still pass before v0.0.9 becomes a verified checkpoint.

The final PR head `a1fd78c7c242bed6cf780ba13e1e59eba9095e67` contained six expected commits and 63 expected files, remained `CLEAN` and `MERGEABLE` after draft promotion, and merged with history preserved as `4f302820c8452c83226b834b76ea208842f626fd`. A fresh public clone of that merge independently passed compilation, 16 tests, every frozen validator and milestone contract, the current source gate, artifact parsing and selected-manifest identity, unchanged policy, model/secret exclusion, held-out CLI, MCP authority inventory, all 40 API checks, all 23 persistence/telemetry checks, and visual dashboard inspection. The public `v0.0.9` tag and non-draft release bind the release-closure commit; Runbook Sentinel remains a synthetic-only, research-informed preview rather than a production, universal temporal-robustness, strict latency-dominance, or external comparative claim.

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

Package, API, MCP, CLI, tests, README, dashboard, and real-surface verifiers now identify `0.0.8` / baseline 0008. The versioned 23-file manifest passes at SHA-256 `fac3bf310d244322c364516e21b6da78053ddb57d5c3cb05bc15b993609c59da`. Attempt 001 remains immutable and favorable but is superseded for release selection because its manifest predates those versioned surfaces; a fresh version-bound attempt is required before live verification.

Version-bound attempt 002 passed all 78 trials, all six retrieval-stress attempts, all 12 behavioral-relation attempts, 27 expected executions, 51 exact no-action trials, both splits, and every gate. Median and p95 end-to-end latency were 45.245 and 92.216 ms; model calls and estimated external spend remain zero. Report and 132-event trace SHA-256 are `ff913b43daf0c89591d847fc264e8206bbac19bd866372706651e1ffd87362b8` and `2ea120c1ac3319540aeae605b1caf253588eb177dfdcb1f8ab1f7e38dc92205b`; `latest.json` is byte-identical and neither artifact contains approval-token or concrete idempotency material.

The direct held-out CLI and MCP stdio paths used v2, retained the exact project telemetry plus three auditable guidance identities under the top-4 stressor, proposed the frozen restart, and exposed no approval or execution tool. The real loopback API passed 34 named checks for health, selected evaluation, stress retrieval, hash-bound approval, execution, exact postconditions, same-key idempotency, different-key HTTP 409 replay rejection, token redaction, CSP, and dashboard content. Independent SQLite, audit, telemetry, selected-manifest, stress-metric, and screenshot inspection passed. Native receipt and dashboard SHA-256 are `9f9b57a9701fe900a78ef432fea14b646b5992f55ed0aea2a17c74d477e18e8f` and `c49b2135acd4e4564ecb45e498d25871e4165dbef09dadaf2da9dd792fba1baf`.

Visual inspection confirmed the 1440 by 1000 dashboard accurately reports baseline 0008, passing deterministic v2, evidence-priority retrieval, stress evidence recall 1.0, prior exact metrics 1.0, human approval, disconnected real infrastructure, and one mitigated synthetic guidance-flood incident. The headless browser emitted a renderer task-manager warning only after successfully writing the verified PNG; the warning is retained as tooling evidence.

GitHub PR `#7` matched the exact verified head, contained seven commits and 52 expected files, and was `CLEAN` and `MERGEABLE` with no configured checks. It merged with history preserved as `6b79b9e6a02ee083747fc0a8c7559e0222f1b24a`. A fresh public clone of that merge passed compilation, 15 tests, every frozen validator, the research source gate, artifact parsing, manifest and selected-evaluation identity, unchanged policy, model/secret exclusion, held-out CLI, MCP authority inventory, all 34 API checks, persisted approval/executor/replay/postconditions, telemetry, and visual dashboard inspection. The public `v0.0.8` tag and non-draft release bind the reconciled closure commit; Runbook Sentinel remains a synthetic-only, research-informed preview rather than a production or comparative-safety claim.

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
