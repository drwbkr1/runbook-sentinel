FROM cgr.dev/chainguard/python@sha256:1f6779775c9f466890da563e411cb677045a6c20b6a65160eefad1deffb5012c
LABEL org.opencontainers.image.title="Runbook Sentinel"
LABEL org.opencontainers.image.description="Research-informed synthetic SRE incident-agent preview"
LABEL org.opencontainers.image.version="0.0.32"
LABEL org.opencontainers.image.source="https://github.com/drwbkr1/runbook-sentinel"
LABEL dev.runbook-sentinel.base.digest="sha256:1f6779775c9f466890da563e411cb677045a6c20b6a65160eefad1deffb5012c"
COPY --chown=65532:65532 dist/runbook-sentinel-0.0.32.pyz /opt/runbook-sentinel/runbook-sentinel.pyz
COPY --chown=65532:65532 artifacts/evaluations/latest.json /opt/runbook-sentinel/evaluation.json
USER 65532:65532
ENTRYPOINT ["/usr/bin/python", "/opt/runbook-sentinel/runbook-sentinel.pyz"]
CMD ["--help"]
