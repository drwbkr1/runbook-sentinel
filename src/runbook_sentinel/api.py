from __future__ import annotations

import html
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .errors import ApprovalError, NotFoundError, PolicyRejected, ReplayRejected, SentinelError
from .service import RunbookSentinel


CHECKPOINT = "baseline-0006"


class SentinelHTTPServer(ThreadingHTTPServer):
    def __init__(self, address, service: RunbookSentinel, evaluation_path: str | Path):
        super().__init__(address, SentinelHandler)
        self.service = service
        self.evaluation_path = Path(evaluation_path)


class SentinelHandler(BaseHTTPRequestHandler):
    server: SentinelHTTPServer

    def log_message(self, format, *args):
        return

    def _headers(self, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
        self.end_headers()

    def _json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8")
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 65536:
            raise ValueError("Request body is too large")
        return json.loads(self.rfile.read(length) or b"{}")

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
            body = self._body()
            if path == "/api/runs":
                self._json(HTTPStatus.CREATED, self.server.service.run_scenario(body["scenario_id"]))
            elif match := re.fullmatch(r"/api/proposals/([A-Za-z0-9_-]+)/approve", path):
                self._json(
                    HTTPStatus.CREATED,
                    self.server.service.approve(match.group(1), body.get("actor", ""), int(body.get("ttl_seconds", 300))),
                )
            elif match := re.fullmatch(r"/api/proposals/([A-Za-z0-9_-]+)/execute", path):
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
        elif isinstance(error, (ReplayRejected, ApprovalError, PolicyRejected)):
            status = HTTPStatus.CONFLICT
        elif isinstance(error, (ValueError, KeyError, json.JSONDecodeError)):
            status = HTTPStatus.BAD_REQUEST
        elif isinstance(error, SentinelError):
            status = HTTPStatus.UNPROCESSABLE_ENTITY
        else:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
        self._json(status, {"error": type(error).__name__, "message": str(error)})

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
        trajectory_display = f"{trajectory_exact:.1f}" if isinstance(trajectory_exact, (int, float)) else "not run"
        terminal_display = f"{terminal_exact:.1f}" if isinstance(terminal_exact, (int, float)) else "not run"
        condition_display = (
            f"{condition_coverage:.1f}"
            if isinstance(condition_coverage, (int, float))
            else "not run"
        )
        rows = "".join(
            f"<tr><td>{html.escape(item['id'])}</td><td>{html.escape(item['scenario_id'])}</td><td>{html.escape(item['status'])}</td></tr>"
            for item in incidents
        ) or "<tr><td colspan='3'>No incidents have been run in this process.</td></tr>"
        return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Runbook Sentinel</title><style>
:root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background:#08111f; color:#e8f0f7; }}
body {{ margin:0; }} main {{ max-width:1080px; margin:auto; padding:40px 24px; }}
.eyebrow {{ color:#75d7c6; letter-spacing:.12em; text-transform:uppercase; font-size:.78rem; }}
h1 {{ font-size:clamp(2rem,6vw,4.5rem); margin:.25rem 0; }}
.promise {{ color:#aebfd0; max-width:760px; font-size:1.15rem; line-height:1.6; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:16px; margin:32px 0; }}
.card {{ background:#101d2d; border:1px solid #21354b; border-radius:14px; padding:20px; }}
.value {{ font-size:1.8rem; color:#75d7c6; }} table {{ width:100%; border-collapse:collapse; }}
th,td {{ text-align:left; padding:12px; border-bottom:1px solid #21354b; }} .boundary {{ color:#ffcf70; }}
</style></head><body><main>
<div class="eyebrow">Baseline 0006 - synthetic SRE only</div><h1>Runbook Sentinel</h1>
<p class="promise">Evidence can be incomplete, stale, or hostile. The agent may diagnose, request evidence, propose a bounded action, or abstain. It never executes.</p>
<section class="grid">
<div class="card"><div>Evaluation</div><div class="value">{html.escape(disposition)}</div></div>
<div class="card"><div>Agent</div><div class="value">deterministic v2</div></div>
<div class="card"><div>Decision context</div><div class="value">evidence only</div></div>
<div class="card"><div>Tool trajectory exact</div><div class="value">{trajectory_display}</div></div>
<div class="card"><div>Terminal state exact</div><div class="value">{terminal_display}</div></div>
<div class="card"><div>Evidence condition coverage</div><div class="value">{condition_display}</div></div>
<div class="card"><div>Execution boundary</div><div class="value boundary">human approval</div></div>
<div class="card"><div>Real infrastructure</div><div class="value boundary">disconnected</div></div>
</section>
<section class="card"><h2>Persisted incidents</h2><table><thead><tr><th>Incident</th><th>Scenario</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></section>
</main></body></html>"""


def create_server(host: str, port: int, db_path: str, trace_path: str, evaluation_path: str) -> SentinelHTTPServer:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Runbook Sentinel permits loopback HTTP binding only")
    service = RunbookSentinel(db_path, trace_path)
    return SentinelHTTPServer((host, port), service, evaluation_path)
