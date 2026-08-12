# ADR 0018: normalize local image layers without weakening the contract

- Status: accepted for BASELINE-0027 v3 implementation
- Date: 2026-08-12

## Context

Container-runtime-v2 froze two independent image IDs, an exact base-layer prefix, and exactly two added payload layers. Its Dockerfile placed `WORKDIR` before two COPY directives. The first two no-cache builds failed image identity. Later exact inspection corrected the layer boundary: the digest-pinned base has eleven layers, while each v2 candidate adds a directory-only `WORKDIR` layer plus the two payload layers.

A second run supplied the final-manifest epoch through Buildx's special `SOURCE_DATE_EPOCH` path. Both image configs then used the exact frozen creation time, but COPY-layer digests and image IDs still differed. BuildKit's official reproducibility specification distinguishes image-config/history normalization from its image-exporter option for rewriting file timestamps inside layers. Two bounded `type=image`, `rewrite-timestamp=true`, `unpack=false` probes produced one exact local image ID but remain excluded because their settings were not frozen and the v2 Dockerfile still added three layers.

## Decision

Retain v1 and v2 contracts and every failed or excluded result. Freeze container-runtime-v3 before implementation. Keep exactly two candidate-added rootfs layers by copying the zipapp and evaluation report to absolute paths before declaring `WORKDIR`; because the directory then exists, `WORKDIR` must not create a third rootfs layer.

Set `SOURCE_DATE_EPOCH=1786556577`, derived from retained final-source companion manifest SHA-256 `cdc9ced520421f89b87ea04629bbce1b4a80e7f875b4366a6359c987a009f67a`, in the Buildx caller environment. This identity remains stable when the current release manifest is renewed. Use only the local image exporter with `rewrite-timestamp=true`, `store=true`, `unpack=false`, `push=false`, no destination archive, no build network, no cache, no provenance export, and no SBOM export. Require two clean process exits, exact frozen image creation time, identical image IDs, exact eleven-layer base prefix, exact two-layer payload allowlist, and an independently identical clean-clone build.

Bind the release claim to Docker Engine 29.4.3, Docker Desktop 4.74.0, Buildx 0.33.0-desktop.1, BuildKit 0.29.0, and the Docker driver actually verified. A later builder version requires renewed empirical evidence; the project does not claim universal cross-version reproducibility.

## Consequences

- The security and authority boundary is unchanged: digest-pinned base, no build or runtime egress, non-root, read-only, capability-free, no secret or real infrastructure, and no container export or publication.
- The two-payload-layer requirement is preserved rather than relaxed to accommodate an implementation accident.
- The manifest-bound Dockerfile, runtime verifier, package, source/package evaluations, real surfaces, and clean-clone evidence must be renewed after the public v3 freeze.
- Failed v2 builds and excluded probes remain visible and cannot be promoted into passing release evidence.
