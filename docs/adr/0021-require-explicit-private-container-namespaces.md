# ADR 0021: Require explicit private container namespaces

- Status: accepted for BASELINE-0027 container-runtime-v6
- Date: 2026-08-12

## Context

Container-runtime-v5 built exact local image `sha256:96655a011b8ec8079fe23df988025fbb899575ae3b72ebbef30e92291cf0c5bf` twice and passed its corrected local-event window. Runtime security then stopped because the verifier treated every non-empty PID, IPC, UTS, or user-namespace mode as host sharing. Exact Docker inspect metadata showed empty PID, UTS, and userns modes but `IpcMode: private`.

Official Docker documentation at revision `c8c1ada37a8a3c598d0f8744d66f2dfbb780c145` defines `private` IPC as an owned private namespace, `host` as the host namespace, `container:<name-or-ID>` as another container's namespace, and `shareable` as private with later cross-container sharing allowed. The exact source identity, rights, fitness, and security review is preserved in `artifacts/verification/research-source-gate-baseline-0027-container-v6-namespaces.json`.

## Decision

Container-runtime-v6 changes only namespace-mode validation. On the exact verified builder, the verifier will require `PidMode`, `UTSMode`, and `UsernsMode` to be empty and `IpcMode` to be exactly `private`. It will fail closed on `host`, `shareable`, `container:<name-or-ID>`, an empty daemon-default IPC result, or any unknown representation.

The v5 event window, Dockerfile, build context, digest-pinned base, exporter, two payload layers, source/package evidence, non-root read-only capability-free networkless runtime, device and bind exclusions, real-surface gates, and no-export/no-push boundary remain exact.

## Consequences

- The verifier represents namespace isolation by exact allowed values instead of generic truthiness.
- V5 remains a failed and superseded result even though its observed container used private IPC.
- Requiring exact `private` is stricter than accepting Docker's daemon default, which may resolve to `private` or `shareable`.
- No incident-agent behavior, authority, dependency, secret, external asset, or real infrastructure changes.
