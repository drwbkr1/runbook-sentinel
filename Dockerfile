FROM cgr.dev/chainguard/python@sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5
LABEL org.opencontainers.image.title="Runbook Sentinel"
LABEL org.opencontainers.image.description="Research-informed synthetic SRE incident-agent preview"
LABEL org.opencontainers.image.version="0.0.30"
LABEL org.opencontainers.image.source="https://github.com/drwbkr1/runbook-sentinel"
LABEL dev.runbook-sentinel.base.digest="sha256:69437de912cc3b5d36a2480b8fb0c3f658f151d8bc1978d19a6412be3a4983d5"
COPY --chown=65532:65532 dist/runbook-sentinel-0.0.30.pyz /opt/runbook-sentinel/runbook-sentinel.pyz
COPY --chown=65532:65532 artifacts/evaluations/latest.json /opt/runbook-sentinel/evaluation.json
USER 65532:65532
ENTRYPOINT ["/usr/bin/python", "/opt/runbook-sentinel/runbook-sentinel.pyz"]
CMD ["--help"]
