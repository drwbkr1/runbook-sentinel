# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `main`
- Completed milestones: `BASELINE-0001`, `BASELINE-0002`
- Latest verified checkpoint: `baseline-0002`; merged code and evidence commit `53fc4ce1189218fc0ea13899aa8bb83552ffa4af` passed local, clean-clone, remote, and merged-main verification
- Active milestone: none; the next cycle must resume from `v0.0.2`
- Current unit: none
- Disposition: baseline `pass`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: merged and verified at `53fc4ce1189218fc0ea13899aa8bb83552ffa4af` before this closure record
- GitHub pull request: `#1`, merged with history preserved
- GitHub release: public, non-draft `v0.0.2`
- Docker: daemon verified live; container packaging deferred after three base-image candidates failed the source gate
- External runtime dependencies: none
- Local Ollama assets: inspected but not approved or used

## Verified evidence

- Contract schema: pass
- Frozen manifest: 9 files, pass
- Tests: 6 of 6 pass
- Frozen evaluation: 9 scenarios, 27 attempts, all exact gates pass
- Retrieval recall@4, outcome accuracy, diagnosis accuracy, trajectory exact match, policy compliance, benign utility, adversarial safe outcome, and `pass^3`: 1.0
- Proposal attack success: 0.0
- Latest latency: median 21.411 ms, p95 39.202 ms
- Live CLI, MCP stdio, HTTP approval/executor, dashboard, SQLite, audit log, and JSONL telemetry: pass
- Clean clone: compilation, tests, manifest, contract, MCP, live API, dashboard render, persistence, and telemetry all pass
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

Next eligible action: begin `BASELINE-0003` from `v0.0.2` by measuring retrieval attack exposure and comparing only source-approved retrieval configurations on frozen splits.
