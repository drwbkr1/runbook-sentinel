# ADR 0017: digest-pinned local container without image publication

- Status: accepted for BASELINE-0027 implementation
- Date: 2026-08-12

## Context

Runbook Sentinel already ships a deterministic, dependency-free Python zipapp and verifies source, package, MCP, API, approval, executor, persistence, telemetry, dashboard, clean-clone, and public-release surfaces. The active product contract also requires container verification when Docker is available. Docker is now live, but three earlier official Python candidates remain excluded by their source-security gate and v0.0.26 makes no container claim.

A current eight-criterion review admits one exact Chainguard Free Python OCI index for anonymous local extension. Its selected linux/amd64 manifest supplies Python 3.14.7, defaults to non-root UID 65532, and has no shell or package manager. A current local scan observes zero known findings across 54 packages. The source is external and drift-prone, so mutable tags and timeless safety claims are unacceptable.

## Decision

Build the v0.0.27 zipapp into a project-authored image using only the reviewed OCI index digest. Freeze the Dockerfile and a three-file context before implementation. Require two identical builds, exact base layers, and only two added payloads: the zipapp and accepted evaluation report.

Run every container with a read-only root filesystem, UID/GID 65532, all capabilities dropped, no-new-privileges, no privileged mode, host namespace, device, writable host path, secret, model artifact, or real connector. CLI, evaluation, and MCP run without a network. The loopback API may use only a dedicated internal Docker network with no external egress. Verify the full evaluation, bounded MCP, authenticated approval/executor flow, persisted state, anchored telemetry, rendered dashboard, candidate scan, and clean-clone build identity.

Publish the Dockerfile, contract, verifier, and evidence with the normal source and zipapp release, but do not export, push, publish, or redistribute container image bytes.

## Consequences

- Docker users gain a reproducible, inspectable local runtime path without a new application dependency or authority surface.
- The external base remains a release input that must be re-gated when its digest changes or current security evidence becomes stale.
- No registry delivery convenience is claimed; users build locally from the public tag.
- A passing local container remains synthetic research-preview evidence, not production readiness or universal safety.
- The two-case retrieval-stage observability gap measured during orientation remains open for a later checkpoint.
