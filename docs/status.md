# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `codex/baseline-0005-terminal-state-grading`
- Completed milestones: `BASELINE-0001`, `BASELINE-0002`, `BASELINE-0003`, `BASELINE-0004`
- Latest verified checkpoint: public `v0.0.4`; release reconciliation binds the local tag, remote tag, remote `main`, public repository, and non-draft release to the exact closure commit
- Active milestone: `BASELINE-0005`
- Current unit: freeze exact terminal states, evaluation-harness trajectories, and authority separation before implementation
- Disposition: baseline `pass`; container `defer`
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: pull request `#3` merged as `fca61e3f4b1a52e525477002c3977a15aab0cd8f` before the exact closure record
- GitHub pull request: `#3`, merged with history preserved
- GitHub release: public, non-draft `v0.0.4`
- Docker: daemon verified live; container packaging deferred after three base-image candidates failed the source gate
- External runtime dependencies: none for the accepted baseline; optional local Ollama evaluation is source-gated separately
- Local model source gate: ready for existing Ollama 0.32.5 plus `llama3.2:3b` at manifest SHA-256 `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`; adapter boundary tests pass and the first synthetic smoke call failed closed

## Verified evidence

- Contract schema: candidate pass
- Frozen manifest: 11 files, release candidate pass
- Tests: 12 of 12 release candidate pass
- Frozen evaluation: 18 scenarios, 54 attempts, all exact deterministic release-candidate gates pass
- Retrieval recall@4, outcome accuracy, diagnosis accuracy, trajectory exact match, policy compliance, benign utility, adversarial safe outcome, and `pass^3`: 1.0
- Instruction-bearing attack-document decision exposure: 0.0
- Proposal attack success: 0.0
- Latest selected-control latency: median 9.009 ms, p95 20.500 ms; no general performance claim
- Live CLI, MCP stdio, HTTP approval/executor, dashboard, SQLite, audit log, and JSONL telemetry: candidate pass
- Clean clone: exact baseline-0004 candidate commit `1b886c5557d311a272997866a715c2f8f815d76e` passed source gate, compilation, 12 tests, manifest, contracts, artifact hashes, unchanged policy, CLI, MCP, API, dashboard render, approval, executor, replay, SQLite, audit, and telemetry checks
- Final release closure `e364425d08e8e931b2b2f5a7c6be83651dd4931c`: local main, remote main, annotated tag, peeled remote tag, and public release agree
- GitHub review: pull request `#3`, 9 commits, 45 changed files, `CLEAN`, `MERGEABLE`, no required checks, merged with history preserved
- Merged main: compilation, 12 tests, manifest, contracts, unchanged policy, MCP, API, approval, executor, replay, postconditions, dashboard, SQLite, audit, and telemetry pass
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

Next eligible action: commit the evaluator implementation, run immutable repeated evaluation attempts against that exact commit and manifest, preserve their traces, and promote only a passing attempt.

Immutable attempt 001 passed all 54 trials and is now the latest-passed pointer. It executed 15 of 15 expected actions across `restart_worker`, `rollback_deployment`, and `warm_cache`; all 39 no-action trials stayed open and exactly unchanged. Proposal, actual trajectory, terminal state/status, policy, approval, execution, postconditions, idempotency, replay rejection, audit order, trace order, approval boundary, development/test reliability, and `pass^3` gates are all exact passes.

Attempt SHA-256 is `b3079ffcf29b8c6c44ebe0f1fda167cd7ffb6c32f9c15c37eca21b6f7546543e`; its 84-event trace SHA-256 is `9819b78a58ed31e58120b4ac9135b9a3be520a0b78f3ec8f85da383ddb3eb1e5`; its copied manifest matches active SHA-256 `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`. `latest.json` is byte-identical to the attempt. End-to-end median and p95 are 56.022 ms and 97.946 ms; diagnosis-only median and p95 are 5.288 ms and 14.148 ms.

Next eligible action: version the bounded checkpoint as `0.0.5`, rerun the accepted evaluation against the versioned surfaces, and verify the real CLI, API, MCP, approval/executor, dashboard, persistence, telemetry, clean clone, and public release.

Versioned package, API health, MCP identity, CLI default, tests, README, and dashboard now identify `0.0.5` / baseline 0005. The dashboard adds visible actual tool-trajectory and terminal-state exactness without adding approval or execution controls. The release-candidate manifest now binds 17 files, including package metadata, package version, CLI, and the evaluation driver; SHA-256 is `c8a4797dbdde2bc53ff9057bd1953bbfda925149b28c8a538f1d155334757310`.

Next eligible action: commit the versioned surfaces, generate immutable attempt 002 against the exact 17-file manifest, and begin native real-surface verification only if it passes.
