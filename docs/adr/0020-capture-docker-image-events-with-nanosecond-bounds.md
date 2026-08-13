# ADR 0020: Capture Docker image events with nanosecond bounds

- Status: accepted for BASELINE-0027 container-runtime-v5
- Date: 2026-08-12

## Context

Container-runtime-v4 built the exact same local image twice at `sha256:2d3f89d5807513719d958ae2b6c6f65e1cf391ea47c66aa6f084d0766d9039ee`. Both unique tags resolve to that ID, its local repository digest equals that ID, and the retained Docker event log contains local `create` and `tag` events for both builds. Runtime validation nevertheless stopped because the verifier converted its end time to integer seconds. Build B's tag occurred 0.162754846 seconds inside the same second used as `--until`, and Docker omitted it from that bounded query.

Official Docker documentation at revision `c8c1ada37a8a3c598d0f8744d66f2dfbb780c145` specifies Unix event bounds as `seconds[.nanoseconds]`, exposes local versus swarm scope, supports event filtering, and emits JSON Lines. The exact source identity, rights, fitness, and security review is preserved in `artifacts/verification/research-source-gate-baseline-0027-container-v5-events.json`.

## Decision

Container-runtime-v5 changes only local image-event capture. The verifier will use `time.time_ns()`, format both bounds as Unix seconds plus exactly nine fractional digits, and set the end bound one complete second after the final build returns. It will continue to require both current unique tags, the exact shared image ID, local scope, and only `create` or `tag` actions. A missing tag, remote scope, or `push` action remains a hard failure.

The v4 Dockerfile, build context, digest-pinned base, exporter, two payload layers, source/package evidence, non-root read-only networkless runtime, real-surface gates, and no-export/no-push boundary remain exact.

## Consequences

- The one-second event completion window may add about one second to a build verification.
- V4 remains a failed and superseded result even though its two images were byte-identical.
- The correction does not infer publication status from a missing event; it positively binds the local exporter command and complete local event window.
- No incident-agent behavior, authority, dependency, secret, external asset, or real infrastructure changes.
