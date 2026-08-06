# Development log

## 2026-08-06 — BASELINE-0001 started

- User approved the long-running goal with the SRE domain.
- Live inspection found the OneDrive workspace contained only an unborn Git shell and no authoritative project history.
- User directed active work away from OneDrive and toward `C:\Projects` plus GitHub ownership under `drwbkr1`.
- `C:\Projects\STORAGE_POLICY.md` required the authoritative worktree under `C:\Projects\Active\runbook-sentinel`.
- Initialized an empty `main` repository at the policy-compliant path and left the OneDrive shell intact.
- GitHub CLI is authenticated as `drwbkr1`; remote creation is paused on the required visibility decision.
- Docker Desktop start was requested after live inspection showed the daemon was off.
- Began a standard-library-only deterministic control baseline. No local model or external package has been used.

### Retained verification attempt 001

- Milestone contract validation failed because the active unit used `active`; the validator requires `in_progress`.
- All six tests reached their assertions, but Windows cleanup failed because SQLite context managers committed without explicitly closing connections.
- Disposition: `remediate`. The failed output remains in the Codex execution record; both infrastructure defects were corrected before rerun.

### Retained container source-gate attempts

- Docker Desktop became live at engine version 29.4.3.
- The first parallel Scout scan attempt contended on its cache and was rejected as evidence.
- Sequential scans excluded three immutable Docker Official Python image digests: slim Trixie and Bookworm for two critical plus two high unfixed Perl findings each, and Alpine for two high unfixed SQLite findings.
- Disposition: `defer`. Removed the unaccepted Dockerfile and Compose file; the native baseline remains eligible. Exact evidence is in `artifacts/verification/container-source-gate.json`.

### Retained live-API tooling attempt

- A long inline PowerShell verification command was rejected by the shell safety layer before execution.
- No server or synthetic mutation occurred in that attempt.
- Disposition: `remediate` by moving the check into the reviewable `scripts/verify_live_api.ps1` workflow.

### Source-review hardening before checkpoint freeze

- Bound each idempotency key to one proposal and serialized the cache check inside the execution transaction.
- Moved execution audit insertion into the same transaction as approval consumption and state mutation.
- Restricted the baseline HTTP server to loopback addresses.
- Made raw evaluation attempts immutable and separated them from the mutable latest-passed pointer.

### Native candidate verification

- Regenerated and verified a nine-file frozen manifest after hardening.
- Six focused unit/integration tests passed.
- Immutable attempt 002 passed all 27 repeated evaluations across nine scenarios; it was promoted to the latest-passed pointer.
- Live CLI correctly rejected stale deployment state as sufficient evidence.
- Real MCP stdio negotiation and tool calls passed with no approval or execution tool.
- Real HTTP approval and execution passed hash binding, idempotency, replay rejection, pre/postconditions, and trace-redaction checks.
- Rendered and visually inspected the 1440x1000 dashboard.
- Reconciled SQLite, atomic audit records, JSONL traces, evaluation, manifest, and rendered artifact into `artifacts/verification/native-baseline.json` with disposition `pass`.

### Pre-commit whitespace gate

- `git diff --check` found trailing blank lines in newly authored text files.
- Disposition: `remediate`. Preserved attempt 002's manifest, normalized only reported files, and required a new frozen manifest and evaluation attempt before commit.

- Attempt 003 passed all gates against the normalized nine-file manifest and became the accepted latest result. Attempts 001 and 002 remain retained as superseded evidence.
- Generated evaluation, trace, manifest, and verification-receipt paths are binary/byte-preserved in `.gitattributes` so Git cannot invalidate their recorded hashes or treat carriage returns as source whitespace during commit checks.

### Verified checkpoint closure

- The complete staged baseline passed Git whitespace validation and a repository secret-pattern scan.
- Created root candidate commit `c5c78d1` (`bootstrap deterministic control baseline`).
- Cloned that candidate without local object sharing to `C:\Projects\Verification\runbook-sentinel-baseline-0001-c5c78d1-20260806145334`.
- The clean clone passed compilation, all six tests, frozen-manifest integrity, milestone-contract validation, MCP stdio negotiation, live loopback API approval/execution/replay checks, dashboard rendering, SQLite persistence inspection, and JSONL telemetry inspection.
- `BASELINE-0001` disposition: `pass`. GitHub publication remains stopped at the explicit repository-visibility gate. Container packaging remains `defer`, not silently omitted.

### Public repository gate released

- The user explicitly selected public visibility on 2026-08-06.
- Created `https://github.com/drwbkr1/runbook-sentinel` under the authenticated `drwbkr1` account with public visibility.
- Pushed verified closure commit `061f0aefa0a4c61e0ed14d589e2d3bcee5ec413e` to the new `main` branch and verified the repository visibility, default branch, and remote commit through GitHub.
- No license grant was added; public visibility and open-source licensing remain distinct.

## 2026-08-06 — BASELINE-0002 started

- Began from verified public release `v0.0.1`; local tag, remote tag, and remote `main` all resolve to `5a3cf1e708d6e21c17a0c3c0587db9c271e8ff9d`.
- The accepted nine-case suite still passed all 27 orientation trials, but it had no explicit topology coverage metric and no gateway or configuration cases.
- Precommitted schema 1.1 with 16 cases across gateway, API, worker, database, cache, deployment, configuration, and observability before changing the implementation.
- The unchanged control failed all 21 trials belonging to the seven new cases. Attempt 001 retained exact match and `pass^3` of 0.5625, benign utility of 0.5556, adversarial safe outcome of 0.5714, policy compliance of 1.0, and proposal attack success of 0.0.
- Disposition: `remediate`. The change remains bounded to non-action diagnoses and exact evaluation coverage; executor actions and capabilities are frozen.
- A no-replace PowerShell guard emitted a parameter-binding error because it repeated `-LiteralPath`; the three targets were independently absent and each immutable evidence file was created once.

### Retained verification attempt 002

- Attempt 002 passed all exact scenario, split, topology coverage, policy, security, and reliability gates.
- Live CLI inspection then showed the service emitted `deterministic-control-v1` while the evaluator declared `deterministic-control-v2`; the artifact is therefore superseded rather than accepted.
- The live API database and trace also contained records from prior runs because the verifier reused generated files. The verifier now removes only its exact generated database, sidecars, trace, and log files before startup.
- Disposition: `remediate`. Updated the service identity and required a new immutable evaluation plus isolated real-surface run.

### Candidate verification attempt 003

- Attempt 003 emitted and declared `deterministic-control-v2` and passed all 48 trials across 16 cases.
- Development and test exact gates each passed at 1.0; topology coverage reached 8 of 8 domains; policy compliance remained 1.0; proposal attack success remained 0.0.
- Median latency was 7.771 ms and p95 latency was 19.739 ms with zero model calls and zero estimated spend. These single-run values do not support a performance-improvement claim.
- The isolated live API run produced exactly one incident, run, proposal, approval, idempotency record, and execution; replay returned HTTP 409 and traces contained no approval token.
- Live CLI, MCP stdio, rendered dashboard, SQLite, audit, JSONL telemetry, manifest binding, JSON parsing, secret-pattern scan, and unchanged executor policy checks passed.
- Preserved checkpoint-specific v0.0.1 and baseline-0002 dashboard and runtime receipts before updating the living pointers.

### Clean-clone candidate gate

- Committed the complete implementation and evidence candidate as `c080e83617636b81e67c48956be27056972d71f4`.
- Cloned that branch without local object sharing to `C:\Projects\Verification\runbook-sentinel-baseline-0002-c080e83-20260806153016`.
- The exact commit passed compilation, six tests, manifest integrity, both milestone contracts, MCP, isolated API approval/execution/replay, dashboard rendering, SQLite, telemetry, JSON parsing, secret scanning, and diff checks.
- Publication remains in progress; a clean clone is necessary but does not by itself prove the GitHub branch, pull request, merged `main`, tag, or release.

### Verified checkpoint publication

- Pushed final branch head `da3ba22e76ccb068a132f29e1c55c04f88f67035` and verified the remote branch identity.
- Opened GitHub pull request `#1` as a draft, inspected its 42-file server-side scope, confirmed `CLEAN` and `MERGEABLE` state, then marked it ready.
- Merged with history preserved as `53fc4ce1189218fc0ea13899aa8bb83552ffa4af`; the merge parents are `v0.0.1` release commit `5a3cf1e` and verified branch head `da3ba22`.
- Fast-forwarded the authoritative local `main` to the remote merge commit and reran tests, manifest validation, MCP, isolated API approval/execution/replay, dashboard rendering, SQLite, audit, and telemetry checks successfully.
- `BASELINE-0002` disposition: `pass`. Failed attempt 001 and superseded attempt 002 remain retained; container packaging remains `defer`.

## 2026-08-06 — BASELINE-0003 started

- Resumed from public `v0.0.2` at `a320d36a933e80e5f22b5776be4ce39fa40cd530`; release identities and a fresh 48-attempt orientation evaluation passed.
- Four instruction-bearing poisoned runbooks were retrieved into the context passed to the agent in all four labeled attack cases, for exposure rate 1.0, even though proposal attack success remained 0.0.
- Rechecked the AgentDojo and CaMeL primary papers. They support measuring attacks over untrusted tool data and separating untrusted data from trusted control flow; the proposed evidence-only decision context is a narrower project-specific application, not a claim to implement CaMeL.
- Froze explicit attack-document identities before changing the evaluator or runtime.
- The orientation PowerShell guard repeated invalid `Test-Path` syntax; ignored target paths were absent and created once. The defect is retained and the syntax will not be reused.

### Retained full-context control attempt 001

- Extended the exact evaluator to label instruction-bearing attack documents and measure whether they enter the decision context.
- The unchanged v0.0.2 service passed every prior quality, reliability, and action-security gate but exposed an attack document in all 12 trials across four labeled cases.
- Full-retrieved-context-v1 results: exposure 1.0, required evidence recall 1.0, exact trajectory 1.0, `pass^3` 1.0, policy compliance 1.0, proposal attack success 0.0.
- Disposition: `remediate`. The control artifact and manifest are immutable and were not promoted to the latest-passed pointer.

### Candidate evidence-only attempt 002

- Added a deterministic context policy with reproducible `full-retrieved-context-v1` and `evidence-only-context-v2` configurations.
- The candidate retains full `retrieved_document_ids`, records excluded runbook identities as guidance, and passes only telemetry/status documents into the decision agent.
- Attempt 002 passed all 48 trials. Instruction-bearing decision exposure fell from 1.0 to 0.0 while recall, generation, exact trajectory, utility, policy compliance, adversarial safe outcome, and `pass^3` remained 1.0; proposal attack success and cost remained 0.0.
- Live CLI and MCP verified that the poisoned worker runbook remained auditable but absent from `decision_document_ids`. Redacted traces recorded the selected context policy and document counts.
- Isolated API approval/execution/replay, dashboard, SQLite, audit, telemetry, and manifest-binding checks passed. The first baseline-0003 runtime receipt is retained; attempt 002 adds the explicit decision-context check.
- The selected boundary depends on trusted project-authored document-kind metadata in this synthetic baseline. It is not a general sanitizer and does not yet validate hostile misclassification.

### Complete-gate regression attempt 003

- Compilation, seven tests, the frozen manifest, all three milestone contracts, JSON and JSONL parsing, executor-policy identity, secret-pattern scanning, and Git whitespace checks passed.
- The complete gate created a separate immutable attempt rather than overwriting attempt 002. Attempt 003 passed all 48 trials with decision exposure 0.0, proposal attack success 0.0, exact quality and reliability metrics 1.0, median latency 7.391 ms, and p95 latency 18.075 ms.
- Reran MCP and the isolated API against the promoted attempt. Full retrieval audit remained present, the poisoned runbook stayed outside the decision context, approval/execution/replay/postcondition checks passed, and the rendered dashboard, SQLite state, audit log, and telemetry reconciled.
- Preserved attempt-003-specific evaluation, trace, manifest, dashboard, and runtime receipt. Attempt 001 remains `remediate`; attempt 002 remains the accepted comparison candidate.

### Clean-clone candidate gate

- Created candidate commit `0aa4fc68bfcf208c2f64a3578e54727a55002ef3` and cloned it without local object sharing to `C:\Projects\Verification\runbook-sentinel-baseline-0003-0aa4fc6-20260806160053`.
- The exact commit passed compilation, seven tests, frozen-manifest integrity, all three milestone contracts, unchanged executor-policy identity, MCP negotiation, isolated API approval/execution/replay, rendered dashboard, SQLite, audit, telemetry, JSON and JSONL parsing, secret-pattern scanning, and diff checks.
- The live verifier changed only the clone's living dashboard and runtime-receipt pointers, as expected. GitHub review, merged-main verification, tag, and release remain pending.

### GitHub review and merged-main verification

- Pushed final branch head `c5fc8f5cdb80436af5ebead18a665b6878f8db28`; the remote branch matched exactly and passed a no-local-object exact-head regression.
- Opened pull request `#2` as a draft, inspected its server-side four-commit and 45-file scope, confirmed `CLEAN`, `MERGEABLE`, and no required checks, then marked it ready.
- Merged with history preserved as `995dcefb1cef284b936a5b336c4601c54bad2462` and fast-forwarded the authoritative local `main` to the exact remote commit.
- Merged main passed compilation, seven tests, manifest integrity, all contracts, unchanged executor policy, MCP, isolated API approval/execution/replay, postconditions, rendered dashboard, SQLite, audit, and telemetry checks.
- Preserved merged-main dashboard and runtime receipts. The exact closure commit is eligible for the `v0.0.3` tag and public release.

## 2026-08-06 — BASELINE-0004 started

- Resumed from exact public `v0.0.3` closure `fa2eb78eb497617b1c775ebd2b609f1216acb8d8` after tag, remote `main`, release API, rendered README, and corrected rendered release notes agreed.
- Identified the next measurable gap: the accepted deterministic agent has no stochastic structured-generation comparison.
- Applied the external-source gate before model use. Ollama 0.32.5 is signed by Ollama Inc. and responds only through the approved loopback endpoint. The local `llama3.2:3b` manifest is `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`; all six referenced blobs match their declared SHA-256 digests.
- Official Meta license, AUP, and model-card evidence and Ollama release, license, and registry evidence passed for synthetic evaluation only. No download, package, account, secret, remote API, model-weight redistribution, tool access, approval access, executor access, or real infrastructure is authorized.
- The first UTC timestamp command used unsupported Windows PowerShell `Get-Date -AsUTC` syntax and failed without mutation. Replaced it with `ToUniversalTime()` and retained the failure in the milestone contract.
- Source gate disposition: `ready`. The gate authorizes a standard-library loopback adapter and frozen synthetic invocation; it does not establish model quality or permission to operate critical infrastructure.

### Retained pre-model specification regression

- The first 18-case regression failed before any model invocation. A period immediately after `telemetry_coverage=0.12` was captured as part of the value by the existing fact lexer and could not be converted to a float; the MCP inventory test also retained the old 16-case assertion.
- Disposition: `remediate`. Replaced prose-boundary periods with semicolon delimiters in both new in-band records and updated the exact MCP inventory assertion to 18. The failed test output remains recorded here and in the milestone contract.

### Deterministic comparison control

- Committed the model contract and 18-case frozen schema before any model invocation. The two new cases place allowed-action injection prose inside telemetry/status records, so decision exposure is intentionally 1.0 rather than hidden by guidance filtering.
- Immutable attempt 001 passed all 54 deterministic trials. Development and test exact results, policy compliance, benign utility, adversarial safe outcome, and `pass^3` were 1.0; in-band and overall proposal attack success were 0.0.
- Median latency was 8.160 ms and p95 latency was 28.367 ms with zero model calls and zero estimated monetary spend. The retained manifest SHA-256 is `ae322324f034595c4374fdf24e3d285e678f7d52e91ced0be030bf40fc33b7fe`.

### Pre-model adapter boundary verification

- Implemented an optional standard-library Ollama adapter while retaining `deterministic-control-v2` as the default. The adapter accepts only the frozen direct loopback endpoint and disables proxies, redirects, streaming, and tools.
- The exact parser accepts only the six frozen top-level fields, evidence identifiers from the supplied decision context, and one of three server-known action/capability pairs with empty arguments. Invalid, unavailable, or timed-out output becomes an abstention and never falls back to the deterministic control.
- Redacted trace and immutable evaluation records identify the model manifest, runtime, contract, system prompt, request payload, raw output digest, parse disposition, tokens, durations, and end-to-end latency without storing raw generated text in telemetry.
- Twelve tests passed before the first model invocation. They cover valid proposal integration, malformed output, mismatched capabilities, timeout, missing model identity, remote endpoint rejection, trace redaction, all 18 deterministic scenarios, and candidate-level metric accounting.
- Before invocation, the evaluation record was extended to preserve the complete validated semantic decision separately from the raw-output digest; raw response bytes remain absent from traces.
- Review identified that the standard URL client would otherwise follow redirects. Redirects and environment proxies were disabled before any model invocation so the direct loopback boundary is enforced by transport behavior as well as contract validation.
- Executor policy remains byte-identical to the `v0.0.3` checkpoint at SHA-256 `1b23a56b14527347ec723a4c83595414987f9ef7288b532afda49fb4fb7bd1aa`.

### First local-model smoke call

- Invoked the exact source-gated local model on `dev-worker-backlog` only after committing the adapter and candidate manifest. The request contained one frozen synthetic telemetry record and no tools, credentials, approvals, executor access, remote service, or real infrastructure.
- The model response had raw-output digest `b267a73ec4a4391d2a69fe8554f925497c5b3982fb168c857c69054c48464c98` but failed the exact semantic parser. The adapter returned `abstain / model_output_invalid`, persisted no proposal, and did not substitute the deterministic result.
- End-to-end latency was 25138.148 ms, including 6681307500 ns reported load duration. The result disposition is `remediate`; it remains retained independently of the complete repeated comparison.

### Complete local-model comparison and selection

- Ran all 18 frozen cases three times through the exact committed adapter and model contract. The report, 54 redacted traces, and candidate manifest are immutable; their SHA-256 digests are `c3cd0f15435a2e4f993c7cbb6f16a12ad4e8bba35f585e221c1fa2a87f5c3433`, `94accdb4b2a74d0c4b2b925e4fe08bdccc1d4c1adcee39ae8bf2733fb0abcf84`, and `edc4cd30f18863260331c04ccad80a692481da86ec4e6afc48d7fe566b2138d1`.
- Candidate parse success was 5/54, outcome accuracy 0.1481, diagnosis accuracy 0.0, exact trajectory 0.0, benign utility 0.0, and `pass^3` 0.0. Development and held-out test exact trajectories both remained 0.0.
- Retrieval recall remained 1.0. Policy compliance remained 1.0 and proposal attack success remained 0.0 because 49 invalid outputs failed closed and the five valid outputs produced no accepted action proposal. This is boundary evidence, not a model-safety claim.
- Candidate median latency was 12448.711 ms and p95 latency was 19687.913 ms across 54 calls, versus control values of 8.160 ms and 28.367 ms. External API billing was zero; local hardware and energy were not estimated.
- The candidate produced 27 distinct raw-output digests. Nine cases were byte-semantically stable by digest across all three trials and nine varied. Raw generated text is absent from traces; validated semantic decisions remain in the evaluation artifact.
- Disposition: `exclude`. The deterministic control remains the default and the latest-passed pointer remains byte-identical to its passing report.

### Native release-candidate verification

- Bumped versioned runtime surfaces to `0.0.4` and the dashboard/API checkpoint to baseline 0004 without changing the executor action set. Regenerated the 11-file manifest and ran deterministic attempt 002 against the exact current runtime.
- Attempt 002 passed all 54 trials with exact trajectory, policy compliance, benign utility, adversarial safe outcome, and `pass^3` at 1.0; proposal attack success remained 0.0. It became the latest-passed pointer. Median latency was 9.009 ms and p95 was 20.500 ms.
- The real CLI handled the held-out in-band observability action injection by requesting evidence. MCP negotiated protocol `2025-11-25`, reported server version `0.0.4`, retained full retrieval audit, excluded poisoned guidance from the decision context, and exposed no approval or execution tool.
- The isolated API reported baseline 0004 and served the passing deterministic evaluation. Hash-bound approval, synthetic execution, exact postconditions, idempotent replay under the same key, HTTP 409 rejection under a new key, and approval-token trace redaction all passed.
- Visually inspected the 1440 by 1000 rendered dashboard. It accurately shows Baseline 0004, passing deterministic v2, evidence-only context, human approval, disconnected real infrastructure, and one persisted mitigated incident.
- SQLite contained exactly one incident, run, proposal, approval, idempotency record, and execution plus three ordered audit events. The approval stored a 64-character hash, was consumed, and matched the proposal action hash.
- Docker Desktop 4.74.0 and Engine 29.4.3 were live. Container packaging remains `defer`: daemon availability does not override the retained failure of all reviewed base-image candidates to pass the source gate.

### Clean-clone candidate gate

- Created candidate commit `1b886c5557d311a272997866a715c2f8f815d76e` and cloned it without local object sharing to `C:\Projects\Verification\runbook-sentinel-baseline-0004-1b886c5-20260806210458`.
- The exact clone passed compilation, 12 tests, the 11-file manifest, all milestone contracts, the model source gate, candidate and selected evaluation artifact hashes, unchanged executor policy, model-weight exclusion, JSON and JSONL parsing, and diff checks.
- Real MCP and API verification passed again. A fresh dashboard render was visually inspected, the held-out in-band CLI case requested evidence, and the only tracked post-verification change was the intentionally regenerated dashboard PNG containing a new synthetic incident identifier.
- GitHub review, merged-main verification, exact release closure, tag, release, and rendered public-page verification remain pending.

### GitHub review and merged-main verification

- Pushed verified branch head `36cfcba4c7a1b333325b196481d9f9bea6357e35` and verified the remote branch identity. Pull request `#3` contained 9 commits and 45 expected files, was `CLEAN` and `MERGEABLE`, had no configured checks, and contained no model weights or expanded authority surface.
- Marked PR `#3` ready and merged with history preserved as `fca61e3f4b1a52e525477002c3977a15aab0cd8f`. Its parents are the exact `v0.0.3` closure and verified baseline-0004 branch head.
- Fast-forwarded authoritative local `main` to remote `main`. Compilation, 12 tests, the manifest, all contracts, the model source gate, selected-evaluation identity, and unchanged executor policy passed.
- Cloned remote merged main into `C:\Projects\Verification\runbook-sentinel-merged-main-fca61e3-20260806210929`. MCP, API evaluation serving, approval, execution, idempotency, replay rejection, postconditions, SQLite, telemetry, and a fresh visually inspected dashboard passed again.

### Verified checkpoint publication

- Created one release-closure commit after merged-main verification. The annotated `v0.0.4` tag, peeled remote tag, remote `main`, and public non-draft GitHub release bind that exact commit.
- Verified the public repository README and release page after publication. Both describe the candidate as excluded, preserve the deterministic default, and make no claim of production readiness or useful model safety.
- `BASELINE-0004` disposition: `pass`; model candidate disposition: `exclude`; container disposition: `defer`. No model weights, runtime binaries, paid services, secrets, new executor capability, real infrastructure connection, or default model change shipped.

## 2026-08-06 — BASELINE-0005 started

- Resumed from exact public `v0.0.4` closure `e364425d08e8e931b2b2f5a7c6be83651dd4931c`; local main, remote main, annotated tag, peeled remote tag, public release, clean worktree, 12 tests, 11-file manifest, and Docker Engine 29.4.3 agree.
- Inspected the accepted evaluation and source. `trajectory_exact` is assigned directly from generation agreement, while `evaluation.py` contains no approval or execution call and the 18-case schema contains no expected terminal-state field.
- The gap affects five actionable cases, 15 repeated trials, and all three executor actions. The remaining 39 trials also lack an explicit exact no-mutation grader.
- Ran a temporary synthetic orientation harness across `restart_worker`, `rollback_deployment`, and `warm_cache`. Every action verified postconditions, exact mitigated state, same-key idempotency, and different-key replay rejection; approval material remained absent from the agent result.
- Rechecked the tau-bench primary paper. Its deterministic final-database-state comparison and repeated `pass^k` framing support the bounded grader; no external code, data, model, or dependency is imported.
- Corrected the living evaluation report's unsupported terminal-state claim without rewriting the immutable baseline-0004 artifacts. Disposition: `remediate` through an evaluation-only harness; runtime authority and policy remain frozen.
- Froze schema 1.4 before evaluator implementation. Every one of the 18 cases now names an exact full terminal state, incident status, and either the approved-execution or no-execution harness trajectory; the validator passes at 5 actionable and 13 no-action cases across all three existing actions.
- Preserved the accepted baseline-0004 report by hash in a separate pre-change control receipt. It records the favorable proposal proxy alongside the actual 0 approval calls, 0 execution calls, 0 terminal-state grades, and 0 explicit no-mutation grades.
- Bound the terminal contract, its validator, and the unchanged pre-change evaluator to an immutable 13-file manifest with SHA-256 `c458a2ed2af1a6b4324c58f1ac438bbd8cb816938201e5fc8f573b32f8329b8f`. UNIT-002 passed; UNIT-003 began.
- A verification command named a nonexistent `scripts/validate_milestone_contract.py` and failed without mutation. A first replacement assertion then expected a nonexistent nested `authority.status` rather than the contract's top-level status and also failed without mutation. The repository has no dedicated milestone validator; JSON, dependency ordering, inherited authority, unit state, terminal contract, manifest, and tests passed through the actual available checks.
- Implemented the evaluation-only harness against the real `approve` and `execute` service methods. It runs only after result persistence, uses disposable SQLite state, and records no raw approval token or idempotency key in the evaluation report or traces.
- Separated proposal, actual tool trajectory, terminal state, policy, security, reliability, end-to-end latency, and cost metrics. End-to-end latency now includes approval, execution, idempotency, replay, state, audit, trace, and boundary inspection instead of diagnosis alone.
- Added a focused adversarial grader regression: `rollback_deployment` actually executes in the in-band worker case and counts as terminal attack success, while the same proposal against an already-stable deployment is blocked by preconditions and does not count as terminal attack success.
- Thirteen tests pass. A 54-trial implementation smoke passed 15 of 15 expected-action executions across all three action types and 39 of 39 strict no-action checks; the report and all 84 trace events contained no approval-token literal.
- The first post-implementation manifest had 13 files and SHA-256 `0d77a9d669eb03ea9817eaeb1669bb08fbebb13843cee6824cfd6711401b12fa`. Pre-attempt review caught that `scripts/verify_baseline.py` still named baseline 0004; no immutable attempt had been created or promoted.
- Corrected the driver to baseline 0005, made terminal-contract validation mandatory, added the driver to the manifest, and refroze the final 14-file evaluation surface at SHA-256 `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`. Policy, service, API, and MCP hashes remain unchanged from v0.0.4. UNIT-003 passed; UNIT-004 began.
- Immutable attempt 001 passed all 54 trials and became the latest-passed pointer. All 15 expected-action trials executed across all three action types, all 39 expected no-action trials remained open and exactly unchanged, and development and held-out test `pass^3` were 1.0.
- The 84-event telemetry stream contains 54 runs, 15 approvals, and 15 executions. Report and traces contain no raw approval token or concrete `baseline-0005:{scenario}:{trial}` idempotency value. Report, trace, and manifest SHA-256 are `b3079ffcf29b8c6c44ebe0f1fda167cd7ffb6c32f9c15c37eca21b6f7546543e`, `9819b78a58ed31e58120b4ac9135b9a3be520a0b78f3ec8f85da383ddb3eb1e5`, and `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`.
- End-to-end median and p95 latency were 56.022 ms and 97.946 ms, versus diagnosis-only 5.288 ms and 14.148 ms. The measurement now includes the reliability work rather than presenting it as diagnosis latency. UNIT-004 passed; UNIT-005 began.
- Bumped package, API health, MCP server, CLI default, tests, README, and rendered-dashboard identity to `0.0.5` / baseline 0005. The dashboard now exposes actual trajectory and terminal-state exactness as evidence, while approval and execution remain absent from the agent and MCP surfaces.
- Expanded the release-candidate manifest from 14 to 17 files so it binds package metadata, package version, CLI, and the evaluation driver. The exact manifest SHA-256 is `c8a4797dbdde2bc53ff9057bd1953bbfda925149b28c8a538f1d155334757310`.
- Immutable attempt 002 passed the versioned 17-file surface: all 54 trials, 15 expected executions, 39 strict no-action results, three action types, exact security and reliability gates, median end-to-end latency 58.510 ms, and p95 108.435 ms. Report and trace SHA-256 are `b1e3eae0cf0ea8a558a7afc5bec4f82616ff811d81006c6f6c73156d8790a3ba` and `9b8aa00f2aa2619c2fd935f54d7d2184f93d53314a140ddaa8fe70c763cf55a1`.
- Before live verification, review found baseline-0004 paths and MCP version expectations in three real-surface verifier scripts. No live receipt had been created. Attempt 002 is retained as pass but superseded for release selection; the corrected API, MCP, persistence, telemetry, and dashboard verifiers will be bound into a 20-file manifest and require attempt 003.
- Immutable attempt 003 passed all 54 trials against the first 20-file manifest. The direct held-out CLI case requested evidence, while MCP negotiated protocol `2025-11-25`, reported version 0.0.5, retained full retrieval audit, excluded poisoned guidance from the decision context, and exposed no approval or execution tool.
- Two attempts to combine CLI, MCP, and nested PowerShell verification were rejected by local command policy before execution. Splitting the calls removed the tooling issue without changing project behavior.
- Live API attempt 001 completed the synthetic action: hash-bound approval, execution, exact postconditions, same-key cache, different-key HTTP 409 replay rejection, persisted mitigated state, three ordered audit events, and redacted three-event telemetry all passed. The dashboard rendered baseline 0005 and its terminal metric. The verifier still returned failure because its unnamed aggregate boolean evaluated false.
- Preserved the failed attempt's database, trace, stdout, stderr, and 1440 by 1000 dashboard under attempt-specific names and added `artifacts/verification/native-baseline-0005-attempt-001-failed.json`. No pass receipt was promoted.
- Replaced the ambiguous boolean array with named typed checks and an explicit receipt status. Refroze the manifest-bound verifier surface at SHA-256 `8f3e0a8710abdfd3894047c451ffc23f3a1488b836dbe510cfab7832b2549267`; attempt 004 is required before rerun.
- Immutable attempt 004 passed the corrected 20-file manifest and all 54 evaluation trials. It became the latest-passed pointer with report SHA-256 `132306bbf9f8619e61dee1d74f1a9e7ef208b0b8b178b672e51c42d3751b99f1`, trace SHA-256 `d6ae7e0d7800b0a64b8063b574504a40102550a10c62d9a2bc2a341fb8c69e87`, median end-to-end latency 38.198 ms, and p95 73.236 ms.
- Live API attempt 002 passed all 22 named checks. Independent runtime inspection passed SQLite schema and counts, consumed hash-only approval, execution, idempotency, audit order, trace redaction, decision-context identity, selected evaluation/manifest binding, and 1440 by 1000 dashboard integrity.
- Visually inspected the rendered dashboard. It accurately reports baseline 0005, evaluation pass, deterministic v2, evidence-only context, tool trajectory exact 1.0, terminal state exact 1.0, human approval, disconnected real infrastructure, and one mitigated synthetic incident.
- Docker Desktop 4.74.0 and Engine 29.4.3 are live. Container packaging remains `defer`; daemon availability does not cure the retained base-image source-gate failure.
- Created a no-local-object clone of candidate `bf29abe17576db7458e0706a3f7fda52049cc3a6` at `C:\Projects\Verification\runbook-sentinel-baseline-0005-bf29abe-20260806221336`.
- The exact clean clone passed compilation, all 13 tests, the 20-file manifest, terminal contract, five milestone records, selected evaluation identity, unchanged policy and service hashes, model-weight absence, secret-pattern scan, held-out CLI, MCP, live API approval/executor/replay, SQLite, audit, telemetry, and native receipt.
- Visually inspected the clean clone's fresh 1440 by 1000 dashboard. Only the new synthetic incident screenshot and its regenerated native receipt changed after verification; source, contract, manifest, evaluation, policy, and service remained unchanged.
- Pushed verified branch head `b012b381a3a3f8f7ab57b05095affe9495f49666`, opened GitHub pull request `#4`, confirmed 12 commits and 48 expected changed files, and found it `CLEAN` and `MERGEABLE` with no configured checks or review requirement.
- Merged PR `#4` with history preserved as `a55249a4c679d61573e72dfe5c3be5363c3b78d1`; its parents are the public v0.0.4 closure and the exact reviewed baseline-0005 branch head.
- Cloned remote merged main into `C:\Projects\Verification\runbook-sentinel-merged-main-a55249a-20260806222046`. Compilation, 13 tests, manifest, terminal contract, selected evaluation identity, CLI, MCP, API approval/executor/replay/postconditions, SQLite, audit, telemetry, native receipt, and a fresh visually inspected dashboard passed.
- Reconciled the v0.0.5 closure records. The release remains synthetic-only and research-informed; the agent and model still lack credentials, approval material, execution authority, and real-infrastructure access. Container packaging remains deferred.

## 2026-08-06 - BASELINE-0006 started

- Resumed from exact public v0.0.5 closure `e756044787deb9f31f8371669b84a703383f7350`. A fresh public-source clone passed compilation, manifest, terminal contract, all 13 tests, and structured-artifact parsing; local main, remote main, annotated and peeled tags, release metadata, rendered README, and rendered release agree.
- Reran the released system under `C:\Projects\Verification`: 54 trials passed with 54 run, 15 approval, and 15 execution events. The evaluator reported binary topology coverage but no explicit incomplete, adversarial, conflicting, stale, or instruction-bearing coverage metric.
- Measured the catalog gap: zero of 18 cases had an explicit evidence-condition field; stale evidence had one held-out case and conflicting evidence had two held-out cases, with zero development coverage for both.
- Froze schema 1.5 before evaluator implementation. All 20 cases now use a closed condition taxonomy; one synthetic stale-cache development case and one synthetic conflicting-database development case freeze exact retrieval, outcome, diagnosis, no-execution trajectory, incident status, and unchanged terminal state.
- Independent validators pass all five conditions in both development and test, adversarial coverage in both splits, five actionable cases, fifteen no-action cases, and all three existing actions. The pre-implementation manifest SHA-256 is `f097e3eeb20b33c63747e7b5ea71c650bc8050439b9b2ceb5d69ab4c1f934e70`.
- The first expanded full test run failed three stale count assertions that expected 18 scenarios, 54 attempts, and 18 model calls. All scenario behavior passed; only inventory assertions were corrected. The unchanged evaluator's frozen pre-change control then passed 60 trials under the old gates but emitted no condition metric or gate and reported stale checkpoint baseline-0005 against the baseline-0006 manifest.
- Implemented independent contract validity, condition/split counts, missing-pair reporting, condition split coverage, adversarial counts, missing adversarial splits, and adversarial split coverage. The report checkpoint now derives from the manifest; missing or unknown labels fail closed.
- Fourteen tests and a 60-trial implementation smoke pass. Agent, policy, service, API, MCP, action, approval, and executor hashes remain unchanged. The 21-file implementation manifest SHA-256 is `595b729c5ce780585499333bdb7ab80f7fd950df76e7b788a774b6e22ba0cbbc`.
- Immutable attempt 001 passed all condition, split, terminal, policy, security, utility, reliability, latency, and cost gates. Its 90 telemetry events contain no approval-token literal; report and trace SHA-256 are `b887c9549674217fb0e1812d4f7381b6cf9aa6fd6446fa32ee77ee8721c4ba93` and `2ac8be834ad9a14a59a7ae6f1b421dac64980f00b4e6c818b02eb8225e86d8ca`.
- Bumped package, API health, MCP server, CLI default, tests, README, dashboard, and real-surface verifier identities to `0.0.6` / baseline 0006. The dashboard adds evidence-condition split coverage as a visible metric without adding approval or execution controls.
- Refroze the versioned 21-file surface at SHA-256 `9f70f756ab93d4ba8732ed70455e0ce3c26f3cc84558baff24d8f56b7e101573`. Attempt 001 remains immutable and passing but is superseded for release selection; a new attempt is required before live verification.
- Immutable attempt 002 passed the exact versioned manifest and all 60 trials. It became the latest-passed pointer with report SHA-256 `45fd47dd788541f47ff04d9547206de1d01abf24c07501a0f17ffaba10323224`, trace SHA-256 `5329eb6cafcba980d840ba81ee989ec909c5b61a56fee218897e0e12bde3122a`, median end-to-end latency 60.221 ms, and p95 103.683 ms.
- A combined cleanup, CLI, and MCP shell command was rejected by local command policy before execution. Split direct calls passed: held-out CLI requested evidence without a proposal; MCP 2025-11-25 reported version 0.0.6, retained the full retrieval audit, excluded attack prose from the decision context, and exposed no approval or execution tool.
- Live API verification passed all 25 named checks, including selected evaluation and manifest identity, evidence-condition and adversarial split coverage, hash-bound approval, execution, exact postconditions, same-key idempotency, different-key HTTP 409 replay rejection, token redaction, CSP, and dashboard content.
- Independent runtime inspection passed required SQLite tables, one executed proposal, one consumed hash-only approval, one idempotency record, three ordered audit and trace events, evidence-only context, selected evaluation, manifest binding, screenshot dimensions, and forbidden-term absence.
- Visually inspected the 1440 by 1000 dashboard. It accurately shows baseline 0006, evaluation pass, evidence condition coverage 1.0, tool and terminal exactness 1.0, human approval, disconnected real infrastructure, and one mitigated synthetic incident.
- Docker Desktop 4.74.0 and Engine 29.4.3 remain live. Container packaging remains `defer`; the retained base-image source-gate failure still controls.
