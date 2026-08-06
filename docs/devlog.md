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
