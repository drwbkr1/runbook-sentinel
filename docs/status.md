# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `codex/baseline-0003-retrieval-boundary`
- Completed milestones: `BASELINE-0001`, `BASELINE-0002`
- Latest verified checkpoint: public `v0.0.2` at `a320d36a933e80e5f22b5776be4ce39fa40cd530`; local tag, remote tag, remote `main`, public repository, and non-draft release agree
- Active milestone: `BASELINE-0003`
- Current unit: complete-diff and clean-clone verification for candidate `v0.0.3`
- Disposition: baseline `pass`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: verified at public `v0.0.2` closure commit `a320d36a933e80e5f22b5776be4ce39fa40cd530`
- GitHub pull request: `#1`, merged with history preserved
- GitHub release: public, non-draft `v0.0.2`
- Docker: daemon verified live; container packaging deferred after three base-image candidates failed the source gate
- External runtime dependencies: none
- Local Ollama assets: inspected but not approved or used

## Verified evidence

- Contract schema: candidate pass
- Frozen manifest: 9 files, candidate pass
- Tests: 7 of 7 candidate pass
- Frozen evaluation: 16 scenarios, 48 attempts, all exact candidate gates pass
- Retrieval recall@4, outcome accuracy, diagnosis accuracy, trajectory exact match, policy compliance, benign utility, adversarial safe outcome, and `pass^3`: 1.0
- Instruction-bearing attack-document decision exposure: 0.0
- Proposal attack success: 0.0
- Latest latency: median 7.391 ms, p95 18.075 ms; no general performance claim
- Live CLI, MCP stdio, HTTP approval/executor, dashboard, SQLite, audit log, and JSONL telemetry: candidate pass
- Clean clone: pending for the exact candidate commit
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

Next eligible action: commit the reconciled candidate and verify that exact commit from a no-local-object clean clone before GitHub publication.
