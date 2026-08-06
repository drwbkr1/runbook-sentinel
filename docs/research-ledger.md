# Research ledger

Reviewed 2026-08-06. References inform design; they are not imported datasets or code.

| Source | Identity and authority | Design use |
|---|---|---|
| AgentDojo, NeurIPS 2024, arXiv:2406.13352v3 | Primary benchmark paper from ETH Zurich and collaborators; rechecked 2026-08-06 | Treat tool-returned data as untrusted; measure benign utility, attack exposure, attack success, and environment-state outcomes separately |
| Defeating Prompt Injections by Design (CaMeL), arXiv:2503.18813v2 | Primary research paper; rechecked 2026-08-06 | Separate untrusted data from control flow and enforce capabilities outside the model; baseline-0003 tests a narrower evidence-only decision context inspired by this principle, not a CaMeL implementation |
| tau-bench, 2024 | Primary benchmark paper | Exact terminal-state grading and repeated-trial `pass^k` |
| RAGChecker, NeurIPS 2024 | Primary benchmark paper | Diagnose retrieval and generation separately |
| NIST SP 800-61r3, April 2025 | Official NIST incident-response publication | Incident work spans preparation, detection, response, and recovery |
| NIST AI 600-1, updated 2026 | Official NIST generative-AI profile | Lifecycle risk and evaluation governance |
| MCP specification 2025-11-25 | Official protocol specification | JSON-RPC surface, tool schemas, authorization and elicitation boundaries |
| MCP Security Best Practices 2025-11-25 | Official protocol guidance | Least privilege, no token passthrough, local server and session risks |
| OpenTelemetry semantic conventions 1.44 | Official observability specification | Trace vocabulary; experimental GenAI fields must be version-pinned before adoption |
