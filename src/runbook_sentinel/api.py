from __future__ import annotations

import html
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .errors import ApprovalError, NotFoundError, OperatorAuthenticationError, PolicyRejected, ReplayRejected, SentinelError
from .operator_auth import AUTHENTICATION_CHALLENGE, OperatorAuthenticator
from .service import DEFAULT_APPROVAL_TTL_SECONDS, RunbookSentinel
from .telemetry import live_trace_anchor_path


CHECKPOINT = "baseline-0033"


class SentinelHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        address,
        service: RunbookSentinel,
        evaluation_path: str | Path,
        operator_authenticator: OperatorAuthenticator,
    ):
        super().__init__(address, SentinelHandler)
        self.service = service
        self.evaluation_path = Path(evaluation_path)
        self.operator_authenticator = operator_authenticator


class SentinelHandler(BaseHTTPRequestHandler):
    server: SentinelHTTPServer

    def log_message(self, format, *args):
        return

    def _headers(
        self, status: int, content_type: str, extra_headers: dict[str, str] | None = None
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()

    def _json(
        self,
        status: int,
        payload: dict | list,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", extra_headers)
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 65536:
            raise ValueError("Request body is too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def _discard_bounded_body_without_parsing(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return
        if 0 < length <= 65536:
            self.rfile.read(length)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/health":
                self._json(HTTPStatus.OK, {"status": "ok", "checkpoint": CHECKPOINT})
            elif path == "/api/scenarios":
                self._json(HTTPStatus.OK, self.server.service.list_scenarios())
            elif path == "/api/incidents":
                self._json(HTTPStatus.OK, self.server.service.list_incidents())
            elif path == "/api/evaluation":
                if self.server.evaluation_path.exists():
                    self._json(HTTPStatus.OK, json.loads(self.server.evaluation_path.read_text(encoding="utf-8")))
                else:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "evaluation_not_found"})
            elif match := re.fullmatch(r"/api/incidents/([A-Za-z0-9_-]+)", path):
                self._json(HTTPStatus.OK, self.server.service.get_incident(match.group(1)))
            elif path in {"/", "/dashboard"}:
                body = self._dashboard().encode("utf-8")
                self._headers(HTTPStatus.OK, "text/html; charset=utf-8")
                self.wfile.write(body)
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except Exception as error:
            self._error(error)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/runs":
                body = self._body()
                self._json(HTTPStatus.CREATED, self.server.service.run_scenario(body["scenario_id"]))
            elif match := re.fullmatch(r"/api/proposals/([A-Za-z0-9_-]+)/approve", path):
                try:
                    operator = self.server.operator_authenticator.authenticate(
                        self.headers.get_all("Authorization", [])
                    )
                except OperatorAuthenticationError:
                    self._discard_bounded_body_without_parsing()
                    raise
                body = self._body()
                if "actor" in body:
                    raise ValueError("Approval request must not contain actor")
                self._json(
                    HTTPStatus.CREATED,
                    self.server.service.approve(
                        match.group(1),
                        operator,
                        body.get("ttl_seconds", DEFAULT_APPROVAL_TTL_SECONDS),
                    ),
                )
            elif match := re.fullmatch(r"/api/proposals/([A-Za-z0-9_-]+)/execute", path):
                body = self._body()
                self._json(
                    HTTPStatus.OK,
                    self.server.service.execute(
                        match.group(1),
                        body.get("approval_token", ""),
                        body.get("idempotency_key", ""),
                    ),
                )
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except Exception as error:
            self._error(error)

    def _error(self, error: Exception) -> None:
        if isinstance(error, NotFoundError):
            status = HTTPStatus.NOT_FOUND
        elif isinstance(error, OperatorAuthenticationError):
            status = HTTPStatus.UNAUTHORIZED
        elif isinstance(error, (ReplayRejected, ApprovalError, PolicyRejected)):
            status = HTTPStatus.CONFLICT
        elif isinstance(error, (ValueError, KeyError, json.JSONDecodeError)):
            status = HTTPStatus.BAD_REQUEST
        elif isinstance(error, SentinelError):
            status = HTTPStatus.UNPROCESSABLE_ENTITY
        else:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
        extra_headers = (
            {"WWW-Authenticate": AUTHENTICATION_CHALLENGE}
            if isinstance(error, OperatorAuthenticationError)
            else None
        )
        self._json(
            status,
            {"error": type(error).__name__, "message": str(error)},
            extra_headers,
        )

    def _dashboard(self) -> str:
        incidents = self.server.service.list_incidents(10)
        evaluation = None
        if self.server.evaluation_path.exists():
            evaluation = json.loads(self.server.evaluation_path.read_text(encoding="utf-8"))
        disposition = evaluation["gates"]["baseline_disposition"] if evaluation else "not run"
        metrics = evaluation.get("metrics", {}) if evaluation else {}
        trajectory_exact = metrics.get("tool_trajectory", {}).get("exact_match")
        terminal_exact = metrics.get("terminal_state", {}).get("exact_match_rate")
        condition_coverage = metrics.get("coverage", {}).get(
            "evidence_condition_split_coverage"
        )
        topology_split_coverage = metrics.get("coverage", {}).get(
            "topology_split_coverage"
        )
        action_split_coverage = metrics.get("coverage", {}).get(
            "action_split_coverage"
        )
        adversarial_topology_split_coverage = metrics.get("coverage", {}).get(
            "adversarial_topology_split_coverage"
        )
        adversarial_action_split_coverage = metrics.get("coverage", {}).get(
            "adversarial_action_split_coverage"
        )
        adversarial_outcome_split_coverage = metrics.get("coverage", {}).get(
            "adversarial_outcome_split_coverage"
        )
        adversarial_condition_outcome_split_coverage = metrics.get(
            "coverage", {}
        ).get("adversarial_condition_outcome_split_coverage")
        adversarial_domain_outcome_split_coverage = metrics.get(
            "coverage", {}
        ).get("adversarial_domain_outcome_split_coverage")
        adversarial_exposure_stage_outcome_split_coverage = metrics.get(
            "coverage", {}
        ).get("adversarial_exposure_stage_outcome_split_coverage")
        adversarial_retrieval_stage_outcome_split_coverage = metrics.get(
            "coverage", {}
        ).get("adversarial_retrieval_stage_outcome_split_coverage")
        guidance_retrieved_filtered_attempt_count = metrics.get(
            "coverage", {}
        ).get("guidance_retrieved_filtered_attempt_count")
        guidance_not_retrieved_attempt_count = metrics.get("coverage", {}).get(
            "guidance_not_retrieved_attempt_count"
        )
        retrieval_quality = metrics.get("retrieval_quality", {})
        expected_document_share = retrieval_quality.get("expected_evidence", {}).get(
            "expected_document_share_mean"
        )
        extra_document_attempt_rate = retrieval_quality.get(
            "expected_evidence", {}
        ).get("attempts_with_extra_documents_rate")
        guidance_rank_buckets = (
            retrieval_quality.get("declared_attack_exposure", {})
            .get("guidance", {})
            .get("first_rank_attempt_count")
        )
        inband_rank_buckets = (
            retrieval_quality.get("declared_attack_exposure", {})
            .get("inband", {})
            .get("first_rank_attempt_count")
        )
        conditional_policy_compliance = retrieval_quality.get(
            "declared_attack_exposure", {}
        ).get("populated_bucket_policy_compliance_rate")
        relation_exact = metrics.get("behavioral_relations", {}).get("exact_match_rate")
        stress_recall = metrics.get("retrieval_stress", {}).get(
            "expected_project_evidence_recall_at_4"
        )
        fresh_evidence_recall = metrics.get("stale_evidence_stress", {}).get(
            "fresh_project_evidence_recall_at_4"
        )
        stale_identity_retention = metrics.get("stale_payload_projection", {}).get(
            "stale_identity_retention_rate"
        )
        stale_payload_exposure = metrics.get("stale_payload_projection", {}).get(
            "stale_payload_exposure_rate"
        )
        approval_lifetime_exact = metrics.get("approval_lifetime", {}).get(
            "exact_match_rate"
        )
        idempotency_authorization_exact = metrics.get(
            "idempotency_authorization", {}
        ).get("exact_match_rate")
        operator_authentication_exact = (
            metrics.get("operator_authentication", {})
            .get("metrics", {})
            .get("exact_match_rate")
        )
        trace_integrity_exact = (
            metrics.get("telemetry_integrity", {})
            .get("contract_evaluation", {})
            .get("metrics", {})
            .get("exact_match_rate")
        )
        live_trace_anchor_exact = metrics.get("live_trace_endpoint_anchor", {}).get(
            "metrics", {}
        ).get("exact_match_rate")
        trajectory_display = f"{trajectory_exact:.1f}" if isinstance(trajectory_exact, (int, float)) else "not run"
        terminal_display = f"{terminal_exact:.1f}" if isinstance(terminal_exact, (int, float)) else "not run"
        condition_display = (
            f"{condition_coverage:.1f}"
            if isinstance(condition_coverage, (int, float))
            else "not run"
        )
        topology_split_display = (
            f"{topology_split_coverage:.1f}"
            if isinstance(topology_split_coverage, (int, float))
            else "not run"
        )
        action_split_display = (
            f"{action_split_coverage:.1f}"
            if isinstance(action_split_coverage, (int, float))
            else "not run"
        )
        adversarial_topology_split_display = (
            f"{adversarial_topology_split_coverage:.1f}"
            if isinstance(adversarial_topology_split_coverage, (int, float))
            else "not run"
        )
        adversarial_action_split_display = (
            f"{adversarial_action_split_coverage:.1f}"
            if isinstance(adversarial_action_split_coverage, (int, float))
            else "not run"
        )
        adversarial_outcome_split_display = (
            f"{adversarial_outcome_split_coverage:.1f}"
            if isinstance(adversarial_outcome_split_coverage, (int, float))
            else "not run"
        )
        adversarial_condition_outcome_split_display = (
            f"{adversarial_condition_outcome_split_coverage:.1f}"
            if isinstance(
                adversarial_condition_outcome_split_coverage, (int, float)
            )
            else "not run"
        )
        adversarial_domain_outcome_split_display = (
            f"{adversarial_domain_outcome_split_coverage:.1f}"
            if isinstance(adversarial_domain_outcome_split_coverage, (int, float))
            else "not run"
        )
        adversarial_exposure_stage_outcome_split_display = (
            f"{adversarial_exposure_stage_outcome_split_coverage:.1f}"
            if isinstance(
                adversarial_exposure_stage_outcome_split_coverage, (int, float)
            )
            else "not run"
        )
        adversarial_retrieval_stage_outcome_split_display = (
            f"{adversarial_retrieval_stage_outcome_split_coverage:.1f}"
            if isinstance(
                adversarial_retrieval_stage_outcome_split_coverage, (int, float)
            )
            else "not run"
        )
        guidance_retrieved_filtered_attempt_display = (
            str(guidance_retrieved_filtered_attempt_count)
            if isinstance(guidance_retrieved_filtered_attempt_count, int)
            and not isinstance(guidance_retrieved_filtered_attempt_count, bool)
            else "not run"
        )
        guidance_not_retrieved_attempt_display = (
            str(guidance_not_retrieved_attempt_count)
            if isinstance(guidance_not_retrieved_attempt_count, int)
            and not isinstance(guidance_not_retrieved_attempt_count, bool)
            else "not run"
        )
        expected_document_share_display = (
            f"{expected_document_share:.3f}"
            if isinstance(expected_document_share, (int, float))
            else "not run"
        )
        extra_document_attempt_rate_display = (
            f"{extra_document_attempt_rate:.3f}"
            if isinstance(extra_document_attempt_rate, (int, float))
            else "not run"
        )

        def rank_bucket_display(value: object) -> str:
            if not isinstance(value, dict) or any(
                not isinstance(value.get(bucket), int)
                or isinstance(value.get(bucket), bool)
                for bucket in ("not_retrieved", "rank_1", "rank_2", "rank_3_4")
            ):
                return "not run"
            return (
                f"NR {value['not_retrieved']} / R1 {value['rank_1']} / "
                f"R2 {value['rank_2']} / R3-4 {value['rank_3_4']}"
            )

        guidance_rank_display = rank_bucket_display(guidance_rank_buckets)
        inband_rank_display = rank_bucket_display(inband_rank_buckets)
        conditional_policy_display = (
            f"{conditional_policy_compliance:.1f}"
            if isinstance(conditional_policy_compliance, (int, float))
            else "not run"
        )
        relation_display = (
            f"{relation_exact:.1f}"
            if isinstance(relation_exact, (int, float))
            else "not run"
        )
        stress_display = (
            f"{stress_recall:.1f}"
            if isinstance(stress_recall, (int, float))
            else "not run"
        )
        fresh_evidence_display = (
            f"{fresh_evidence_recall:.1f}"
            if isinstance(fresh_evidence_recall, (int, float))
            else "not run"
        )
        stale_identity_display = (
            f"{stale_identity_retention:.1f}"
            if isinstance(stale_identity_retention, (int, float))
            else "not run"
        )
        stale_payload_display = (
            f"{stale_payload_exposure:.1f}"
            if isinstance(stale_payload_exposure, (int, float))
            else "not run"
        )
        approval_lifetime_display = (
            f"{approval_lifetime_exact:.1f}"
            if isinstance(approval_lifetime_exact, (int, float))
            else "not run"
        )
        idempotency_authorization_display = (
            f"{idempotency_authorization_exact:.1f}"
            if isinstance(idempotency_authorization_exact, (int, float))
            else "not run"
        )
        operator_authentication_display = (
            f"{operator_authentication_exact:.1f}"
            if isinstance(operator_authentication_exact, (int, float))
            else "not run"
        )
        trace_integrity_display = (
            f"{trace_integrity_exact:.1f}"
            if isinstance(trace_integrity_exact, (int, float))
            else "not run"
        )
        live_trace_anchor_display = (
            f"{live_trace_anchor_exact:.1f}"
            if isinstance(live_trace_anchor_exact, (int, float))
            else "not run"
        )
        rows = "".join(
            f"<tr><td>{html.escape(item['id'])}</td><td>{html.escape(item['scenario_id'])}</td><td>{html.escape(item['status'])}</td></tr>"
            for item in incidents
        ) or "<tr><td colspan='3'>No incidents have been run in this process.</td></tr>"
        checkpoint_display = html.escape(CHECKPOINT.removeprefix("baseline-"))
        return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Runbook Sentinel</title><style>
:root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background:#08111f; color:#e8f0f7; }}
body {{ margin:0; }} main {{ max-width:1260px; margin:auto; padding:8px 24px; }}
.eyebrow {{ color:#75d7c6; letter-spacing:.12em; text-transform:uppercase; font-size:.78rem; }}
h1 {{ font-size:clamp(2rem,6vw,3.5rem); line-height:1.05; margin:.15rem 0; }}
.promise {{ color:#aebfd0; max-width:760px; font-size:1rem; line-height:1.3; margin:.5rem 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(165px,1fr)); gap:7px; margin:9px 0; }}
.card {{ background:#101d2d; border:1px solid #21354b; border-radius:10px; padding:8px; }}
.value {{ font-size:1.25rem; line-height:1.25; color:#75d7c6; }} table {{ width:100%; border-collapse:collapse; }}
h2 {{ margin:.4rem 0; }} th,td {{ text-align:left; padding:8px 12px; border-bottom:1px solid #21354b; }} .boundary {{ color:#ffcf70; }}
</style></head><body><main>
<div class="eyebrow">Baseline {checkpoint_display} - synthetic SRE only</div><h1>Runbook Sentinel</h1>
<p class="promise">Evidence can be incomplete, stale, or hostile. The agent may diagnose, request evidence, propose a bounded action, or abstain. It never executes.</p>
<section class="grid">
<div class="card"><div>Evaluation</div><div class="value">{html.escape(disposition)}</div></div>
<div class="card"><div>Agent</div><div class="value">deterministic v2</div></div>
<div class="card"><div>Decision context</div><div class="value">fresh content / stale metadata v3</div></div>
<div class="card"><div>Retriever</div><div class="value">freshness priority v3</div></div>
<div class="card"><div>Tool trajectory exact</div><div class="value">{trajectory_display}</div></div>
<div class="card"><div>Terminal state exact</div><div class="value">{terminal_display}</div></div>
<div class="card"><div>Evidence condition coverage</div><div class="value">{condition_display}</div></div>
<div class="card"><div>Topology split coverage</div><div class="value">{topology_split_display}</div></div>
<div class="card"><div>Action split coverage</div><div class="value">{action_split_display}</div></div>
<div class="card"><div>Adversarial topology split</div><div class="value">{adversarial_topology_split_display}</div></div>
<div class="card"><div>Adversarial action split</div><div class="value">{adversarial_action_split_display}</div></div>
<div class="card"><div>Adversarial outcome split</div><div class="value">{adversarial_outcome_split_display}</div></div>
<div class="card"><div>Adversarial condition/outcome split</div><div class="value">{adversarial_condition_outcome_split_display}</div></div>
<div class="card"><div>Adversarial domain/outcome split</div><div class="value">{adversarial_domain_outcome_split_display}</div></div>
<div class="card"><div>Adversarial exposure-stage/outcome split</div><div class="value">{adversarial_exposure_stage_outcome_split_display}</div></div>
<div class="card"><div>Adversarial retrieval-stage/outcome split</div><div class="value">{adversarial_retrieval_stage_outcome_split_display}</div></div>
<div class="card"><div>Hostile guidance retrieved then filtered</div><div class="value">{guidance_retrieved_filtered_attempt_display} attempts</div></div>
<div class="card"><div>Hostile guidance never retrieved</div><div class="value">{guidance_not_retrieved_attempt_display} attempts</div></div>
<div class="card"><div>Expected-document share</div><div class="value">{expected_document_share_display}</div></div>
<div class="card"><div>Attempts with extra documents</div><div class="value">{extra_document_attempt_rate_display}</div></div>
<div class="card"><div>Guidance first-rank buckets</div><div class="value">{guidance_rank_display}</div></div>
<div class="card"><div>In-band first-rank buckets</div><div class="value">{inband_rank_display}</div></div>
<div class="card"><div>Rank-conditioned policy compliance</div><div class="value">{conditional_policy_display}</div></div>
<div class="card"><div>Behavioral relation exact</div><div class="value">{relation_display}</div></div>
<div class="card"><div>Guidance stress recall</div><div class="value">{stress_display}</div></div>
<div class="card"><div>Fresh evidence recall</div><div class="value">{fresh_evidence_display}</div></div>
<div class="card"><div>Stale identity retained</div><div class="value">{stale_identity_display}</div></div>
<div class="card"><div>Stale payload exposure</div><div class="value">{stale_payload_display}</div></div>
<div class="card"><div>Approval lifetime exact</div><div class="value">{approval_lifetime_display}</div></div>
<div class="card"><div>Cached result authorization</div><div class="value">{idempotency_authorization_display}</div></div>
<div class="card"><div>Operator authentication</div><div class="value">{operator_authentication_display}</div></div>
<div class="card"><div>Trace integrity</div><div class="value">{trace_integrity_display}</div></div>
<div class="card"><div>Live trace endpoint</div><div class="value">{live_trace_anchor_display}</div></div>
<div class="card"><div>Execution boundary</div><div class="value boundary">authenticated external operator</div></div>
<div class="card"><div>Real infrastructure</div><div class="value boundary">disconnected</div></div>
</section>
<section class="card"><h2>Persisted incidents</h2><table><thead><tr><th>Incident</th><th>Scenario</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></section>
</main></body></html>"""


def create_server(
    host: str,
    port: int,
    db_path: str,
    trace_path: str,
    evaluation_path: str,
    operator_capability: str,
) -> SentinelHTTPServer:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Runbook Sentinel permits loopback HTTP binding only")
    service = RunbookSentinel(
        db_path,
        trace_path,
        str(live_trace_anchor_path(trace_path)),
    )
    authenticator = OperatorAuthenticator(operator_capability)
    return SentinelHTTPServer((host, port), service, evaluation_path, authenticator)
