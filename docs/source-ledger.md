# External source ledger

BASELINE-0030 admits only citation and narrow paraphrase from official JSON Schema Draft 2020-12 and exact-tag Ollama v0.32.6 documentation under `artifacts/verification/research-source-gate-baseline-0030-model-output-conformance.json`. This supports one project-authored diagnosis-pattern experiment and no external asset import. The already installed Ollama and `llama3.2:3b` bytes remain governed by `artifacts/verification/model-source-gate-baseline-0018.json`; no download, update, copy, redistribution, remote call, model tool, secret, personal data, or real-infrastructure use is authorized.

BASELINE-0029 admits only citation and narrow paraphrase from two primary retrieval-evaluation papers under `artifacts/verification/research-source-gate-baseline-0029-retrieval-quality.json`. RAGChecker arXiv v2 supports separate retriever/generator diagnostics, chunk-level context precision, and the useful-information/noise tradeoff. The peer-reviewed EACL 2024 RAGAs paper supports treating focused context, generator faithfulness, and generation quality as separate dimensions and penalizing redundant context. Runbook Sentinel's exact-ID semantics, neutral expected-document-share name, rank buckets, thresholds, graders, tests, and synthetic corpus are project-authored. No paper bytes, code, dataset, benchmark, model, prompt, metric package, service, secret, or real infrastructure are imported.

Baseline-0027 preserves its first narrow BuildKit/Docker gate and adds validated successor `artifacts/verification/research-source-gate-baseline-0027-buildkit-reproducibility-v2.json` after `SOURCE_DATE_EPOCH` alone failed to make COPY layers deterministic. The successor binds exact official BuildKit and Docker Docs revisions and authorizes only project-authored use of the final-manifest epoch plus `type=image`, `rewrite-timestamp=true`, `store=true`, `unpack=false`, and `push=false` after the v3 contract is public. No external code, sample, configuration, package, executable, service, secret, image, data, or model is imported. No mutable dependency, authentication, purchase, network widening, archive destination, registry push, publication, or redistribution is authorized.

## Approved for baseline-0001

Accepted v0.0.26 imports no external runtime package, model, dataset, or third-party code. Its application runtime uses Python 3.12-or-newer standard-library modules only, and project-authored synthetic scenarios are the only dataset.

Baseline-0027 conditionally adds one external container base around—not inside—the dependency-free application package. The exact Chainguard Free Python OCI index `sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5` passes the eight-criterion gate in `artifacts/verification/container-source-gate-baseline-0027-chainguard-python.json` for anonymous digest-bound local build and runtime verification. The admitted linux/amd64 manifest is `sha256:15e66fa35e0b07095bbc4f4f0522718b780944709026687485f4e712cc6d5ae0`; local metadata and a current scan identify Python 3.14.7, UID 65532, 54 packages, and zero observed critical/high/medium/low findings. The prior three official Python candidates remain excluded. This gate authorizes no mutable tag, authentication, purchase, build dependency, image export, registry push, publication, redistribution, secret, or real-infrastructure access; no Runbook Sentinel image exists yet.

## Approved specification use for baseline-0011 and baseline-0012

Official Python 3.12.13 `zipapp`, `zipfile`, and PSF licensing documentation passed the eight-criterion source gate in `artifacts/verification/research-source-gate-baseline-0011.json`. Approval covers citation, narrow paraphrase, and a project-authored standard-library zipapp builder and verifier. No external code, package, sample archive, executable, data, model, or service was imported. The same reviewed primitives support the superseding v0.0.12 package contract.

## Approved specification use for baseline-0017

Official Python 3.12.13 `os` and `tempfile` documentation passed the eight-criterion gate in `artifacts/verification/research-source-gate-baseline-0017-live-anchor.json`. Approval covers narrow citation and project-authored trace flush/fsync, secure same-directory temporary creation, temporary-file flush/fsync/close, and `os.replace`. No external code, sample, package, executable, data, model, service, key, credential, or trace was imported. Cross-filesystem atomicity, directory-entry durability, writer authentication, and hostile-writer resistance are not claimed.

## Baseline-0023 external-source disposition

Baseline-0023 reuses only the previously approved CheckList citation for the narrow capability-by-slice rationale. The outcome/split contract, transformed telemetry, grader, thresholds, package entry, and all evaluation bytes are project-authored. No external code, paper bytes, dataset, model, package, sample, executable, service, credential, or other asset was accessed or imported.

## Pending before use

| Asset | Current local observation | Required gate |
|---|---|---|
| `bge-m3` via Ollama | 566.7M F16 embedding model; local metadata reports MIT text | Verify exact upstream identity, digest, complete license provenance, retrieval fitness, security, and reproducible invocation |
| Docker Official Python base image | Official Image packaging is MIT-licensed and community-maintained; current tags were resolved from Docker Hub | Three candidates were excluded: slim Trixie and Bookworm each had 2 critical and 2 high unfixed Perl findings; Alpine had 2 high unfixed SQLite findings. Exact digests are retained in `artifacts/verification/container-source-gate.json`. No container image is approved. |

GitHub repository creation is not an asset import. The user released the access gate by explicitly selecting public visibility on 2026-08-06. The repository contains no imported third-party code, data, model, or runtime package.
