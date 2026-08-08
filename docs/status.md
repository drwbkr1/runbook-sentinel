# Current status

- Project: Runbook Sentinel
- Authoritative repository: `C:\Projects\Active\runbook-sentinel`
- Branch: `codex/baseline-0017-live-trace-anchor`
- Completed milestones: `BASELINE-0001` through `BASELINE-0010` and `BASELINE-0012` through `BASELINE-0016`; `BASELINE-0011` is stopped and unpublished with its failed evidence retained
- Latest verified checkpoint: public `v0.0.16`; release reconciliation binds the annotated tag, peeled remote tag, remote `main`, public repository, non-draft release, selected zipapp and checksum assets, downloaded public bytes, rendered public pages, and fresh public-tag clone to the release-closure commit
- Candidate version: `v0.0.17`; selected source/package evidence is manifest-bound and locally verified but not yet clean-clone or release verified
- Active milestone: `BASELINE-0017` - durable endpoint anchoring for live API, MCP, and direct CLI traces
- Current unit: `UNIT-004` in progress - all ten frozen cases, source/package gates, real CLI/API/MCP endpoint anchors, persisted state, telemetry, and visually inspected dashboards pass; clean-clone verification remains
- Disposition: baseline-0016 `pass`; baseline-0015 `pass`; baseline-0014 `pass`; baseline-0013 `pass`; baseline-0012 `pass`; v0.0.11 `stop` and unpublished
- GitHub target owner: `drwbkr1`
- GitHub repository: `https://github.com/drwbkr1/runbook-sentinel`
- GitHub visibility: public, explicitly selected by the user on 2026-08-06
- GitHub `main`: verified baseline-0016 release closure
- GitHub pull request: `#14`, merged with history preserved under expected-head lock `be13f5bb0c56f19623ef7e7c00165460f18c5b3c`
- GitHub release: public, non-draft `v0.0.16` with verified `.pyz` and `.sha256` assets
- Docker: client 29.4.3 is installed but the daemon is currently off; container packaging remains deferred after three base-image candidates failed the source gate
- External runtime dependencies: none for the accepted baseline; optional local Ollama evaluation is source-gated separately
- Local model source gate: ready for existing Ollama 0.32.5 plus `llama3.2:3b` at manifest SHA-256 `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`; adapter boundary tests pass and the first synthetic smoke call failed closed

## Verified evidence

### BASELINE-0017 live-trace endpoint-anchor gap and frozen contract

- Public v0.0.16 is the exact starting checkpoint: annotated and peeled tag, remote `main`, non-draft release, selected 358,711-byte archive and checksum, anonymous downloads, release page, commit-bound rendered README, raw main/tag, and a fresh no-alternates public-tag clone reconcile at `465f4e299578e822b38aae7a90835238c4c9c3b8`.
- A fresh downloaded-package evaluation and fresh public-tag source/package evaluations pass `84+9+6+10+10`, exact 150-event report anchors, 28 tests, exact archive rebuild, MCP, API, state, audit, telemetry, parsing, scan, and visual gates.
- Completed evaluation traces are externally anchored by their reports, but live API and MCP traces persist only the self-contained chain. The fresh public-tag live API trace is a valid five-event chain and has no durable endpoint-anchor file.
- A non-destructive probe used the downloaded public package's canonical event builder in memory. A six-event full chain and its five-event suffix-truncated form both verify unanchored; supplying the full endpoint makes the truncated form fail exact event-count and final-digest checks. No released or runtime evidence byte changed.
- The smallest bounded improvement is a sibling `trace-anchor/v1` endpoint for live traces: trace bytes flush and fsync first, a securely created same-directory temporary anchor flushes and fsyncs, then `os.replace` updates the endpoint. Missing, orphaned, stale, malformed, wrong-file, truncation, or extra-suffix states must fail before resume.
- Official Python 3.12.13 `os` and `tempfile` documentation passes all eight source criteria for narrow citation and project-authored standard-library use. No external code, sample, data, package, executable, model, service, key, credential, or trace is imported.
- `live-trace-anchor-v1` freezes four development and six held-out cases before candidate implementation. The contract validator passes with no candidate results; the controlled milestone reports inherited authority and `UNIT-003` as the only authorized ready unit.
- The design explicitly does not claim writer authentication, hostile-writer resistance, immutable storage, non-repudiation, digital signatures, directory-entry durability, or RFC conformance. A same-authority attacker can still recompute both an unkeyed chain and sibling anchor.
- The generic implementation adds canonical anchor serialization and verification, durable trace-before-anchor write ordering, fail-closed resume, explicit sibling-path enforcement, and live CLI/API/MCP wiring. Its sealed implementation commit is `7b30740`; the sealed evaluator commit is `80c0a53`.
- The first immutable full reveal passes all ten cases exactly. Both splits, invalid-state no-append, truncation detection, and valid restart/resume are 1.0; the retained 10,147-byte result SHA-256 is `449e93aef8c9b27cfc2429576a5f86c0aa6ec2664439fcaca54cdef942c4eb96`.
- Selected source and package attempts pass 33 tests and `84+9+6+10+10+10` under 62-file manifest SHA-256 `069c397348497ca109d549c897205061f4ff7f4144a5cc2d57b555f3f191863c`. Completed-evaluation companion traces each contain 150 exact events.
- Two independently built 392,893-byte, 32-entry zipapps are byte-identical at SHA-256 `4c14dfd4efe87929c9f7de40b00d23b78d25570f0b6a754fa5e35d33d23e6880`. Source and package MCP expose exactly three diagnostic/read tools; real API approval, execution, replay, state, audit, live anchor, and dashboard checks pass.
- Visual inspection rejected the first otherwise-passing dashboard candidate because its incident table fell below the 1440 by 1000 frame. The archive and source/package visual/native receipts remain retained as superseded attempt 001. The corrected source and package dashboards visibly include the live-endpoint metric and persisted mitigated incident.
- Next eligible action: seal the selected candidate, run a no-local-object clean clone, then perform release audit and GitHub review only if every gate remains exact.

### BASELINE-0015 approval-authority gap

- The approved project-specific `Sentinel-Capability` boundary is implemented. Approval authentication precedes JSON parsing; missing, wrong, malformed, Bearer, duplicate, and prior-launch material returns uniform HTTP 401; a caller-provided `actor` returns HTTP 400; valid requests derive a launch-scoped `operator-[0-9a-f]{16}` identity server-side.
- The agent, model, and MCP still receive no approval material or execution authority. The raw per-launch capability is absent from process arguments, environment, repository, package, database, audit, traces, logs, evaluation records, and dashboard. The rendered label is `authenticated external operator`, not proof of human presence.
- `operator-authentication-v1` passes all ten development and held-out cases. Authentication denial, authorized utility, denied no-mutation, server-derived identity, capability exclusion, prior-launch rejection, and both splits are 1.0 with zero model calls or external cost.
- Frozen source attempt 002 and package attempt 002 pass all 84 repeated scenarios plus 9 approval-lifetime, 6 idempotency-authorization, and 10 operator-authentication cases under 51-file manifest SHA-256 `72a180546c6ddbd4ee36fb61b2d49406d0c0666821b7a368b5c73cd4f858225c`.
- Two 326,418-byte, 28-entry dependency-free zipapps are byte-identical at SHA-256 `0e4d12cd449c8e198ec9434fd12ba3bffc10b8baa609f18c6f71d0d4200da4df`. Source and package MCP, real API/approval/executor/state/telemetry/log checks, and visually inspected 1440 by 1000 dashboards pass.
- A public-branch clone of exact commit `fcae2740f968db0ef7f35936feebb30cb156e5a5` started clean with no Git alternates, repeated the full gate, rebuilt the exact selected archive, and passed the package MCP and real surfaces. `artifacts/verification/clean-clone-baseline-0015.json` retains the receipt.
- Retained unfavorable and superseded evidence includes the initial manifest-bound evaluation failure, a direct package import-path failure, an over-strict parity comparison, a Windows PowerShell response-body extraction failure, and the first immutable archive/evaluation attempts. No failed result was rewritten.
- PR `#13` merged under the exact expected-head lock as `824ad5468d420c29d8d0416b15c011fcb531d8e4`, with parents exact prior release closure and reviewed head. A fresh no-alternates public-main clone passes 24 tests, source/package 84+9+6+10, the exact selected archive rebuild, package MCP/API/state/telemetry/logs, evidence parsing, secret/model exclusion, and visual inspection.
- The annotated `v0.0.15` tag, peeled remote tag, remote `main`, non-draft GitHub release, 326,418-byte zipapp, adjacent checksum, downloaded public bytes, rendered README and release page, and fresh public-tag clone reconcile to the release-closure commit.
- This checkpoint has been superseded as the active work target by the bounded baseline-0016 candidate; v0.0.15 remains the latest verified public release until publication completes.

### BASELINE-0016 trace-integrity gap and frozen contract

- A fresh downloaded public v0.0.15 archive at the selected SHA-256 passes the full 84+9+6+10 gate. Its 150-event JSONL trace has no event sequence, previous-event digest, event digest, completed-evaluation trace binding, or telemetry-integrity metric.
- A non-destructive in-memory probe changed the first `sentinel.execute` event from `postconditions=true` to `postconditions=false`. The altered stream still parses, retains the expected event names, passes every current trace-content check, and leaves the completed evaluation disposition at `pass`. The released file was not changed.
- `trace-integrity-v1` freezes ten ordered development and held-out cases before candidate implementation. It covers valid anchored and unanchored chains, content mutation, sequence gaps, anchored tail truncation, reordering, previous-hash mutation, interior deletion, malformed JSON, and exact append resume.
- The bounded candidate may add only deterministic SHA-256 sequence continuity, fail-closed existing-prefix validation, and exact completed-evaluation event-count/final-digest binding. It adds no key, secret, dependency, signer, collector, or real-infrastructure connection and makes no origin-authentication, hostile-writer, immutable-storage, digital-signature, or RFC 5848 conformance claim.
- The official-source gate validates `ready` for narrow citation and a project-authored standard-library implementation. The milestone and ten-case contract validators pass with no held-out candidate result reveal.
- Development-only checks passed before the sealed implementation commit. The first held-out reveal then passed all ten frozen cases exactly, including all seven corruption classes and valid-prefix resume.
- The 57-file manifest is SHA-256 `b1487c7fe1f017181f007da592a8091f3543e4cff42bcf17e87e7b33a1a5d354`. Source and package attempts pass all 84 repeated scenarios plus 9 approval-lifetime, 6 idempotency-authorization, 10 operator-authentication, and 10 trace-integrity cases.
- Independent report-to-trace verification binds each selected evaluation to its exact 150-event companion trace. Source and packaged real API, approval, executor, state, audit, live-chain, MCP, and rendered dashboard checks pass.
- Two 358,711-byte, 30-entry dependency-free zipapps are byte-identical at SHA-256 `9c04e2815f4bb536904a803f8bf64079342eab4f694039ea8c61105453b8344f`. Visual inspection confirms Baseline 0016, trace integrity 1.0, authenticated external operator, and disconnected real infrastructure.
- A no-local-object clone of exact candidate commit `8c088c2cbe68e7bdb30363cf094cb6e37025067c` started clean with no Git alternates. It passed the source gate, reproduced exact selected archive SHA-256 `9c04e2815f4bb536904a803f8bf64079342eab4f694039ea8c61105453b8344f`, and passed packaged evaluation, MCP, API, state, audit, chain, anchor, parsing, scan, and original-detail visual inspection.
- The first clone wrapper timed out after its immutable source evaluation completed; independent verification proved the report and 150-event anchor pass. The unchanged result remains retained. A first all-dark image preview was likewise retained before exact-resolution inspection displayed the correct dashboard.
- PR `#14` reviewed exact head `be13f5bb0c56f19623ef7e7c00165460f18c5b3c` and merged it under expected-head lock as `848a7ae1c3dd8dfec6d40bbfe5196263e99cb90e`, with exact parents `da66c5b8306c37a04b6d37d66b283f5ff2fd21d4` and `be13f5bb0c56f19623ef7e7c00165460f18c5b3c`.
- A fresh public-main clone has no object alternates and began clean. Twelve validators, 28 tests, fresh anchored source and package `84+9+6+10+10` evaluations, exact selected-archive rebuild, three-tool MCP, all 86 API checks, all 49 persisted-state/audit/telemetry checks, 266 JSON parses, 65 JSONL parses with 7,492 records, model/credential exclusion, and original-detail dashboard inspection pass.
- The fresh public-main scan found one stale README claim that the current builder used 28 entries; the frozen package contract and exact archive contain 30. The release-closure branch corrects that documentation-only discrepancy before the final audit.
- Final pre-publication audit `artifacts/verification/release-audit-baseline-0016.json` independently computes `verified` with no errors, warnings, failed required checks, missing surfaces, or stale surfaces.
- The annotated `v0.0.16` tag, peeled remote tag, remote `main`, non-draft GitHub release, 358,711-byte zipapp, adjacent checksum, downloaded public bytes, rendered README and release page, and fresh public-tag clone reconcile to the release-closure commit.
- Next eligible action: begin the next cycle from verified public v0.0.16 by running the system and inspecting traces and separate evaluation results before selecting one bounded improvement.

- Fresh public v0.0.14 reconciliation passes: remote main, annotated tag, downloaded assets, a no-alternates public-tag clone, nine validators, 22 tests, exact archive rebuild, source/package 84+9+6 evaluations, both real MCP/API/state/telemetry surfaces, and rendered dashboard inspection agree.
- The current 150-event evaluation trace uses only the fixed caller-supplied actor `frozen-evaluation-harness`. The evaluation has no approver identity-authentication, approver authorization, or separation-of-duties metric.
- A real loopback probe against the downloaded public zipapp submitted `actor: sentinel-agent-self-declared` in the unauthenticated approval JSON body. Approval returned HTTP 201 with a token, execution returned HTTP 200, `restart_worker` changed the synthetic incident from unhealthy/restart count 0 to healthy/restart count 1, and postconditions passed.
- SQLite, audit, and trace evidence preserves that self-declared actor and the consumed approval across all three probes. The first two product flows executed but their diagnostic reporters failed on incorrect response-shape assumptions; those failures remain retained with the complete third result in `artifacts/verification/approval-authority-gap-baseline-0015.json`.
- This does not expose real infrastructure, put a credential in the model, or add an MCP approval tool. It does show that the public dashboard's `human approval` label is not backed by authenticated identity: any local HTTP caller can self-declare the approver and mint an execution-authorizing token.
- The smallest enforcement options required a new local operator credential or OS-authenticated access boundary, which crossed the standing secret/access gate. The user selected the per-launch capability; label correction alone was not used as the security control.
- Current official-source review rejects direct Bearer/OAuth use on this surface: RFC 6750 requires TLS, while Runbook Sentinel uses bare loopback HTTP, and OAuth would add roles and flows without a matching product need. RFC 9110 is fit only for generic HTTP authentication semantics. Python 3.12 standard-library primitives implement the selected per-launch capability without a new dependency.
- The user approved the recommended option verbatim: `yes, implement the recommended option`. The closed human-review workflow locked and reconciled one `approve-per-launch-operator-capability` decision, no alternative decision, and no fabricated response. `operator-authentication-v1` now freezes ten ordered development and held-out cases before runtime implementation.

### BASELINE-0014 cached-result authorization gap and frozen contract

- A fresh run of the downloaded public v0.0.13 zipapp passes all 28 scenarios and 84 attempts. Its 150-event trace contains 84 run, 33 approval, and 33 execution events; every approval actor is the evaluation harness, and no separate cached-result authorization metric exists.
- A real loopback HTTP probe executed one proposal with a valid approval, then retried the same proposal and idempotency key with a wrong token and with no token. Both unauthorized retries returned HTTP 200 and the exact cached successful result. SQLite, audit, and trace inspection prove there was no second executor or state mutation.
- The gap is bounded to cached-result disclosure and response truth. Direct execution still requires a valid unconsumed, unexpired, action-bound approval, and the model, agent, MCP tools, capabilities, executor, postconditions, credentials, and real-infrastructure boundaries remain unchanged.
- `eval/idempotency-authorization-contract.json` freezes six cases before implementation: three revealed development cases and three held-out test cases. It requires a hash-matching consumed approval before same-proposal cache disclosure, permits the original completed retry even after token expiry, preserves different-key replay rejection, and requires byte-exact state, audit, and trace stability on every retry.
- The first isolated candidate reveal passes all six cases. Authorized cache utility, unauthorized denial, retry no-mutation, new-key replay rejection, development exactness, and test exactness are 1.0. The 10,782-byte immutable result SHA-256 is `90ec001f063d97755014d32c84832687c67b5a3130aca89e57b3c427a26d3306` and contains no raw approval-token field.
- The integrated evaluator schema is 2.1 and reports idempotency authorization separately from the 84 repeated scenarios and nine approval-lifetime cases. All 22 tests pass.
- Candidate identity is now `0.0.14` / `baseline-0014`. The package contract froze before any archive build with 25 exact entries and SHA-256 `b6d6544e9bf98d1c8201b0970daeb6b5775c8fc92cd6d62f0ef58e3101d29b47`; the 45-file evaluation manifest passes at SHA-256 `aae568de2095570d6d142bdf9e17828cb77c51e7ced9efef46d82836349cca10`.
- Version-bound source attempt 001 passes all 84 scenario attempts plus the nine lifetime and six cache-authorization cases. Its report and trace SHA-256 values are `098be4dab2aff8585f9f252de356492ec82b5f6f2d2de881a2b202a8b196164f` and `a29e6d98d0880ba11857e9e54f485345831b72caaac44ecbb9ace601bc13f6f0`.
- Two independent 283,148-byte, 25-entry zipapps are byte-identical at SHA-256 `9c9dbcba3b44fe0abb5ef83ac64d413112a64438d8776320f037493db55a3e6f`. The archive contract, CLI, packaged 84+9+6 evaluation, bounded MCP, 66 HTTP/dashboard checks, 35 persisted-state/telemetry checks, and rendered dashboard inspection pass.
- Source and package non-latency results are exact after removing only declared latency and per-run state/trace fingerprint fields. Both dashboards visibly report Baseline 0014, cached result authorization 1.0, approval lifetime 1.0, human approval, disconnected real infrastructure, and persisted synthetic incidents.
- A no-local-object clone of exact commit `aa0c70b54962594b4c14d2fd5bae390a7c22c0f1` has no alternates and initially had a clean worktree. It passes compilation, nine validators, 22 tests, fresh source and package 84+9+6 evaluations, two exact archive rebuilds, source and package MCP, 66 HTTP/dashboard checks per runtime, 35 persisted-state checks per runtime, model/secret exclusion, and visual package-dashboard inspection.
- Final reviewed head `6a1e166046311f9944fead99cc25e67293fe00c6` contained seven expected commits and 51 exact changed paths. PR `#12` merged it under the expected-head lock with history preserved as `da084e469534d0a952375a1852b20818480adfd1`, whose parents are exact prior release closure `18c7bf30c65954713164214cc5823e4394166886` and reviewed head.
- A fresh public-main clone of the merge has no object alternates and began clean. Nine validators, all 22 tests, fresh source and package 84+9+6 evaluations, exact selected-archive rebuild, both MCP surfaces, 66 HTTP/dashboard checks and 35 state/telemetry checks per runtime, parsing of 220 JSON and 55 JSONL files with 6,285 records, model/secret exclusion, protected-boundary comparison, and rendered dashboard inspection pass.
- Final pre-publication audit `artifacts/verification/release-audit-baseline-0014.json` reports `verified` and authorizes the exact release-closure commit, annotated tag, two selected public assets, and immediate public verification.
- The annotated public `v0.0.14` tag, peeled remote tag, remote `main`, non-draft GitHub release, 283,148-byte `.pyz`, adjacent checksum, downloaded public bytes, rendered README and release page, and fresh public-tag clone reconcile to the release-closure commit.
- RFC 9110 passed the external-source gate for narrow HTTP terminology and a clearly labeled project inference only. The expired and archived IETF Idempotency-Key Internet-Draft is retained as blocked and excluded from normative or design use. No external code, data, model, package, executable, or service was imported.
- Next eligible action: begin the next cycle from verified public v0.0.14 by running the system and inspecting its traces and separate evaluation results before selecting one bounded improvement.

### BASELINE-0013 approval-lifetime gap and frozen contract

- Fresh orientation ran the downloaded public v0.0.12 zipapp from `C:\Projects\Verification`, not the development tree. All 28 scenarios and 84 attempts still pass; policy and `pass^3` are 1.0, proposal and terminal attack success are 0.0, and model calls and estimated cost remain zero.
- The fresh report and trace SHA-256 values are `b2b969a9bfb648290f6aecdea7440c820d290fae5f2faa6ba3a68acdabc381ef` and `026fcdf6d81bdc151af952574e202f07ecfd29bd7964e4001dc5798123c04e03`. The trace contains 84 run, 33 approval, and 33 execute events, but no invalid approval-lifetime case.
- A real loopback HTTP probe against the released zipapp submitted `ttl_seconds: -1`. Approval returned HTTP 201 and changed the proposal to approved even though the returned token was already expired; execution then returned HTTP 409, a recovery approval returned HTTP 409 because the proposal was no longer pending, and the incident remained open. The exact released failure remains retained outside the repository and summarized in `artifacts/verification/approval-lifetime-gap-baseline-0013.json`.
- The frozen `eval/approval-lifetime-contract.json` defines a JSON integer, excluding booleans, with an inclusive range of 1 through 300 seconds and a default of 300. Invalid input must return HTTP 400 before proposal, approval, audit, trace, or incident mutation.
- Nine exact development and held-out cases cover negative, zero, above-maximum, fractional, string, boolean, minimum, maximum, and omitted lifetimes. Only the known negative-TTL development failure was revealed before implementation; candidate results for the six held-out cases remain unrevealed.
- The improvement is bounded to approval-lifetime validation and its independent evaluation. Agent outcomes, retrieval, proposal schema, capabilities, executor actions, idempotency, replay, preconditions, postconditions, scenarios, and disconnected real-infrastructure boundary remain unchanged.
- The first and only frozen candidate reveal passes all nine isolated real loopback HTTP, SQLite, audit, and JSONL trace cases. Invalid no-mutation, valid-lifetime exactness, and both split exact-match rates are 1.0; no approval token value is retained in the result.
- The integrated schema 2.0 evaluator reports approval lifetime separately from the unchanged 84 scenario attempts. After two retained verifier false positives on a field-name substring, all 21 tests and the independent contract validator pass.
- Version-bound attempt 001 passed but its subsequent live verifier failed on PowerShell error-body parsing. The exact failure remains retained. Corrected manifest attempt 002 at SHA-256 `249513aca8911a1a574a48e2546458db0b3d1e37ecdd4416db40cbb8638bc4c9` passes eight validators, 21 tests, all 84 scenario attempts, and all nine lifetime cases.
- Source and package MCP expose the same three diagnostic/read tools with no approval or execution tool. Source and package HTTP/dashboard each pass 58 checks; their SQLite, audit, trace, evaluation, manifest, and screenshot receipts each pass 31 checks.
- Two independent 257,847-byte, 23-entry, dependency-free zipapps are byte-identical at SHA-256 `c14a4559f3cfc4f53d5ce501115747252c9f33e7f299eb34f088c605930fbd41`. Source and package evaluation results are exact after excluding declared latency fields.
- Source and packaged dashboards were visually inspected at 1440 by 1000. Both visibly report Baseline 0013, evaluation pass, approval lifetime exact 1.0, human approval, disconnected real infrastructure, and persisted synthetic incidents.
- A public-branch clone of exact commit `2f50f5e8d2098d593fea1d5fefa2ca846422fe9f` has no object alternates and initially has a clean worktree. It passes compilation, eight validators, 21 tests, fresh 84+9 source evaluation, exact selected-archive rebuild, fresh packaged 84+9 evaluation, packaged MCP, 58 HTTP/dashboard checks, 31 runtime checks, and visual inspection.
- Final reviewed head `5c4a358a3f85c21ccb27c19efcb791e5b06be283` contained six expected commits and 50 expected paths, then PR `#11` merged with history preserved as `54c56411ea0ff3e1b17743fcbd8ebc225dabaabb` with exact parents.
- A no-alternates public-main clone of the merge commit passes compilation, eight validators, 21 tests, 202 tracked JSON files, 53 JSONL files with 5,985 records, model/secret exclusion, source and package 84+9 evaluations, exact selected-archive rebuild, packaged MCP, 58 HTTP/dashboard checks, 31 runtime checks, persistence, telemetry, and visual dashboard inspection.
- The merged-main dashboard visibly reports Baseline 0013, approval lifetime exact 1.0, human approval, disconnected real infrastructure, and a mitigated persisted synthetic incident. The receipt is `artifacts/verification/merged-main-baseline-0013.json`.
- The final pre-publication audit computes `verified` and releases only the inherited release-closure, annotated-tag, selected-asset publication, and immediate public-verification actions.
- Public release reconciliation verifies the annotated `v0.0.13` tag, peeled remote tag, remote `main`, non-draft GitHub release, selected 257,847-byte zipapp at SHA-256 `c14a4559f3cfc4f53d5ce501115747252c9f33e7f299eb34f088c605930fbd41`, adjacent checksum, downloaded public bytes, rendered README and release page, and fresh public-tag clone against the release-closure commit.

### BASELINE-0012 package release-candidate evidence

- Public v0.0.10 remains the latest verified checkpoint. BASELINE-0011 and v0.0.11 are stopped and unpublished after the first packaged real-surface reveal rendered `Baseline 0010` while health and evaluation reported baseline-0011; the candidate, screenshot, and 49-of-50 result remain retained.
- Frozen baseline-0012 contracts classify the stale dashboard label as a known regression rather than held-out evidence and require a new v0.0.12 candidate, exact package contents and metadata, source/package parity, clean-clone rebuild identity, and public-download checksum identity.
- The pre-merge release audit caught impossible future-dated project-authored provenance metadata. The earlier functionally passing archive, evaluation, and clean-clone receipt remain retained with disposition `superseded`; they were not promoted, merged, tagged, or released.
- Two corrected independent 239,183-byte archives are byte-identical at SHA-256 `679f7ad301689bee62a5bcb33df8c4778f9f0307135cf30632b13408e2f31083`; each has exactly 21 allowlisted entries, fixed metadata, no cache, bytecode, runtime state, dependency, or secret, and exact package/evaluation manifest bindings.
- Corrected source validation passes a 35-file frozen manifest, seven validators, 19 tests, and all 84 evaluation attempts. The corrected package evaluation passes all 84 attempts and matches every source gate and non-latency metric family under manifest SHA-256 `63a02909d62c0bb6f156d6700df7b2b9453a7b9e7385e9bf524243c184ccd028`.
- Retrieval, generation, proposal, tool trajectory, terminal state, policy, utility, attack success, repeated reliability, latency, cost, behavioral relations, guidance stress, stale-evidence stress, and stale-payload projection remain separately reported. Policy and `pass^3` are 1.0; proposal and terminal attack success are 0.0; model calls and estimated cost are zero.
- Packaged MCP reports v0.0.12, exposes three diagnostic/read tools and no approval or execution tool, retains the full retrieval audit, excludes the attack document from decisions, and exposes zero stale payload characters.
- Packaged HTTP/dashboard passes all 51 checks, including approval hashing, execution, replay rejection, postconditions, redaction, CSP, baseline-0012 health/evaluation/rendered identity, and absence of stale baseline labels. SQLite, audit, trace, manifest binding, and telemetry pass all 27 checks.
- The corrected 1440 by 1000 dashboard was visually inspected. It visibly reports Baseline 0012, evaluation pass, deterministic v2, decision-context v3, retrieval v3, exact metrics, human approval, disconnected real infrastructure, and one mitigated synthetic incident; PNG SHA-256 `a714e4e3da6745501d07eded0617124ec6e75c479f0d64e948b1be3210ec67fa`.
- Official Python 3.12.13 packaging documentation passed the source gate for citation and project-authored standard-library implementation only. No external code, package, sample, data, model, executable, or service was imported.
- The earlier no-local-object clone of exact candidate `329767a6995aa261509d44e806729f94d166f180` remains retained as functionally passing but superseded. A renewed no-local-object clone of corrected commit `59bb7d7763ad3f132d443a79359a05fd60648c44` has no object alternates, independently reproduces SHA-256 `679f7ad301689bee62a5bcb33df8c4778f9f0307135cf30632b13408e2f31083` twice, and passes compilation, 19 tests, seven validators, 12 milestone contracts, 183 tracked JSON files, 50 JSONL files with 5,535 records, source/package 84-attempt evaluations, packaged MCP, 51 API checks, 27 runtime checks, secret/model exclusion, and visual inspection.
- The final reviewed PR head `12e2c71897a3965fc0d64c1f718e8f110cc4f7e1` contained 11 expected commits and 63 exact changed paths, then merged with history preserved as `e4dcde1227d0f235f8725df3e15f91ad5675e7ab` with exact prior-main and reviewed-head parents.
- A fresh public-main clone of the merge commit passed compilation, 19 tests, seven validators, both package contracts, the source gate, 12 milestone contracts, 185 tracked JSON files, 50 JSONL files with 5,535 records, model/secret exclusion, exact repeated archive rebuild, source/package 84-attempt evaluations, packaged MCP, 51 API checks, 27 runtime checks, persistence, telemetry, and visual dashboard inspection.
- The final pre-publication audit computes `verified` and releases only the inherited release-closure, annotated-tag, public-release, asset, and immediate public-verification actions.
- Public release reconciliation verifies the annotated `v0.0.12` tag, peeled remote tag, remote `main`, non-draft GitHub release, selected 239,183-byte zipapp at SHA-256 `679f7ad301689bee62a5bcb33df8c4778f9f0307135cf30632b13408e2f31083`, adjacent checksum, downloaded public bytes, rendered README and release page, and fresh public-tag clone against the release-closure commit.

### BASELINE-0010 release-candidate evidence

- Fresh public-v0.0.9 orientation: all 84 trials pass; the report and trace are retained outside the repository under `C:\Projects\Verification`.
- Measured weakness: the released decision context forwards 27 stale project records across 15 of 84 attempts, exposing 2,913 stale title/content characters even though the agent uses no stale record for facts.
- Research gate: CaMeL and StruQ pass all 16 criteria for citation and narrow paraphrase; no external code, data, paper, model, dependency, executable, or service was imported.
- Frozen schema 1.9: 28 scenarios; one development and one sealed held-out projection case; exact stale fields `id`, `kind`, and `observed_at`; forbidden stale fields `title` and `content`; unchanged fresh payload and behavior.
- Pre-change v2: stale identity retention 1.0, stale metadata projection 0.0, stale payload exposure 1.0, fresh payload retention 1.0, and exact behavior 1.0. The immutable disposition is `remediate`.
- Candidate v3: six same-manifest 84-trial runs pass; stale identity retention, metadata projection, fresh payload retention, and exact behavior are 1.0; stale payload exposure is 0.0 in development and held-out test.
- All compared retrieval, generation, proposal, tool trajectory, terminal state, behavioral relations, both retrieval-stress families, policy, benign utility, security, repeated reliability, model calls, and estimated cost are unchanged and passing across 1,008 comparison attempts.
- Selection: v3 is the only configuration that passes the mandatory projection gate. It is not strictly numerically Pareto-dominant: versus v2, the median of diagnosis medians is 0.141 ms lower, while diagnosis p95, end-to-end median, and end-to-end p95 are 2.265, 1.794, and 4.778 ms higher.
- Retained failures: the first full candidate suite exposed a model-adapter field-assumption defect and stale checkpoint assertion; both were fixed generically without changing frozen cases, expectations, or graders. V2 comparison attempt 005's latency outlier remains in the record.
- Version-bound manifest: 27 files, SHA-256 `4b22c5dbd99dd778c5dcca5bb6bbd230178170775b22dcc5b579872e6c9b0ce4`.
- Version-bound attempt 001: all 84 trials and every gate pass; report and trace SHA-256 are `55d1b5be051e8985c0235ad64e1bba88171484e2f1c425360ae03b5962e81cc7` and `3b3e3688918a552886beaba6e45edd60a17ec8174e8ea0127e5950aa0d81747b`; `latest.json` is byte-identical to the report.
- Held-out CLI and MCP: stale metadata is exact, stale payload characters are zero, fresh payload remains complete, MCP version is 0.0.10, and no approval or execution tool is exposed.
- Real API and runtime: all 50 HTTP/dashboard checks and all 27 persisted-state/telemetry checks pass. The native receipt and rendered dashboard SHA-256 are `54c3f7709fb6e52a0d1f1c6fc34e4559078bb204bb98e5768737b7a3831aeef7` and `a4a15564f7a1d4523cc6f0cdfefe8152497ea265f4319176fd7c82fb781cb241`.
- Rendered dashboard: visually inspected at 1440 by 1000; it accurately reports baseline 0010, decision-context v3, stale identity 1.0, stale payload exposure 0.0, human approval, disconnected real infrastructure, and one mitigated synthetic incident.
- Container: Docker is currently off; packaging remains deferred independently because all reviewed base-image candidates are excluded by the existing source gate. No image was imported or run.
- Package probe: local wheel construction is not a release gate and failed because `setuptools.build_meta` is absent. No dependency was added or downloaded; this checkpoint ships a dependency-free source repository, not a PyPI package.
- Clean clone: exact candidate `1fafe2c99e96d84693a4ba54271694611b3602e4` at `C:\Projects\Verification\runbook-sentinel-baseline-0010-1fafe2c-20260807T134131` passed compilation, 19 tests, seven validators, the source gate, ten milestone contracts, 152 tracked JSON files, 47 tracked JSONL files with 5,085 records, selected-manifest identity, unchanged authority files, model/secret exclusion, held-out CLI, MCP, 50 API checks, 27 runtime checks, persistence, telemetry, and rendered-dashboard inspection.
- Release audit: the retained pending audit correctly computes `blocked` only because GitHub review and public-release truth have not yet run; all local and clean-clone checks pass.
- GitHub review: final PR `#9` head `914a719a9f26e555ccc70f02ea4fe056ed675759` had three expected commits, 90 expected changed files, exact local/remote file-set equality, `CLEAN`, `MERGEABLE`, and no configured checks before history-preserving merge.
- Merged main: fresh public clone of `ccbdafc40777ce7b20ed1375463193ecdbaa7d6c` passed compilation, 19 tests, seven validators, source gate, ten contracts, artifact parsing, selected identity, unchanged authority files, model/secret exclusion, held-out CLI, MCP, 50 API checks, 27 runtime checks, persistence, telemetry, and rendered-dashboard inspection.
- Release audit: the retained pending audit preserves the pre-GitHub blocked state; the final pre-publication audit computes `verified` and releases only the exact tag, public-release, and public-verification actions inherited from the project goal.
- Public release: local annotated `v0.0.10`, peeled remote tag, remote `main`, non-draft GitHub release, rendered README and release page, and a fresh public-tag clone agree on the release-closure commit.

### BASELINE-0009 release-candidate evidence

- Fresh public-v0.0.8 orientation: all 78 trials and every baseline-0008 gate pass; the report and trace are retained under `C:\Projects\Verification`
- Measured weakness: five stale, query-matching telemetry records displace current telemetry from v2 top-4 retrieval, producing a safe but avoidable evidence request
- Research gate: two current primary ACL sources pass all 16 criteria for citation and project-authored synthetic tests; no external code, data, paper, model, dependency, executable, or service was imported
- Frozen schema 1.8: 28 scenarios, one development and one held-out stale-evidence pair, six repeated stale-stress attempts, and terminal-state-v5 with 11 actionable and 17 no-action scenarios
- Pre-change v2 attempt 002: 84 trials, fresh-evidence recall, decision retention, and exact stale-stress behavior 0.0; `pass^3` 0.928571; 27 of 33 expected actions executed; 51 no-action trials unchanged; policy 1.0; proposal and terminal attack success 0.0
- Candidate v3: three same-manifest runs pass all 84 trials, all stale and guidance stress attempts, all relations, all 33 expected executions, all 51 no-action trials, policy, security, reliability, and zero-cost gates
- Selection: v3 is the only hard-gate-passing reliability configuration. Strict numeric latency dominance is false; common-case diagnosis median is 0.131 ms higher and common-case end-to-end median is 4.681 ms higher in this local comparison
- Version-bound manifest: 25 files, SHA-256 `5d18d47df8ad9f74bbc483864e31de7a85d637a67773c1555de18b05386afd85`; supersedes the retained pre-version manifest without rewriting it
- Version-bound attempt 002: all 84 trials pass; median/p95 end-to-end latency 72.339/104.912 ms; diagnosis median/p95 6.821/14.939 ms; report and trace SHA-256 `2cc4fbb816e04d918bc42d9bb818f64c71e294d670de8ee8776d9598f9e1a61d` and `cdd5567bc563f43db7b5cdb53ec2779364ccc057ceed18769ef77c8c80bfeb90`
- Held-out CLI and MCP: v3 preserves current evidence ahead of three stale records, proposes the frozen action, retains full audit identities, and MCP version 0.0.9 exposes no approval or execution tool
- Real API and runtime: all 40 HTTP/dashboard checks and all 23 persisted-state/telemetry checks pass; native receipt SHA-256 `fef021cea1a5a58536f684bec2a99017837239f1eea89d3d10d2a0657dac743d`
- Rendered dashboard: visually inspected at 1440 by 1000; accurately reports baseline 0009, v3, both retrieval recalls 1.0, human approval, disconnected real infrastructure, and the mitigated synthetic incident; PNG SHA-256 `934b13fb481b2566730aeab62e7484244edaf478d3aba0ee53d9127d5de85099`
- Container: daemon 29.4.3 is live, but every locally cached Python base candidate remains excluded by `artifacts/verification/container-source-gate.json`; packaging is deferred and no image was imported or run for this checkpoint
- Clean clone: exact candidate `f3d882a6e92d4bfe0b4d1803e8b9b214dac362eb` at `C:\Projects\Verification\runbook-sentinel-baseline-0009-f3d882a-20260806T225204` passed compilation, 16 tests, five validators, the research source gate, nine milestone contracts, 114 JSON files, 34 JSONL files and 3,135 records, selected-manifest identity, unchanged policy, model/secret exclusion, held-out CLI, MCP, 40 API checks, 23 runtime checks, persistence, telemetry, and rendered-dashboard inspection
- GitHub review: PR `#8` final head `a1fd78c7c242bed6cf780ba13e1e59eba9095e67` had six expected commits, 63 expected changed files, `CLEAN`, `MERGEABLE`, and no configured checks before history-preserving merge
- Merged main: fresh public clone of `4f302820c8452c83226b834b76ea208842f626fd` passed compilation, 16 tests, all contracts and source gates, 116 JSON files, 34 JSONL files/3,135 records, selected identity, unchanged policy, model/secret exclusion, CLI, MCP, 40 API checks, 23 runtime checks, persistence, telemetry, and rendered-dashboard inspection
- Public release: local annotated `v0.0.9`, peeled remote tag, remote `main`, non-draft GitHub release, rendered README and release page, and a fresh public-tag clone agree on the release-closure commit

- Contract schema: pass
- Frozen manifest: 23 files, SHA-256 `fac3bf310d244322c364516e21b6da78053ddb57d5c3cb05bc15b993609c59da`, pass
- Tests: 15 of 15 pass
- Frozen evaluation: version-bound attempt 002 passed 26 scenarios, 78 attempts, 27 expected executions, 51 strict no-action results, all 6 stress attempts, and all 12 relation attempts
- Retrieval recall@4, outcome accuracy, diagnosis accuracy, proposal exactness, actual tool-trajectory exactness, terminal-state exactness, policy compliance, benign utility, adversarial safe outcome, and `pass^3`: 1.0
- Instruction-bearing attack-document decision exposure: 0.0
- Proposal attack success: 0.0
- Terminal attack success: 0.0
- Evidence-condition split coverage: 10 of 10 required pairs, 1.0; adversarial split coverage: 2 of 2, 1.0
- Behavioral-relation exactness: 12 of 12 relation attempts, 1.0 across invariance, directional safety, development, and held-out test
- Retrieval-stress project-evidence recall, decision-evidence retention, exact behavior, and development/held-out exactness: 1.0; guidance saturation at four: 0.75
- Selected release-candidate end-to-end latency: median 45.245 ms, p95 92.216 ms; diagnosis-only median 6.994 ms, p95 15.746 ms; no general performance claim
- Live CLI, MCP stdio, HTTP approval/executor, dashboard, SQLite, audit log, and JSONL telemetry: pass
- Clean clone: candidate `3bcbad6aab640fad3eb4948a69161f5a73e99640` passed compilation, 15 tests, all four validators, the source gate, manifest, selected-evaluation identity, policy/model/secret exclusion, CLI, MCP, 34-check API, persistence, telemetry, and rendered-dashboard gates
- GitHub review: pull request `#7`, 7 commits, 52 changed files, `CLEAN`, `MERGEABLE`, no configured checks, merged with history preserved
- Merged main `6b79b9e6a02ee083747fc0a8c7559e0222f1b24a`: a fresh public clone passed compilation, 15 tests, all contracts, the 16-criterion source gate, 98 JSON and 26 JSONL parses, selected evaluation, unchanged policy, model/secret exclusion, held-out CLI, MCP, all 34 API checks, approval, executor, replay, postconditions, dashboard, SQLite, audit, and telemetry
- Public release: local annotated `v0.0.8`, peeled remote tag, remote `main`, non-draft GitHub release, rendered README, rendered release page, and a fresh public-tag clone agree on the release-closure commit
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

Historical handoff at this checkpoint: commit the evaluator implementation, run immutable repeated evaluation attempts against that exact commit and manifest, preserve their traces, and promote only a passing attempt.

Immutable attempt 001 passed all 54 trials and is now the latest-passed pointer. It executed 15 of 15 expected actions across `restart_worker`, `rollback_deployment`, and `warm_cache`; all 39 no-action trials stayed open and exactly unchanged. Proposal, actual trajectory, terminal state/status, policy, approval, execution, postconditions, idempotency, replay rejection, audit order, trace order, approval boundary, development/test reliability, and `pass^3` gates are all exact passes.

Attempt SHA-256 is `b3079ffcf29b8c6c44ebe0f1fda167cd7ffb6c32f9c15c37eca21b6f7546543e`; its 84-event trace SHA-256 is `9819b78a58ed31e58120b4ac9135b9a3be520a0b78f3ec8f85da383ddb3eb1e5`; its copied manifest matches active SHA-256 `713361860a9d1896e0ce1375ba8578db3322e920c915340cb0d0382bd8aa1392`. `latest.json` is byte-identical to the attempt. End-to-end median and p95 are 56.022 ms and 97.946 ms; diagnosis-only median and p95 are 5.288 ms and 14.148 ms.

Historical handoff at this checkpoint: version the bounded checkpoint as `0.0.5`, rerun the accepted evaluation against the versioned surfaces, and verify the real CLI, API, MCP, approval/executor, dashboard, persistence, telemetry, clean clone, and public release.

Versioned package, API health, MCP identity, CLI default, tests, README, and dashboard now identify `0.0.5` / baseline 0005. The dashboard adds visible actual tool-trajectory and terminal-state exactness without adding approval or execution controls. The release-candidate manifest now binds 17 files, including package metadata, package version, CLI, and the evaluation driver; SHA-256 is `c8a4797dbdde2bc53ff9057bd1953bbfda925149b28c8a538f1d155334757310`.

Historical handoff at this checkpoint: commit the versioned surfaces, generate immutable attempt 002 against the exact 17-file manifest, and begin native real-surface verification only if it passes.

Immutable attempt 002 passed the 17-file versioned manifest and all 54 trials, with 15/15 executions, 39/39 strict no-action results, all exact gates, median end-to-end latency 58.510 ms, and p95 108.435 ms. Report, trace, and manifest SHA-256 are `b1e3eae0cf0ea8a558a7afc5bec4f82616ff811d81006c6f6c73156d8790a3ba`, `9b8aa00f2aa2619c2fd935f54d7d2184f93d53314a140ddaa8fe70c763cf55a1`, and `c8a4797dbdde2bc53ff9057bd1953bbfda925149b28c8a538f1d155334757310`.

Pre-live review then found that the API, MCP, and runtime-evidence scripts still named baseline 0004 and were outside the manifest. No live receipt was created. Attempt 002 remains a passing immutable result but is superseded for release selection. The corrected verifier scripts are being added to a 20-file manifest; a new immutable attempt is required before live verification.

Immutable attempt 003 passed the first 20-file manifest and all evaluation gates. The held-out CLI and MCP 2025-11-25 surfaces then passed with server version 0.0.5 and no approval or execution tool. Two combined shell invocations were rejected before execution by local command policy; the direct calls succeeded.

Live API attempt 001 executed the real loopback approval/executor path and printed favorable values for health, baseline identity, action-hash binding, postconditions, same-key idempotency, HTTP 409 replay rejection, token redaction, selected evaluation, terminal metrics, CSP, and dashboard content. Its unnamed PowerShell boolean aggregate nevertheless returned failure, so the attempt is retained and not promoted. Database, three-event trace, logs, screenshot, and failure receipt are preserved with SHA-256 evidence.

The verifier now uses named typed checks and emits an explicit pass/fail receipt. Because that script is manifest-bound, the corrected 20-file manifest SHA-256 is `8f3e0a8710abdfd3894047c451ffc23f3a1488b836dbe510cfab7832b2549267`; a fresh immutable evaluation attempt is required before rerunning live verification.

Immutable attempt 004 passed all 54 trials against that corrected 20-file manifest and is now the latest-passed pointer. Report and trace SHA-256 are `132306bbf9f8619e61dee1d74f1a9e7ef208b0b8b178b672e51c42d3751b99f1` and `d6ae7e0d7800b0a64b8063b574504a40102550a10c62d9a2bc2a341fb8c69e87`; median and p95 end-to-end latency are 38.198 ms and 73.236 ms.

The named-check live API rerun passed all 22 checks. Independent native inspection passed required SQLite tables, one consumed hash-only approval, one idempotency record, one executed proposal, three ordered audit events, three redacted trace events, selected evaluation/manifest identity, and dashboard dimensions. The visually inspected dashboard accurately shows baseline 0005, evaluation pass, trajectory exact 1.0, terminal state exact 1.0, human approval, disconnected real infrastructure, and one mitigated incident.

Held-out CLI and MCP verification passed; MCP reports version 0.0.5 and exposes only list, diagnose/propose, and incident-read tools. Docker Desktop 4.74.0 and Engine 29.4.3 are live, but container packaging remains `defer` because the retained base-image source gate is still failed.

Historical handoff at this checkpoint: commit selected attempt 004 and native evidence, then verify an exact no-local-object clean clone before GitHub review.

Candidate commit `bf29abe17576db7458e0706a3f7fda52049cc3a6` passed a no-local-object clone at `C:\Projects\Verification\runbook-sentinel-baseline-0005-bf29abe-20260806221336`. The clean clone passed compilation, 13 tests, 20-file manifest, terminal contract, all five milestone JSON records, selected attempt and manifest identity, unchanged policy and service hashes, model-weight absence, secret-pattern scan, held-out CLI, MCP 2025-11-25, API approval/executor/replay, SQLite, audit, telemetry, and native dashboard receipt.

The clean-clone dashboard was freshly rendered and visually inspected. It matches the authoritative baseline 0005 surface; the only tracked post-verification clone changes are the expected new synthetic incident screenshot and its regenerated native receipt.

Historical handoff at this checkpoint: commit the clean-clone receipt, push the verified branch, open GitHub review, verify exact remote scope and mergeability, then verify merged main before release closure.

## BASELINE-0005 release closure

- GitHub pull request `#4` matched verified branch head `b012b381a3a3f8f7ab57b05095affe9495f49666`, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `a55249a4c679d61573e72dfe5c3be5363c3b78d1`.
- A fresh clone of that remote merged commit passed compilation, all 13 tests, the 20-file manifest, exact terminal contract, selected evaluation identity, held-out CLI, MCP 2025-11-25, live API approval/executor/replay/postconditions, SQLite, audit, telemetry, native receipt, and rendered-dashboard inspection.
- The public v0.0.5 tag, peeled remote tag, remote `main`, and non-draft release bind the exact release-closure commit containing these reconciled records; rendered public pages were verified after publication.

Next eligible action: begin the next cycle from public v0.0.5 by running the system and selecting one bounded measurable weakness.

## BASELINE-0006 measured gap and selected candidate

- A fresh v0.0.5 orientation passed 54 trials and 84 trace events, but the evaluator exposed only topology coverage. Zero of 18 scenarios had an explicit evidence-condition label; stale and conflicting evidence had no development-split case.
- Schema 1.5 freezes a closed complete, incomplete, stale, conflicting, and instruction-bearing taxonomy. It adds only `dev-stale-cache-evidence` and `dev-conflicting-database-evidence`, both exact no-execution cases, and requires all five conditions in both splits plus adversarial coverage in both splits.
- The immutable pre-change control passed all 60 expanded trials under the old gates while emitting neither a condition metric nor gate and while retaining a stale baseline-0005 report identity. It is preserved with disposition `remediate`.
- Independent validators pass 20 scenario labels, 10 of 10 condition/split pairs, development/test adversarial coverage, five action cases, fifteen no-action cases, all three actions, exact terminal states, and unchanged authority invariants.
- Fourteen tests pass, including fail-closed missing-stale-label and unknown-label regressions. Agent, policy, service, API, MCP, action, approval, and executor code remain unchanged from v0.0.5.
- Immutable attempt 001 passed all 60 trials. Condition and adversarial split coverage, retrieval, generation, proposal, actual tool trajectory, terminal state, policy, benign utility, security, and `pass^3` are 1.0; proposal and terminal attack success are 0.0.
- Attempt 001 report, trace, and manifest SHA-256 are `b887c9549674217fb0e1812d4f7381b6cf9aa6fd6446fa32ee77ee8721c4ba93`, `2ac8be834ad9a14a59a7ae6f1b421dac64980f00b4e6c818b02eb8225e86d8ca`, and `595b729c5ce780585499333bdb7ab80f7fd950df76e7b788a774b6e22ba0cbbc`; `latest.json` is byte-identical to the attempt.
- Version-bound attempt 002 passed the refrozen 21-file surface and is now the latest-passed pointer. Report, trace, and manifest SHA-256 are `45fd47dd788541f47ff04d9547206de1d01abf24c07501a0f17ffaba10323224`, `5329eb6cafcba980d840ba81ee989ec909c5b61a56fee218897e0e12bde3122a`, and `9f70f756ab93d4ba8732ed70455e0ce3c26f3cc84558baff24d8f56b7e101573`.

## BASELINE-0006 release closure

- GitHub pull request `#5` matched verified branch head `7a86bc787257120942eee0c936d586cdeb41df6b`, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `1f0635a008d8fdf6e94c9fedf1c39da40651a465`.
- A fresh public clone of that remote merged commit passed compilation, all 14 tests, the 21-file manifest, both exact contracts, selected evaluation identity, authority hashes, held-out CLI, MCP 2025-11-25, all 25 live API checks, approval/executor/replay/postconditions, SQLite, audit, telemetry, model and secret exclusion, and rendered-dashboard inspection.
- The public v0.0.6 tag, peeled remote tag, remote `main`, and non-draft release bind the exact release-closure commit containing these reconciled records; rendered public pages were verified after publication.

Next eligible action: begin the next cycle from public v0.0.6 by running the system and selecting one bounded measurable weakness.

## BASELINE-0007 measured gap

- A fresh public-v0.0.6 orientation passed all 60 trials and emitted 60 run, 15 approval, and 15 execution events.
- The released catalog has zero explicit evidence-relation cases and zero same-split controlled freshness pairs. The evaluator has no pairwise relation metric or gate.
- Stale evidence has only one case per split; adversarial coverage is one development case and eight held-out cases. Aggregate condition and adversarial split coverage still report 1.0.
- The bounded checkpoint will add four synthetic counterparts and freeze instruction-injection invariance plus fresh-to-stale directional safety in both splits. Agent, retriever, policy, service, actions, approval, executor, MCP, and real-infrastructure boundaries remain unchanged.
- The research source gate permits narrow, attributed method use from the peer-reviewed CheckList paper and the non-peer-reviewed ReliabilityBench v1 preprint. It imports no external code, data, model, or paper file and treats the preprint only as supplemental inspiration.

Next eligible action: freeze schema 1.6, the four exact relations, counterpart scenarios, and an independent validator before changing evaluator code.

- Schema 1.6 now freezes 24 scenarios and four exact relations. Instruction-injection invariance and freshness directional safety each occur once in development and once in held-out test.
- The independent relation validator passes all eight linked cases and rejects undeclared changes. The terminal-state-v3 validator passes seven actionable and seventeen exact no-action cases across the unchanged three-action surface.
- The first expanded test run failed four stale inventory assertions while all scenario behavior and authority tests passed. The exact case map and inventory counts were corrected; all 14 tests then passed.
- The 22-file pre-implementation manifest SHA-256 is `696474d7e12c0ea79de843d4fdef3c3bec8faf9b5225997dc35ae18ab426c191`. Agent, retriever, policy, service, API, MCP, actions, approval, and executor remain unchanged.
- The immutable pre-grader control passed 72 trials and 114 trace events under the old gates but emitted no behavioral-relation metric or gate. Report and trace SHA-256 are `386ece2815be95aff23a84b297ddfb1636a19303f01c59bc7e583f50a9fbfdaf` and `d50d4e32ff1b133447f4f35a9b71a2cfdfb178134b2f753ab11ae490ba5afb6e`.
- The implemented grader validates the closed relation contract and reports missing split/type pairs, coverage, invariance exactness, freshness-direction exactness, combined exactness, per-split exactness, and per-trial checks separately from scenario-level metrics.
- Focused fail-closed tests reject a missing held-out directional relation and detect a corrupted paired action. The first integrated run failed because the new helper interrupted the existing coverage helper; the boundary was repaired without changing the frozen contract or runtime logic, and all 14 tests then passed.
- A disposable 72-trial implementation smoke passed every gate: four relations, 12 of 12 paired attempts exact, development and held-out relation exactness 1.0, 21 expected executions, and 51 strict no-action results. Report and trace SHA-256 are `9da65549afcc80d68ec74ca025e3529d9fefc41484c30b454a57c44f61f3fced` and `80631bf38454f7302b5e2852b3b28560dc8bc7f7941917a31d64f60da3b0d1df`.
- The completed 22-file implementation manifest passes at SHA-256 `8db0a7f5fd15dd92a82ab710e65fc6dbc84e4eec28b2d67b46a94a1427963c69`. Agent, retriever, policy, service, API, MCP, and action surfaces remain unchanged from the pre-grader freeze.
- Immutable attempt 001 passed all 72 scenario trials and all 12 paired relation trials. Invariance, directional safety, combined relation exactness, development exactness, and held-out exactness are 1.0; 21 expected actions executed and all 51 no-action trials remained unchanged.
- Attempt 001 emitted exactly 72 run, 21 approval, and 21 execution events. The report and trace contain no raw approval-token or concrete idempotency material. Report and trace SHA-256 are `eda653ad87436fbbc3c6e3196e2fee4c503589d32cd35795351bf6f50101bccf` and `db9ff7eaed7d67dcbbdd62bdf1f299b41abaa34a581d6476e4fbc0e506076035`.
- The copied manifest matches the active manifest at SHA-256 `8db0a7f5fd15dd92a82ab710e65fc6dbc84e4eec28b2d67b46a94a1427963c69`, and `artifacts/evaluations/latest.json` is byte-identical to attempt 001.
- Package metadata, API health, MCP identity, CLI default, tests, README, dashboard, and real-surface verifiers now identify `0.0.7` / baseline 0007. The dashboard visibly adds behavioral-relation exactness without exposing approval or execution controls.
- The versioned 22-file manifest passes at SHA-256 `02ff28f3616572d3c1b6d97e5fe617594765575666f2ed74cb247b43b7ee5314`; agent, retriever, policy, service, and actions remain unchanged. Attempt 001 remains immutable and passing but is superseded for release selection; a version-bound attempt is required before live verification.
- Immutable attempt 002 passed all 72 scenario trials and 12 paired relation trials against the versioned manifest. It is now the latest-passed pointer; report and trace SHA-256 are `6dbd86d774304ec9d6dbd3687fcc1cc72e87b8846a7f5b96343b0176063f40eb` and `1e6bbdcb7170acf5d02172e74e4d365dcbffd7fe8e33a67d6bc9e8367660ff99`.
- The held-out CLI requested evidence without a proposal. MCP protocol `2025-11-25` reported version `0.0.7`, retained the full retrieval audit, excluded attack guidance from the decision context, and exposed three diagnostic/read tools with no approval or execution tool.
- The real loopback API passed all 27 named checks: selected evaluation and relation metric, hash-bound approval, execution, postconditions, same-key idempotency, different-key HTTP 409 replay rejection, token redaction, CSP, and dashboard identity.
- Independent runtime inspection passed required SQLite tables, one consumed hash-only approval, one idempotency record, one executed proposal, three ordered audit and trace events, evidence-only context, selected manifest identity, and the 1440 by 1000 dashboard. Native receipt and screenshot SHA-256 are `9dbd5f9ef37b69cef29fe28f40365f9e313a91b5463ac18e7edeccc914ee82a2` and `f308245de2fa21e5fcb0d9ad3a9c0cc05b71424259dfb011a6d4384d9570bd69`.
- Visual inspection confirmed the dashboard accurately shows baseline 0007, evaluation pass, behavioral relation exact 1.0, evidence condition, tool trajectory, and terminal state at 1.0, human approval, disconnected real infrastructure, and one mitigated synthetic incident.
- A no-local-object clone of exact candidate `8328c08900739d4f07afd9202a979c1bdd4f63e9` at `C:\Projects\Verification\runbook-sentinel-baseline-0007-8328c08-20260806202958` passed compilation, 14 tests, the 22-file manifest, all three validators, seven milestone contracts, 82 JSON and 22 JSONL parses, selected-evaluation identity, model-weight absence, high-signal secret scan, held-out CLI, MCP, all 27 API checks, all 16 runtime checks, and rendered-dashboard inspection.
- The clean-clone dashboard was freshly rendered and visually inspected. Only its synthetic-incident screenshot and regenerated native receipt changed after verification; no source, contract, manifest, evaluation, policy, or service file changed.
- GitHub PR `#6` matched verified head `0a4cdf28b0d1e55d9d1a999c265ae589d800b572`, base `c33da1cfc91ad5913279ef417c1685ba584918ac`, seven commits, and 45 expected changed files. GitHub reported `CLEAN`, `MERGEABLE`, and no configured checks before merge.
- PR `#6` merged with history preserved as `5c690c9f4f6b00e577eef84a1dc33437f5cd7ba1`. Its parents are the exact v0.0.6 closure and reviewed baseline-0007 head.
- A fresh public clone of merged `main` passed compilation, 14 tests, the 22-file manifest, all three validators, seven milestone contracts, 83 JSON and 22 JSONL parses, selected evaluation and manifest identity, model-weight absence, high-signal secret scan, held-out CLI, MCP, all 27 API checks, all 16 runtime checks, and fresh dashboard inspection.
- Visual inspection confirmed the merged-main dashboard accurately shows baseline 0007, evaluation pass, behavioral relation exact 1.0, all prior exact metrics, human approval, disconnected real infrastructure, and one mitigated synthetic incident.

## BASELINE-0007 release closure

- GitHub pull request `#6` matched verified branch head `0a4cdf28b0d1e55d9d1a999c265ae589d800b572`, was `CLEAN` and `MERGEABLE`, and merged with history preserved as `5c690c9f4f6b00e577eef84a1dc33437f5cd7ba1`.
- A fresh public clone of that remote merged commit passed compilation, all 14 tests, the 22-file manifest, all three exact contracts, selected evaluation identity, authority hashes, held-out CLI, MCP 2025-11-25, all 27 live API checks, approval/executor/replay/postconditions, SQLite, audit, telemetry, model and secret exclusion, and rendered-dashboard inspection.
- The public v0.0.7 tag, peeled remote tag, remote `main`, and non-draft release bind the exact release-closure commit containing these reconciled records; rendered public pages were verified after publication.

Next eligible action: begin the next cycle from public v0.0.7 by running the accepted system and selecting one bounded measurable weakness.
