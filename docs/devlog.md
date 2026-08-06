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
