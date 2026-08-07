# Research ledger

Reviewed 2026-08-06. References inform design; they are not imported datasets or code.

| Source | Identity and authority | Design use |
|---|---|---|
| Beyond Accuracy: Behavioral Testing of NLP Models with CheckList, ACL 2020, DOI 10.18653/v1/2020.acl-main.442 | Primary peer-reviewed ACL proceedings paper; CC BY 4.0; checked live 2026-08-06; source gate `artifacts/verification/research-source-gate-baseline-0007.json` | Use project-authored minimum-functionality, invariance, and directional-expectation relations; no CheckList code or data is imported |
| ReliabilityBench, arXiv:2601.06112v1 | Primary author-submitted preprint; not peer reviewed; CC BY 4.0; checked live 2026-08-06; source gate `artifacts/verification/research-source-gate-baseline-0007.json` | Supplemental inspiration for action metamorphic relations based on end-state equivalence; not evidence of production readiness or comparative safety |
| Meta Llama 3.2 model card, Community License, and AUP | Primary publisher records in `meta-llama/llama-models`; checked live 2026-08-06 | Bound a local 3B Instruct evaluation to synthetic evidence, no model tools, system-level safeguards, application-specific adversarial evaluation, and no real critical-infrastructure operation |
| Ollama 0.32.5 release and `llama3.2:3b` registry entry | Primary Ollama release, tagged MIT license, and registry; checked live 2026-08-06 | Establish loopback runtime identity, model package identity, instruction-model fitness claims, and reproducible local adapter seam before empirical evaluation |
| AgentDojo, NeurIPS 2024, arXiv:2406.13352v3 | Primary benchmark paper from ETH Zurich and collaborators; rechecked 2026-08-06 | Treat tool-returned data as untrusted; measure benign utility, attack exposure, attack success, and environment-state outcomes separately |
| Defeating Prompt Injections by Design (CaMeL), arXiv:2503.18813v2 | Primary research paper; rechecked 2026-08-06 | Separate untrusted data from control flow and enforce capabilities outside the model; baseline-0003 tests a narrower evidence-only decision context inspired by this principle, not a CaMeL implementation |
| tau-bench, 2024, arXiv:2406.12045 | Primary benchmark paper; rechecked 2026-08-06 | Compare deterministic database state at the end of an interaction with an annotated goal state and report repeated-trial `pass^k`; baseline-0005 applies this to isolated synthetic approval and execution trajectories |
| RAGChecker, NeurIPS 2024 | Primary benchmark paper | Diagnose retrieval and generation separately |
| NIST SP 800-61r3, April 2025 | Official NIST incident-response publication | Incident work spans preparation, detection, response, and recovery |
| NIST AI 600-1, updated 2026 | Official NIST generative-AI profile | Lifecycle risk and evaluation governance |
| MCP specification 2025-11-25 | Official protocol specification | JSON-RPC surface, tool schemas, authorization and elicitation boundaries |
| MCP Security Best Practices 2025-11-25 | Official protocol guidance | Least privilege, no token passthrough, local server and session risks |
| OpenTelemetry semantic conventions 1.44 | Official observability specification | Trace vocabulary; experimental GenAI fields must be version-pinned before adoption |
