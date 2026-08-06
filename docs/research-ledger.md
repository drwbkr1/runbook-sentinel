# Research ledger

Reviewed 2026-08-06. References inform design; they are not imported datasets or code.

| Source | Identity and authority | Design use |
|---|---|---|
| AgentDojo, NeurIPS 2024 | Primary benchmark paper from ETH Zurich and collaborators | Untrusted tool content; separate benign utility and attack success; environment-state graders |
| Defeating Prompt Injections by Design (CaMeL), 2025 | Primary research paper | Keep capabilities and control flow outside the model |
| tau-bench, 2024 | Primary benchmark paper | Exact terminal-state grading and repeated-trial `pass^k` |
| RAGChecker, NeurIPS 2024 | Primary benchmark paper | Diagnose retrieval and generation separately |
| NIST SP 800-61r3, April 2025 | Official NIST incident-response publication | Incident work spans preparation, detection, response, and recovery |
| NIST AI 600-1, updated 2026 | Official NIST generative-AI profile | Lifecycle risk and evaluation governance |
| MCP specification 2025-11-25 | Official protocol specification | JSON-RPC surface, tool schemas, authorization and elicitation boundaries |
| MCP Security Best Practices 2025-11-25 | Official protocol guidance | Least privilege, no token passthrough, local server and session risks |
| OpenTelemetry semantic conventions 1.44 | Official observability specification | Trace vocabulary; experimental GenAI fields must be version-pinned before adoption |
