# ADR 0022: Stream and verify tmpfs artifacts with unprivileged exec

- Status: accepted for BASELINE-0027 container-runtime-v7
- Date: 2026-08-12

## Context

Container-runtime-v6 reproduced the image exactly twice, passed local event, image, hardened runtime, CLI, and evaluation execution gates, then failed when `docker cp` attempted to read `/state/container-evaluation.json`. A bounded rerun proved that the report and trace existed in the `/state` tmpfs with exact sizes and SHA-256 identities and that the evaluation exec exited zero. The same `docker cp` failure reproduced.

Docker's official `container cp` specification says that resources under tmpfs and user-created mounts cannot be copied with `docker cp`, and identifies `docker exec` as the recovery path. The official `container exec` specification permits an exact executable to run in an already-running container. The retained evidence therefore classifies this as an extraction-mechanism defect, not an evaluation, product, or runtime-security failure.

## Decision

Container-runtime-v7 will replace only the `docker cp` extraction helper. For each exact allowlisted project-owned `/state` file, it will:

1. reject a non-allowlisted source, an existing destination, or a source larger than the frozen maximum;
2. invoke the image's existing `/usr/bin/python` through `docker exec` as the container's existing non-root user, without a shell, TTY, privilege, user override, environment override, mount, device, capability, secret, or network change;
3. capture exact file bytes from stdout and reject command failure or stderr;
4. obtain exact in-container byte length and SHA-256 through a separate bounded exec;
5. compare both identities before creating the host destination; and
6. return a receipt for the accepted extraction.

The destination is never overwritten and is not created on failed validation. The `/state` tmpfs, runtime flags, source/package payloads, image construction, agent behavior, retrieval, decisions, policy, approval, executor, API/MCP authority, clean-clone contract, and no-export/no-push boundary remain unchanged.

## Consequences

The verifier can inspect tmpfs-backed real surfaces without weakening containment or requiring a shell or extra package in the image. The bounded in-memory stream is limited to the exact synthetic evidence allowlist and maximum size. Any mismatch, unexpected output, or unsupported source fails closed and remains evidence rather than being normalized into a pass.
