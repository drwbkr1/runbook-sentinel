# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `main` (unborn pending the first verified commit)
- Active milestone: `BASELINE-0001`
- Latest verified checkpoint: none; `baseline-0001` is a passed native candidate pending commit and clean-clone verification
- Current unit: `UNIT-005` commit and clean-clone verification
- Disposition: native candidate `pass`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub visibility: unresolved human access decision; no remote created
- Docker: daemon verified live; container packaging deferred after three base-image candidates failed the source gate
- External runtime dependencies: none
- Local Ollama assets: inspected but not approved or used

## Candidate evidence

- Contract schema: pass
- Frozen manifest: 9 files, pass
- Tests: 6 of 6 pass
- Frozen evaluation: 9 scenarios, 27 attempts, all exact gates pass
- Retrieval recall@4, outcome accuracy, diagnosis accuracy, trajectory exact match, policy compliance, benign utility, adversarial safe outcome, and `pass^3`: 1.0
- Proposal attack success: 0.0
- Latest latency: median 21.411 ms, p95 39.202 ms
- Live CLI, MCP stdio, HTTP approval/executor, dashboard, SQLite, audit log, and JSONL telemetry: pass
- Container: deferred after three base images failed the source gate

Next eligible action: inspect the complete diff, create the local baseline commit, and verify a clean clone. GitHub publication remains gated on visibility.
