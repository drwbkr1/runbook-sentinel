# ADR 0025: Align the declared diagnosis pattern before retuning

- Status: accepted
- Date: 2026-08-15
- Checkpoint: baseline-0030

## Context

Public v0.0.29 remains exact and useful under the deterministic control. The retained local-model comparison is not useful: 9 of 84 outputs parse, benign utility and pass-three reliability are zero, and 75 outputs fail closed. Sixty-seven of those failures are `diagnosis_code_invalid`.

The cause is a measurable interface mismatch. `eval/model-contract.json` tells Ollama only that `diagnosis_code` is a string from one through 80 characters, while `parse_model_content` requires `^[a-z][a-z0-9_]{0,79}$`. The parser is the security boundary and correctly rejects the broader schema language. The declared schema therefore fails to express the first static constraint that the generated value must cross.

Official JSON Schema Draft 2020-12 defines `pattern` as a string assertion. Ollama's exact v0.32.6 documentation says the local chat API accepts a JSON Schema object in `format`. These sources establish a credible experiment, not runtime fitness or a result.

## Decision

Freeze one change: add the external parser's existing diagnosis identifier pattern to the schema supplied to the unchanged installed `llama3.2:3b` model. Advance only the model-contract identity metadata needed to distinguish the candidate. Do not change the prompt, generation options, model bytes, runtime, parser acceptance, retrieval, evidence projection, scenarios, terminal states, policy, approval, executor, tools, or authority.

Preserve the exact v2 contract as `eval/model-contract-0018-v2.json`. After the preimplementation freeze is public and remotely exact, compare the legacy and candidate contracts on the same 57 frozen scenarios and three trials. Report retrieval, generation, trajectory, policy, utility, attack success, repeated-trial reliability, latency, and cost separately. Retain raw model output only by digest and stable failure code.

The deterministic control remains the product default. The v3 contract can replace v2 only as the experimental local-model contract if it improves development structured parsing without held-out policy or attack regression. It cannot become the product default unless it independently meets every existing deterministic-default gate.

## Consequences

- The experiment directly targets 67 of 75 measured schema-invalid outcomes without widening parser acceptance.
- A syntactically valid diagnosis code can still be wrong. Exact diagnosis, evidence use, proposal semantics, terminal state, latency, and cost remain independent gates.
- Proposal-argument and out-of-context evidence failures remain retained and out of scope for this one-field checkpoint.
- External enforcement remains fail closed, the model retains no tool or credential access, and no model output carries approval or execution authority.
- The result may be unfavorable. Failure, no improvement, or runtime non-support will be preserved and the candidate excluded.
