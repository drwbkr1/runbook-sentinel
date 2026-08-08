# Architecture

## Baseline topology

1. A frozen scenario catalog provides a closed synthetic SRE environment, explicit topology domain, development or test split, evidence, expected proposal, exact full terminal state and status, exact evaluation trajectory, and mutable synthetic state.
2. A deterministic freshness-priority lexical retriever returns a full ranked set as untrusted data. It uses the scenario's explicit `as_of`, first ranks project-classified telemetry/status that pass the shared fail-closed one-hour rule, then stale project evidence, then untrusted guidance. Complete returned records remain in the audit-facing result.
3. A deterministic decision-context policy passes complete fresh telemetry/status records but projects stale telemetry/status records to exactly `id`, `kind`, and `observed_at`. It records excluded runbooks as guidance-only and records field inventories plus stale-payload exposure counts. In the synthetic catalog, document kind and timestamp are trusted project-authored metadata; any real intake must assign and verify them outside the model.
4. A bounded control agent independently extracts only allowlisted facts from fresh decision-context records. Retrieved prose never controls program flow. Version 2 includes non-action diagnoses for gateway, API latency, worker capacity, configuration, and observability gaps.
5. The agent returns exactly one outcome: `diagnose`, `request_evidence`, `propose_action`, or `abstain`.
6. Proposals are typed, hashed, and persisted. No agent interface exposes approval or execution.
7. A human-facing API or CLI creates a short-lived approval bound to the proposal hash and actor.
8. A deterministic policy gate validates capability and arguments, consumes the approval once, applies an allowlisted synthetic state transition, verifies postconditions, and records idempotency and audit evidence.
9. SQLite persists operational state. JSONL traces record redacted runtime events and decision-context configuration. The dashboard renders current checkpoint, boundaries, evaluation disposition, and persisted incidents.

The executor action surface remains exactly `restart_worker`, `rollback_deployment`, and `warm_cache`; baselines 0005 through 0010 add no capability or runtime state mutation. Its optional local-model adapter is evaluation-only, direct-loopback, no-tools, and fail-closed. The excluded model candidate is not the operational default.

During frozen evaluation only, an isolated harness waits until the agent result is persisted, then acts as a synthetic external approver against temporary SQLite state. It invokes the same approval and execution methods as the operator surface, verifies same-key idempotency and different-key replay rejection, and grades exact incident state, status, audit events, and trace names. The raw approval token and idempotency key remain temporary local variables; neither appears in the report, persisted run JSON, nor telemetry. This harness is not reachable through the CLI, API, MCP server, dashboard, or agent/model interface.

Baseline 0007 adds a relation plane to evaluation, not runtime. A frozen contract links one control and one variant, declares the only permitted evidence transformation, and specifies either exact invariance or a directional safety transition. The evaluator compares already-produced scenario results and terminal records; it gains no approval, execution, model, or infrastructure authority beyond the existing isolated harness.

Baseline 0009 adds a second retrieval-stress plane. Frozen pairs append stale query-matching project records without changing current evidence or exact terminal expectations. The independent validator and evaluator separately measure current-evidence recall, decision retention, stale saturation, behavior, trajectory, and terminal exactness. This changes deterministic retrieval ordering only; it grants no trust to evidence-provided timestamps. Any future real intake must authenticate and normalize source, kind, timestamp, and provenance outside the model before entering this architecture.

Baseline 0010 narrows the decision and optional-model plane after retrieval. Full returned documents remain available for audit, while the field-preserving serializer cannot reconstruct stale `title` or `content` that the projection removed. The independent projection validator and evaluator separately grade contract validity, split coverage, stale identity retention, exact metadata fields, stale payload exposure, fresh payload retention, and behavior. The record ID and timestamp support an exact request for replacement evidence but grant no authority.

Baseline 0012 adds a packaging plane without changing runtime authority. A standard-library builder reads an exact 21-entry allowlist, copies project bytes without transformation, fixes ZIP timestamps and permissions, excludes caches and runtime state, embeds the frozen evaluation manifest, and generates a package manifest with the package-contract hash and every non-self entry hash. An independent verifier checks source parity, ordering, metadata, exclusions, and both manifest bindings. The archive is invoked with Python 3.12 or newer and contains no dependency, credential, approval material, executor expansion, or real-infrastructure connector.

The dashboard checkpoint label derives from the same `CHECKPOINT` constant returned by health. The stopped baseline-0011 candidate showed why release identity is a real-surface invariant: its health and evaluation were correct while an independent HTML literal was stale. Baseline 0012 removes that duplicate identity and verifies the rendered output for source and packaged runtimes.

Baseline 0015 implements a project-specific per-launch operator capability for approval creation. One `Sentinel-Capability` authorization field is required before body parsing, caller-declared `actor` is rejected, a launch-scoped pseudonymous identity is derived server-side, and only an in-memory verifier is retained. The public approve CLI is an HTTP client with hidden-prompt or standard-input custody and no direct approval-store path. Raw capability values are forbidden from arguments, environment variables, repository and package files, SQLite, audit, traces, evaluation reports, dashboard HTML, structured logs, the model, and MCP. The boundary is labeled authenticated external operator, not human presence, Bearer, OAuth, or production identity.

## Ports and trust boundaries

- CLI and HTTP API are local operator surfaces.
- MCP uses standard input/output and exposes scenario listing, diagnosis/proposal, and incident reading only.
- Full retrieval records and guidance-only identities are audit data, not authority. Stale project payloads remain on the audit side of the decision boundary.
- The model boundary ends at typed output. It cannot call the approval broker or executor.
- The executor can mutate only repository-local synthetic state.
- The evaluation harness can approve and execute only after the bounded result exists and only inside disposable synthetic evaluation state.
- No outbound connector, credential store, arbitrary shell, or real-infrastructure adapter exists.

## Configuration seams

Retriever and agent implementations are explicit objects with stable names in evaluation output. Later cycles may add approved dense, hybrid, or model-backed configurations without changing the policy/executor boundary.
