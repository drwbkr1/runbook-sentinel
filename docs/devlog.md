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
