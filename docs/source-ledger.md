# External source ledger

## Approved for baseline-0001

No external runtime package, model, dataset, or third-party code is imported. The runtime uses Python 3.12 standard-library modules only. Project-authored synthetic scenarios are the only dataset.

## Approved specification use for baseline-0011 and baseline-0012

Official Python 3.12.13 `zipapp`, `zipfile`, and PSF licensing documentation passed the eight-criterion source gate in `artifacts/verification/research-source-gate-baseline-0011.json`. Approval covers citation, narrow paraphrase, and a project-authored standard-library zipapp builder and verifier. No external code, package, sample archive, executable, data, model, or service was imported. The same reviewed primitives support the superseding v0.0.12 package contract.

## Approved specification use for baseline-0017

Official Python 3.12.13 `os` and `tempfile` documentation passed the eight-criterion gate in `artifacts/verification/research-source-gate-baseline-0017-live-anchor.json`. Approval covers narrow citation and project-authored trace flush/fsync, secure same-directory temporary creation, temporary-file flush/fsync/close, and `os.replace`. No external code, sample, package, executable, data, model, service, key, credential, or trace was imported. Cross-filesystem atomicity, directory-entry durability, writer authentication, and hostile-writer resistance are not claimed.

## Pending before use

| Asset | Current local observation | Required gate |
|---|---|---|
| `llama3.2:3b` via Ollama | Tool-capable 3.2B Q4_K_M; Llama 3.2 Community License reported by local metadata | Verify upstream identity, manifest digest, license applicability, integrity, fitness, security, and reproducible invocation |
| `bge-m3` via Ollama | 566.7M F16 embedding model; local metadata reports MIT text | Verify exact upstream identity, digest, complete license provenance, retrieval fitness, security, and reproducible invocation |
| Docker Official Python base image | Official Image packaging is MIT-licensed and community-maintained; current tags were resolved from Docker Hub | Three candidates were excluded: slim Trixie and Bookworm each had 2 critical and 2 high unfixed Perl findings; Alpine had 2 high unfixed SQLite findings. Exact digests are retained in `artifacts/verification/container-source-gate.json`. No container image is approved. |

GitHub repository creation is not an asset import. The user released the access gate by explicitly selecting public visibility on 2026-08-06. The repository contains no imported third-party code, data, model, or runtime package.
