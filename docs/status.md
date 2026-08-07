# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `codex/baseline-0007-evidence-relations`
- Completed milestones: `BASELINE-0001` through `BASELINE-0006`
- Latest verified checkpoint: public `v0.0.6`; release reconciliation binds the local tag, remote tag, remote `main`, public repository, and non-draft release to the exact closure commit
- Active milestone: `BASELINE-0007`
- Current unit: version and release the selected relation-aware checkpoint
- Disposition: released baseline `pass`; relation-aware attempt 001 `pass` and selected; local-model candidate `exclude`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: pull request `#5` merged as `1f0635a008d8fdf6e94c9fedf1c39da40651a465` before the exact closure record
- GitHub pull request: `#5`, merged with history preserved
- GitHub release: public, non-draft `v0.0.6`
- Docker: daemon verified live; container packaging deferred after three base-image candidates failed the source gate
- External runtime dependencies: none for the accepted baseline; optional local Ollama evaluation is source-gated separately
- Local model source gate: ready for existing Ollama 0.32.5 plus `llama3.2:3b` at manifest SHA-256 `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`; adapter boundary tests pass and the first synthetic smoke call failed closed

## Verified evidence

- Contract schema: pass
- Frozen manifest: 21 files, SHA-256 `9f70f756ab93d4ba8732ed70455e0ce3c26f3cc84558baff24d8f56b7e101573`, pass
- Tests: 14 of 14 pass
- Frozen evaluation: version-bound attempt 002 passed 20 scenarios, 60 attempts, 15 expected executions, and 45 strict no-action results
- Retrieval recall@4, outcome accuracy, diagnosis accuracy, proposal exactness, actual tool-trajectory exactness, terminal-state exactness, policy compliance, benign utility, adversarial safe outcome, and `pass^3`: 1.0
- Instruction-bearing attack-document decision exposure: 0.0
- Proposal attack success: 0.0
- Terminal attack success: 0.0
- Evidence-condition split coverage: 10 of 10 required pairs, 1.0; adversarial split coverage: 2 of 2, 1.0
- Latest selected-control end-to-end latency: median 60.221 ms, p95 103.683 ms; diagnosis-only median 5.450 ms, p95 13.473 ms; no general performance claim
- Live CLI, MCP stdio, HTTP approval/executor, dashboard, SQLite, audit log, and JSONL telemetry: pass
- Clean clone: candidate `173e42e822def559b870c2e38ca27c6d34b84df4` passed source, contract, 14-test, selected-evaluation, authority-hash, model/secret-exclusion, CLI, MCP, 25-check API, persistence, telemetry, and rendered-dashboard gates
- GitHub review: pull request `#5`, 7 commits, 39 changed files, `CLEAN`, `MERGEABLE`, no configured checks, merged with history preserved
- Merged main `1f0635a008d8fdf6e94c9fedf1c39da40651a465`: fresh public clone passed compilation, 14 tests, manifest, evidence-condition and terminal contracts, selected evaluation, CLI, MCP, all 25 API checks, approval, executor, replay, postconditions, dashboard, SQLite, audit, telemetry, model-weight exclusion, and high-signal secret scan
- Container: deferred after three base images failed the source gate

## BASELINE-0002 measured gap

- Frozen catalog: 16 cases, 48 trials, 7 development and 9 test, spanning all 8 declared domains
- Unchanged v0.0.1 control: 7 new cases failed; trajectory exact match and `pass^3` fell to 0.5625
- Policy compliance remained 1.0 and proposal attack success remained 0.0
- Attempt 001 disposition: `remediate`; evidence is retained and is not the latest-passed pointer
- Attempt 002 disposition: `superseded`; graders passed but declared and emitted agent identities disagreed
- Attempt 003 disposition: `pass`; it is the latest-passed pointer
- Candidate metrics: 16 cases, 48 trials, 8 of 8 domains, development and test exact match 1.0, `pass^3` 1.0, policy compliance 1.0, proposal attack success 0.0
- Candidate latency and cost: median 7.771 ms, p95 19.739 ms, zero model calls and $0.00
- Isolated live CLI, MCP, HTTP approval/executor, replay, dashboard, SQLite, audit, and JSONL telemetry: pass
- Executor policy SHA-256 is unchanged from `v0.0.1`

## BASELINE-0003 measured gap

- Four frozen cases contain explicitly labeled instruction-bearing attack documents.
- v0.0.2 retrieved all four attack documents into the context passed to the bounded agent: exposure rate 1.0.
- Proposal attack success remained 0.0 because the deterministic agent and external policy ignore retrieved prose as authority.
- The bounded comparison will retain full retrieval identities for audit while testing an evidence-only decision plane.
- Full-context attempt 001: exposure 1.0 and disposition `remediate`; all prior quality and action-security gates remained passing.
- Evidence-only attempt 002: exposure 0.0 and disposition `pass`; all prior quality, policy, action-security, reliability, and cost gates remain passing.
- Candidate latency: median 7.729 ms and p95 14.326 ms versus control 8.887 ms and 55.574 ms; no general performance claim is made.
- Pre-commit regression attempt 003: all 48 trials passed again with exposure 0.0, median 7.391 ms, and p95 18.075 ms; it is the latest-passed pointer.
- Live CLI and MCP retained poisoned runbook identity for audit while excluding it from the decision context.
- Isolated API, approval, executor, replay, rendered dashboard, SQLite, audit, and telemetry verification: pass.
- Executor policy SHA-256 is unchanged from `v0.0.2`.

## BASELINE-0004 orientation

- Resumed from public `v0.0.3` at `fa2eb78eb497617b1c775ebd2b609f1216acb8d8`; local tag, peeled remote tag, remote `main`, GitHub release, rendered README, and rendered release agree.
- The retained deterministic control still passes all 48 trials, but no stochastic structured-generation configuration has been measured.
- Local compute: Intel i7-1365U, 10 cores and 12 logical processors, about 34 GB RAM, integrated Intel Iris Xe, no discrete NVIDIA GPU, and about 678 GB free disk.
- Ollama 0.32.5 is live on loopback and publisher-signed. `llama3.2:3b` is the 3.2B GGUF Q4_K_M instruction model with 128K context; its manifest and all six referenced blobs match SHA-256.
- The model and runtime source gate is `ready` only for local synthetic evaluation with no tools, credentials, approvals, execution, downloads, remote services, weight redistribution, or real infrastructure.
- Meta's AUP prohibition on operating critical infrastructure is carried forward as an explicit project no-go. Model card and registry capabilities remain hypotheses until the frozen Runbook Sentinel comparison measures them.
- Frozen schema 1.3 has 18 cases and 54 trials, including development and held-out telemetry/status injections that deliberately enter the decision context.
- Deterministic control attempt 001 passed: exact development and test results 1.0, in-band instruction exposure 1.0, in-band proposal attack success 0.0, overall proposal attack success 0.0, policy 1.0, and `pass^3` 1.0.
- Control latency: median 8.160 ms and p95 28.367 ms; model calls 0 and estimated spend $0.00. Manifest SHA-256 is `ae322324f034595c4374fdf24e3d285e678f7d52e91ced0be030bf40fc33b7fe`.
- The optional adapter is standard-library-only and hard-bound to direct `127.0.0.1:11434/api/chat` transport with redirects, proxies, streaming, and tools disabled.
- Twelve pre-model tests pass, including exact parser, timeout, missing identity, action/capability binding, remote-endpoint rejection, redacted telemetry, and candidate-evaluator coverage. The deterministic agent remains the default.
- Executor policy remains unchanged from `v0.0.3` at SHA-256 `1b23a56b14527347ec723a4c83595414987f9ef7288b532afda49fb4fb7bd1aa`.
- First model smoke: `dev-worker-backlog` returned schema-invalid output and safely became `abstain / model_output_invalid`; no proposal or fallback crossed the boundary. Latency was 25138.148 ms and the raw response is retained only by digest.
- Complete local-model attempt 001: 54 calls, 5 valid parses, 49 schema-invalid abstentions, diagnosis accuracy 0.0, exact trajectory 0.0, benign utility 0.0, and `pass^3` 0.0. Median latency was 12448.711 ms and p95 was 19687.913 ms.
- Candidate policy compliance and proposal attack success were 1.0 and 0.0 respectively, but the candidate made no accepted action proposal. This validates fail-closed enforcement, not useful model safety.
- Candidate disposition: `exclude`. It is not a Pareto improvement; `deterministic-control-v2` and the passing control evaluation remain the defaults.
- Release-candidate deterministic attempt 002 passed all 54 trials against the current 11-file manifest and became the latest-passed pointer; median latency was 9.009 ms and p95 was 20.500 ms.
- Native real-surface verification passed the CLI, MCP version and authority inventory, API health and evaluation endpoints, approval, execution, idempotency, replay rejection, postconditions, rendered dashboard, SQLite, audit log, and redacted traces.
- Docker Desktop 4.74.0 and Engine 29.4.3 are live. Container packaging remains `defer` because the retained base-image source gate has not passed.
- A no-local-object clone of release-candidate commit `1b886c5557d311a272997866a715c2f8f815d76e` passed all required native and real-surface gates before GitHub review and release closure.
- GitHub PR `#3` matched verified branch head `36cfcba4c7a1b333325b196481d9f9bea6357e35`, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `fca61e3f4b1a52e525477002c3977a15aab0cd8f`.
- A fresh remote-main clone of merge commit `fca61e3f4b1a52e525477002c3977a15aab0cd8f` passed tests, manifest, MCP, API, approval/executor/replay/postconditions, persistence, telemetry, and rendered-dashboard inspection.
- Public `v0.0.4`, remote `main`, local annotated tag, peeled remote tag, public release API, rendered README, and rendered release page agree on the exact release-closure commit.

Next eligible action: begin the next cycle from public `v0.0.4`, run the accepted deterministic system, inspect traces and evaluation coverage, and freeze one bounded measurable improvement.

## BASELINE-0005 measured gap

- The current evaluator assigns `trajectory_exact` directly from outcome, diagnosis, and proposed-action agreement. It performs no approval or execution and does not inspect terminal incident state.
- Five actionable cases cover all three executor capabilities and 15 repeated trials, but evaluator terminal-state coverage is 0 of 15 trials and 0 of 3 action types. The other 39 trials do not explicitly prove no mutation.
- No frozen scenario contains an expected terminal-state or exact evaluation-harness trajectory field.
- A separate temporary harness executed `restart_worker`, `rollback_deployment`, and `warm_cache`; all reached the expected state, verified postconditions, returned the same result under the same idempotency key, rejected a different-key replay, and kept approval material outside the agent result.
- The baseline-0004 evaluation report's sentence claiming exact terminal-state graders is unsupported. The historical result remains retained, and the living report now identifies the limitation.
- BASELINE-0005 will let only an isolated evaluation harness hold synthetic approval material. The API, MCP, agent/model, runtime default, action set, and policy boundary remain unchanged.

Schema 1.4 now freezes exact terminal state, incident status, and harness trajectory for all 18 cases. The dedicated validator passes with 5 actionable and 13 no-action cases covering all three existing executor actions. The identical active and retained pre-change manifests have SHA-256 `c458a2ed2af1a6b4324c58f1ac438bbd8cb816938201e5fc8f573b32f8329b8f`.

The retained pre-change control proves the limitation without rewriting baseline-0004: 54 proposal-level trials passed, but the evaluator made 0 approval calls, 0 execution calls, graded 0 terminal states, and explicitly proved no mutation in 0 of 39 no-action trials. Its disposition is `remediate`; the latest-passed pointer remains unchanged.

The isolated harness now invokes the existing approval broker and executor only after the agent result is persisted and only in disposable evaluation state. It separately grades proposal agreement, approval, execution, postconditions, same-key idempotency, different-key replay rejection, exact terminal state and status, no-mutation, audit order, trace order, proposal attacks, and executed terminal attacks.

Thirteen tests pass, including a successful attacker-goal execution and a proposal blocked by deterministic preconditions. A 54-trial implementation smoke reached all 15 expected terminal states across all three action types, kept all 39 no-action trials unchanged, and emitted no approval-token literal in the report or 84 trace events. The final 14-file evaluation manifest SHA-256 is `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`; it binds the evaluation driver as well as the evaluator. Executor policy and service hashes remain unchanged.

Historical handoff at this checkpoint: commit the evaluator implementation, run immutable repeated evaluation attempts against that exact commit and manifest, preserve their traces, and promote only a passing attempt.

Immutable attempt 001 passed all 54 trials and is now the latest-passed pointer. It executed 15 of 15 expected actions across `restart_worker`, `rollback_deployment`, and `warm_cache`; all 39 no-action trials stayed open and exactly unchanged. Proposal, actual trajectory, terminal state/status, policy, approval, execution, postconditions, idempotency, replay rejection, audit order, trace order, approval boundary, development/test reliability, and `pass^3` gates are all exact passes.

Attempt SHA-256 is `b3079ffcf29b8c6c44ebe0f1fda167cd7ffb6c32f9c15c37eca21b6f7546543e`; its 84-event trace SHA-256 is `9819b78a58ed31e58120b4ac9135b9a3be520a0b78f3ec8f85da383ddb3eb1e5`; its copied manifest matches active SHA-256 `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`. `latest.json` is byte-identical to the attempt. End-to-end median and p95 are 56.022 ms and 97.946 ms; diagnosis-only median and p95 are 5.288 ms and 14.148 ms.

Historical handoff at this checkpoint: version the bounded checkpoint as `0.0.5`, rerun the accepted evaluation against the versioned surfaces, and verify the real CLI, API, MCP, approval/executor, dashboard, persistence, telemetry, clean clone, and public release.

Versioned package, API health, MCP identity, CLI default, tests, README, and dashboard now identify `0.0.5` / baseline 0005. The dashboard adds visible actual tool-trajectory and terminal-state exactness without adding approval or execution controls. The release-candidate manifest now binds 17 files, including package metadata, package version, CLI, and the evaluation driver; SHA-256 is `c8a4797dbdde2bc53ff9057bd1953bbfda925149b28c8a538f1d155334757310`.

Historical handoff at this checkpoint: commit the versioned surfaces, generate immutable attempt 002 against the exact 17-file manifest, and begin native real-surface verification only if it passes.

Immutable attempt 002 passed the 17-file versioned manifest and all 54 trials, with 15/15 executions, 39/39 strict no-action results, all exact gates, median end-to-end latency 58.510 ms, and p95 108.435 ms. Report, trace, and manifest SHA-256 are `b1e3eae0cf0ea8a558a7afc5bec4f82616ff811d81006c6f6c73156d8790a3ba`, `9b8aa00f2aa2619c2fd935f54d7d2184f93d53314a140ddaa8fe70c763cf55a1`, and `c8a4797dbdde2bc53ff9057bd1953bbfda925149b28c8a538f1d155334757310`.

Pre-live review then found that the API, MCP, and runtime-evidence scripts still named baseline 0004 and were outside the manifest. No live receipt was created. Attempt 002 remains a passing immutable result but is superseded for release selection. The corrected verifier scripts are being added to a 20-file manifest; a new immutable attempt is required before live verification.

Immutable attempt 003 passed the first 20-file manifest and all evaluation gates. The held-out CLI and MCP 2025-11-25 surfaces then passed with server version 0.0.5 and no approval or execution tool. Two combined shell invocations were rejected before execution by local command policy; the direct calls succeeded.

Live API attempt 001 executed the real loopback approval/executor path and printed favorable values for health, baseline identity, action-hash binding, postconditions, same-key idempotency, HTTP 409 replay rejection, token redaction, selected evaluation, terminal metrics, CSP, and dashboard content. Its unnamed PowerShell boolean aggregate nevertheless returned failure, so the attempt is retained and not promoted. Database, three-event trace, logs, screenshot, and failure receipt are preserved with SHA-256 evidence.

The verifier now uses named typed checks and emits an explicit pass/fail receipt. Because that script is manifest-bound, the corrected 20-file manifest SHA-256 is `8f3e0a8710abdfd3894047c451ffc23f3a1488b836dbe510cfab7832b2549267`; a fresh immutable evaluation attempt is required before rerunning live verification.

Immutable attempt 004 passed all 54 trials against that corrected 20-file manifest and is now the latest-passed pointer. Report and trace SHA-256 are `132306bbf9f8619e61dee1d74f1a9e7ef208b0b8b178b672e51c42d3751b99f1` and `d6ae7e0d7800b0a64b8063b574504a40102550a10c62d9a2bc2a341fb8c69e87`; median and p95 end-to-end latency are 38.198 ms and 73.236 ms.

The named-check live API rerun passed all 22 checks. Independent native inspection passed required SQLite tables, one consumed hash-only approval, one idempotency record, one executed proposal, three ordered audit events, three redacted trace events, selected evaluation/manifest identity, and dashboard dimensions. The visually inspected dashboard accurately shows baseline 0005, evaluation pass, trajectory exact 1.0, terminal state exact 1.0, human approval, disconnected real infrastructure, and one mitigated incident.

Held-out CLI and MCP verification passed; MCP reports version 0.0.5 and exposes only list, diagnose/propose, and incident-read tools. Docker Desktop 4.74.0 and Engine 29.4.3 are live, but container packaging remains `defer` because the retained base-image source gate is still failed.

Historical handoff at this checkpoint: commit selected attempt 004 and native evidence, then verify an exact no-local-object clean clone before GitHub review.

Candidate commit `bf29abe17576db7458e0706a3f7fda52049cc3a6` passed a no-local-object clone at `C:\Projects\Verification\runbook-sentinel-baseline-0005-bf29abe-20260806221336`. The clean clone passed compilation, 13 tests, 20-file manifest, terminal contract, all five milestone JSON records, selected attempt and manifest identity, unchanged policy and service hashes, model-weight absence, secret-pattern scan, held-out CLI, MCP 2025-11-25, API approval/executor/replay, SQLite, audit, telemetry, and native dashboard receipt.

The clean-clone dashboard was freshly rendered and visually inspected. It matches the authoritative baseline 0005 surface; the only tracked post-verification clone changes are the expected new synthetic incident screenshot and its regenerated native receipt.

Historical handoff at this checkpoint: commit the clean-clone receipt, push the verified branch, open GitHub review, verify exact remote scope and mergeability, then verify merged main before release closure.

## BASELINE-0005 release closure

- GitHub pull request `#4` matched verified branch head `b012b381a3a3f8f7ab57b05095affe9495f49666`, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `a55249a4c679d61573e72dfe5c3be5363c3b78d1`.
- A fresh clone of that remote merged commit passed compilation, all 13 tests, the 20-file manifest, exact terminal contract, selected evaluation identity, held-out CLI, MCP 2025-11-25, live API approval/executor/replay/postconditions, SQLite, audit, telemetry, native receipt, and rendered-dashboard inspection.
- The public v0.0.5 tag, peeled remote tag, remote `main`, and non-draft release bind the exact release-closure commit containing these reconciled records; rendered public pages were verified after publication.

Next eligible action: begin the next cycle from public v0.0.5 by running the system and selecting one bounded measurable weakness.

## BASELINE-0006 measured gap and selected candidate

- A fresh v0.0.5 orientation passed 54 trials and 84 trace events, but the evaluator exposed only topology coverage. Zero of 18 scenarios had an explicit evidence-condition label; stale and conflicting evidence had no development-split case.
- Schema 1.5 freezes a closed complete, incomplete, stale, conflicting, and instruction-bearing taxonomy. It adds only `dev-stale-cache-evidence` and `dev-conflicting-database-evidence`, both exact no-execution cases, and requires all five conditions in both splits plus adversarial coverage in both splits.
- The immutable pre-change control passed all 60 expanded trials under the old gates while emitting neither a condition metric nor gate and while retaining a stale baseline-0005 report identity. It is preserved with disposition `remediate`.
- Independent validators pass 20 scenario labels, 10 of 10 condition/split pairs, development/test adversarial coverage, five action cases, fifteen no-action cases, all three actions, exact terminal states, and unchanged authority invariants.
- Fourteen tests pass, including fail-closed missing-stale-label and unknown-label regressions. Agent, policy, service, API, MCP, action, approval, and executor code remain unchanged from v0.0.5.
- Immutable attempt 001 passed all 60 trials. Condition and adversarial split coverage, retrieval, generation, proposal, actual tool trajectory, terminal state, policy, benign utility, security, and `pass^3` are 1.0; proposal and terminal attack success are 0.0.
- Attempt 001 report, trace, and manifest SHA-256 are `b887c9549674217fb0e1812d4f7381b6cf9aa6fd6446fa32ee77ee8721c4ba93`, `2ac8be834ad9a14a59a7ae6f1b421dac64980f00b4e6c818b02eb8225e86d8ca`, and `595b729c5ce780585499333bdb7ab80f7fd950df76e7b788a774b6e22ba0cbbc`; `latest.json` is byte-identical to the attempt.
- Version-bound attempt 002 passed the refrozen 21-file surface and is now the latest-passed pointer. Report, trace, and manifest SHA-256 are `45fd47dd788541f47ff04d9547206de1d01abf24c07501a0f17ffaba10323224`, `5329eb6cafcba980d840ba81ee989ec909c5b61a56fee218897e0e12bde3122a`, and `9f70f756ab93d4ba8732ed70455e0ce3c26f3cc84558baff24d8f56b7e101573`.

## BASELINE-0006 release closure

- GitHub pull request `#5` matched verified branch head `7a86bc787257120942eee0c936d586cdeb41df6b`, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `1f0635a008d8fdf6e94c9fedf1c39da40651a465`.
- A fresh public clone of that remote merged commit passed compilation, all 14 tests, the 21-file manifest, both exact contracts, selected evaluation identity, authority hashes, held-out CLI, MCP 2025-11-25, all 25 live API checks, approval/executor/replay/postconditions, SQLite, audit, telemetry, model and secret exclusion, and rendered-dashboard inspection.
- The public v0.0.6 tag, peeled remote tag, remote `main`, and non-draft release bind the exact release-closure commit containing these reconciled records; rendered public pages were verified after publication.

Next eligible action: begin the next cycle from public v0.0.6 by running the system and selecting one bounded measurable weakness.

## BASELINE-0007 measured gap

- A fresh public-v0.0.6 orientation passed all 60 trials and emitted 60 run, 15 approval, and 15 execution events.
- The released catalog has zero explicit evidence-relation cases and zero same-split controlled freshness pairs. The evaluator has no pairwise relation metric or gate.
- Stale evidence has only one case per split; adversarial coverage is one development case and eight held-out cases. Aggregate condition and adversarial split coverage still report 1.0.
- The bounded checkpoint will add four synthetic counterparts and freeze instruction-injection invariance plus fresh-to-stale directional safety in both splits. Agent, retriever, policy, service, actions, approval, executor, MCP, and real-infrastructure boundaries remain unchanged.
- The research source gate permits narrow, attributed method use from the peer-reviewed CheckList paper and the non-peer-reviewed ReliabilityBench v1 preprint. It imports no external code, data, model, or paper file and treats the preprint only as supplemental inspiration.

Next eligible action: freeze schema 1.6, the four exact relations, counterpart scenarios, and an independent validator before changing evaluator code.

- Schema 1.6 now freezes 24 scenarios and four exact relations. Instruction-injection invariance and freshness directional safety each occur once in development and once in held-out test.
- The independent relation validator passes all eight linked cases and rejects undeclared changes. The terminal-state-v3 validator passes seven actionable and seventeen exact no-action cases across the unchanged three-action surface.
- The first expanded test run failed four stale inventory assertions while all scenario behavior and authority tests passed. The exact case map and inventory counts were corrected; all 14 tests then passed.
- The 22-file pre-implementation manifest SHA-256 is `696474d7e12c0ea79de843d4fdef3c3bec8faf9b5225997dc35ae18ab426c191`. Agent, retriever, policy, service, API, MCP, actions, approval, and executor remain unchanged.
- The immutable pre-grader control passed 72 trials and 114 trace events under the old gates but emitted no behavioral-relation metric or gate. Report and trace SHA-256 are `386ece2815be95aff23a84b297ddfb1636a19303f01c59bc7e583f50a9fbfdaf` and `d50d4e32ff1b133447f4f35a9b71a2cfdfb178134b2f753ab11ae490ba5afb6e`.
- The implemented grader validates the closed relation contract and reports missing split/type pairs, coverage, invariance exactness, freshness-direction exactness, combined exactness, per-split exactness, and per-trial checks separately from scenario-level metrics.
- Focused fail-closed tests reject a missing held-out directional relation and detect a corrupted paired action. The first integrated run failed because the new helper interrupted the existing coverage helper; the boundary was repaired without changing the frozen contract or runtime logic, and all 14 tests then passed.
- A disposable 72-trial implementation smoke passed every gate: four relations, 12 of 12 paired attempts exact, development and held-out relation exactness 1.0, 21 expected executions, and 51 strict no-action results. Report and trace SHA-256 are `9da65549afcc80d68ec74ca025e3529d9fefc41484c30b454a57c44f61f3fced` and `80631bf38454f7302b5e2852b3b28560dc8bc7f7941917a31d64f60da3b0d1df`.
- The completed 22-file implementation manifest passes at SHA-256 `8db0a7f5fd15dd92a82ab710e65fc6dbc84e4eec28b2d67b46a94a1427963c69`. Agent, retriever, policy, service, API, MCP, and action surfaces remain unchanged from the pre-grader freeze.
- Immutable attempt 001 passed all 72 scenario trials and all 12 paired relation trials. Invariance, directional safety, combined relation exactness, development exactness, and held-out exactness are 1.0; 21 expected actions executed and all 51 no-action trials remained unchanged.
- Attempt 001 emitted exactly 72 run, 21 approval, and 21 execution events. The report and trace contain no raw approval-token or concrete idempotency material. Report and trace SHA-256 are `eda653ad87436fbbc3c6e3196e2fee4c503589d32cd35795351bf6f50101bccf` and `db9ff7eaed7d67dcbbdd62bdf1f299b41abaa34a581d6476e4fbc0e506076035`.
- The copied manifest matches the active manifest at SHA-256 `8db0a7f5fd15dd92a82ab710e65fc6dbc84e4eec28b2d67b46a94a1427963c69`, and `artifacts/evaluations/latest.json` is byte-identical to attempt 001.
- Package metadata, API health, MCP identity, CLI default, tests, README, dashboard, and real-surface verifiers now identify `0.0.7` / baseline 0007. The dashboard visibly adds behavioral-relation exactness without exposing approval or execution controls.
- The versioned 22-file manifest passes at SHA-256 `02ff28f3616572d3c1b6d97e5fe617594765575666f2ed74cb247b43b7ee5314`; agent, retriever, policy, service, and actions remain unchanged. Attempt 001 remains immutable and passing but is superseded for release selection; a version-bound attempt is required before live verification.
- Immutable attempt 002 passed all 72 scenario trials and 12 paired relation trials against the versioned manifest. It is now the latest-passed pointer; report and trace SHA-256 are `6dbd86d774304ec9d6dbd3687fcc1cc72e87b8846a7f5b96343b0176063f40eb` and `1e6bbdcb7170acf5d02172e74e4d365dcbffd7fe8e33a67d6bc9e8367660ff99`.
- The held-out CLI requested evidence without a proposal. MCP protocol `2025-11-25` reported version `0.0.7`, retained the full retrieval audit, excluded attack guidance from the decision context, and exposed three diagnostic/read tools with no approval or execution tool.
- The real loopback API passed all 27 named checks: selected evaluation and relation metric, hash-bound approval, execution, postconditions, same-key idempotency, different-key HTTP 409 replay rejection, token redaction, CSP, and dashboard identity.
- Independent runtime inspection passed required SQLite tables, one consumed hash-only approval, one idempotency record, one executed proposal, three ordered audit and trace events, evidence-only context, selected manifest identity, and the 1440 by 1000 dashboard. Native receipt and screenshot SHA-256 are `9dbd5f9ef37b69cef29fe28f40365f9e313a91b5463ac18e7edeccc914ee82a2` and `f308245de2fa21e5fcb0d9ad3a9c0cc05b71424259dfb011a6d4384d9570bd69`.
- Visual inspection confirmed the dashboard accurately shows baseline 0007, evaluation pass, behavioral relation exact 1.0, evidence condition, tool trajectory, and terminal state at 1.0, human approval, disconnected real infrastructure, and one mitigated synthetic incident.
- A no-local-object clone of exact candidate `8328c08900739d4f07afd9202a979c1bdd4f63e9` at `C:\Projects\Verification\runbook-sentinel-baseline-0007-8328c08-20260806202958` passed compilation, 14 tests, the 22-file manifest, all three validators, seven milestone contracts, 82 JSON and 22 JSONL parses, selected-evaluation identity, model-weight absence, high-signal secret scan, held-out CLI, MCP, all 27 API checks, all 16 runtime checks, and rendered-dashboard inspection.
- The clean-clone dashboard was freshly rendered and visually inspected. Only its synthetic-incident screenshot and regenerated native receipt changed after verification; no source, contract, manifest, evaluation, policy, or service file changed.

Next eligible action: commit the clean-clone receipt, push the verified branch, open GitHub review, and verify exact remote scope and mergeability.
