# External source ledger

## Approved for baseline-0001

No external runtime package, model, dataset, or third-party code is imported. The runtime uses Python 3.12 standard-library modules only. Project-authored synthetic scenarios are the only dataset.

## Pending before use

| Asset | Current local observation | Required gate |
|---|---|---|
| `llama3.2:3b` via Ollama | Tool-capable 3.2B Q4_K_M; Llama 3.2 Community License reported by local metadata | Verify upstream identity, manifest digest, license applicability, integrity, fitness, security, and reproducible invocation |
| `bge-m3` via Ollama | 566.7M F16 embedding model; local metadata reports MIT text | Verify exact upstream identity, digest, complete license provenance, retrieval fitness, security, and reproducible invocation |
| Docker Official Python base image | Official Image packaging is MIT-licensed and community-maintained; current tags were resolved from Docker Hub | Three candidates were excluded: slim Trixie and Bookworm each had 2 critical and 2 high unfixed Perl findings; Alpine had 2 high unfixed SQLite findings. Exact digests are retained in `artifacts/verification/container-source-gate.json`. No container image is approved. |

GitHub repository creation is not an asset import. The user released the access gate by explicitly selecting public visibility on 2026-08-06. The repository contains no imported third-party code, data, model, or runtime package.
