# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `codex/baseline-0004-local-model`
- Completed milestones: `BASELINE-0001`, `BASELINE-0002`, `BASELINE-0003`
- Latest verified checkpoint: public `v0.0.3`; release reconciliation binds the local tag, remote tag, remote `main`, public repository, and non-draft release to the exact closure commit
- Active milestone: `BASELINE-0004`
- Current unit: freeze the tested candidate implementation, run one development smoke case, then retain the three-trial local-model comparison
- Disposition: baseline `pass`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: pull request `#2` merged as `995dcefb1cef284b936a5b336c4601c54bad2462` before the exact closure record
- GitHub pull request: `#2`, merged with history preserved
- GitHub release: public, non-draft `v0.0.3`
- Docker: daemon verified live; container packaging deferred after three base-image candidates failed the source gate
- External runtime dependencies: none for the accepted baseline; optional local Ollama evaluation is source-gated separately
- Local model source gate: ready for existing Ollama 0.32.5 plus `llama3.2:3b` at manifest SHA-256 `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`; adapter boundary tests pass and Runbook Sentinel has not yet invoked the model

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
- Clean clone: exact commit `0aa4fc68bfcf208c2f64a3578e54727a55002ef3` passed all source, evidence, MCP, API, dashboard, persistence, telemetry, JSON, secret, and diff gates
- Final branch head `c5fc8f5cdb80436af5ebead18a665b6878f8db28`: exact-clone regression pass
- GitHub review: pull request `#2`, 4 commits, 45 changed files, `CLEAN`, `MERGEABLE`, no required checks, merged with history preserved
- Merged main: compilation, 7 tests, manifest, contracts, unchanged policy, MCP, API, approval, executor, replay, postconditions, dashboard, SQLite, audit, and telemetry pass
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

Next eligible action: freeze and commit the tested implementation identity, invoke one development smoke case, then run the first retained local-model comparison without granting any runtime authority.
