# ADR 0003: retain the local-model seam and exclude the measured candidate

- Status: accepted
- Date: 2026-08-06
- Checkpoint: baseline-0004

## Context

Runbook Sentinel had a verified deterministic control but no measured stochastic generation configuration. The exact local Ollama 0.32.5 runtime and Llama 3.2 3B Instruct Q4_K_M artifact passed a source gate for frozen synthetic evaluation only. The comparison contract required identical retrieval, decision context, scenarios, splits, and three trials per case, with no model tools, credentials, approvals, execution authority, or deterministic fallback.

## Decision

Keep the standard-library loopback adapter and exact untrusted-output parser as an optional evaluation seam. Keep `deterministic-control-v2` as the operational and evaluation default. Exclude `ollama-llama3.2-3b-instruct-q4-k-m-v1` from selection based on the frozen attempt; do not tune on the held-out test split and do not reinterpret fail-closed abstentions as model quality.

The adapter may only reach direct `127.0.0.1:11434/api/chat`. It disables proxies, redirects, streaming, and tools. Model output remains a proposal-domain input to deterministic policy; it never carries approval or execution authority.

## Evidence

Across 18 cases and 54 attempts, the deterministic control achieved exact trajectory and `pass^3` of 1.0 with median latency 8.160 ms. The local-model candidate achieved structured parse success of 5/54, diagnosis accuracy 0.0, exact trajectory 0.0, benign utility 0.0, and `pass^3` 0.0 with median latency 12448.711 ms. Retrieval remained 1.0 for both configurations.

Candidate policy compliance remained 1.0 and proposal attack success remained 0.0, but the candidate made no accepted action proposal. Those safety results demonstrate the parser and external policy boundary failing closed; they do not establish useful model safety. The exact comparison and immutable artifacts are recorded in `artifacts/evaluations/baseline-0004-comparison.json`.

## Consequences

- The public checkpoint can demonstrate a real, source-gated model comparison without claiming that the model improves Runbook Sentinel.
- No model weights, runtime binaries, packages, credentials, or externally billed services enter the repository.
- The deterministic control remains useful, repeatable, and policy-compliant under the frozen evidence suite.
- A future model candidate requires a new frozen attempt. Parser diagnostics or development-prompt changes may be explored, but held-out results remain immutable and cannot be rewritten.
