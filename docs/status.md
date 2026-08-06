# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `main`
- Completed milestone: `BASELINE-0001`
- Latest verified checkpoint: `baseline-0001`; code, closure, and public release-record commits passed native and clean-clone verification
- Current unit: publish and verify the `v0.0.1` research-preview tag before `BASELINE-0002`
- Disposition: baseline `pass`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: live at verified closure commit `061f0aefa0a4c61e0ed14d589e2d3bcee5ec413e` before this reconciliation record
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

Next eligible action: push this verified release record, tag and verify `v0.0.1`, then begin `BASELINE-0002` from `baseline-0001`. Its first measured target is the limited nine-case synthetic scenario and fault corpus.
