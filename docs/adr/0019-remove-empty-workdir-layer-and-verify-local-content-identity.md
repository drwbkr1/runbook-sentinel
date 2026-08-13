# ADR 0019: Remove the empty WORKDIR layer and verify local content identity

- Status: accepted for BASELINE-0027 container-runtime-v4
- Date: 2026-08-12

## Context

Container-runtime-v3 made two independent no-cache builds reproducible at image ID `sha256:ad9160e8976174c34d05671a7293389943ef260d3b14c2d7996689f9c9fdd1c1`, but its image validator stopped before runtime. The pinned base has eleven rootfs layers; v3 added the two deterministic COPY layers plus the canonical empty diff layer emitted by `WORKDIR`, for fourteen total. The exact Docker 29.4.3 containerd image store also assigned a local content-addressed `RepoDigest` equal to the image ID. V3 incorrectly expected both exactly two added layers and no local repository digest.

Official Docker documentation at revision `c8c1ada37a8a3c598d0f8744d66f2dfbb780c145` states that `WORKDIR` creates its directory when needed, while COPY creates missing destination paths. The exporter documentation distinguishes local image-store loading from registry push, and the CLI documentation describes digests as content-addressed image identifiers. Exact source identities and the retained v3 measurement are gated in `artifacts/verification/research-source-gate-baseline-0027-container-v4.json`.

## Decision

Container-runtime-v4 removes only the `WORKDIR` instruction. The entrypoint and application paths remain absolute, and the runtime's default working directory is verified as `/`. The image must therefore preserve the exact eleven-layer base prefix and add exactly two COPY layers containing only the selected zipapp and evaluation report with UID/GID 65532.

On the frozen Docker/Buildx/BuildKit boundary, the local `RepoDigest` is required to resolve to the same content identity as the image ID. No-publication evidence comes from the exact image exporter configuration (`store=true`, `push=false`, no destination), absence of registry authentication or push/export actions, and local-scope Docker events—not from pretending the local image has no digest.

## Consequences

- Incident-agent behavior, retrieval, policy, approval, executor, API, MCP authority, and synthetic-only scope do not change.
- Runtime remains non-root, read-only, capability-free, no-new-privileges, network-none, and disconnected from real infrastructure.
- Container image bytes remain local and are neither archived nor pushed or published.
- V3 and every earlier failed or excluded result remain retained.
- Reproducibility claims remain limited to the exact verified builder and clean-clone evidence; no cross-version guarantee is made.
