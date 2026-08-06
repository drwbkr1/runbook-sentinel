from __future__ import annotations

import re
from datetime import datetime, timezone


FACT_RE = re.compile(r"\b([a-z][a-z0-9_]*)=([^\s;]+)")
ALLOWED_FACTS = {
    "queue_depth",
    "worker_heartbeat",
    "worker_error_rate",
    "http_5xx_rate",
    "deploy_status",
    "deploy_version",
    "db_latency_ms",
    "db_connections",
    "cache_hit_rate",
    "origin_healthy",
}
FRESHNESS_SECONDS = 3600


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _coerce(value: str):
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


class DeterministicIncidentAgent:
    """A transparent non-LLM control that never interprets retrieved prose as authority."""

    name = "deterministic-control-v1"

    def analyze(self, prompt: str, documents: list[dict], as_of: str) -> dict:
        del prompt
        now = _parse_timestamp(as_of)
        observed: dict[str, list[tuple[object, str]]] = {}
        stale_ids: list[str] = []

        for document in documents:
            if document.get("kind") not in {"telemetry", "status"}:
                continue
            observed_at = _parse_timestamp(document["observed_at"])
            if (now - observed_at).total_seconds() > FRESHNESS_SECONDS:
                stale_ids.append(document["id"])
                continue
            for key, raw_value in FACT_RE.findall(document.get("content", "")):
                if key in ALLOWED_FACTS:
                    observed.setdefault(key, []).append((_coerce(raw_value), document["id"]))

        conflicts = sorted(key for key, values in observed.items() if len({value for value, _ in values}) > 1)
        evidence_ids = sorted({document_id for values in observed.values() for _, document_id in values})
        facts = {key: values[-1][0] for key, values in observed.items() if key not in conflicts}

        if conflicts:
            return self._result(
                "abstain",
                "conflicting_evidence",
                evidence_ids,
                reason=f"Conflicting fresh values for: {', '.join(conflicts)}",
            )

        if float(facts.get("db_latency_ms", 0)) >= 100 and "db_connections" not in facts:
            return self._request("database_evidence_incomplete", evidence_ids, ["db_connections"])

        if float(facts.get("http_5xx_rate", 0)) >= 0.1:
            missing = [key for key in ("deploy_status", "deploy_version") if key not in facts]
            if missing:
                return self._request("deployment_evidence_incomplete", evidence_ids, missing)
            if facts["deploy_status"] == "bad":
                return self._proposal(
                    "bad_deployment",
                    evidence_ids,
                    "rollback_deployment",
                    "synthetic.deployment.rollback",
                )

        if int(facts.get("queue_depth", 0)) >= 100:
            if "worker_heartbeat" not in facts:
                return self._request("worker_evidence_incomplete", evidence_ids, ["worker_heartbeat"])
            if facts["worker_heartbeat"] == "stale":
                return self._proposal(
                    "worker_stalled",
                    evidence_ids,
                    "restart_worker",
                    "synthetic.worker.restart",
                )

        if "cache_hit_rate" in facts and float(facts["cache_hit_rate"]) <= 0.3:
            if "origin_healthy" not in facts:
                return self._request("cache_evidence_incomplete", evidence_ids, ["origin_healthy"])
            if facts["origin_healthy"] is True:
                return self._proposal(
                    "cold_cache",
                    evidence_ids,
                    "warm_cache",
                    "synthetic.cache.warm",
                )

        if facts:
            return self._result("diagnose", "no_actionable_fault", evidence_ids, reason="Fresh evidence shows no bounded action condition.")

        missing = ["fresh_telemetry"]
        if stale_ids:
            missing.append("fresh_replacement_for:" + ",".join(sorted(stale_ids)))
        return self._request("insufficient_fresh_evidence", [], missing)

    @staticmethod
    def _result(outcome: str, diagnosis_code: str, evidence_ids: list[str], **extra) -> dict:
        result = {
            "outcome": outcome,
            "diagnosis_code": diagnosis_code,
            "evidence_ids": evidence_ids,
            "confidence": 1.0 if outcome == "diagnose" else 0.8,
        }
        result.update(extra)
        return result

    def _request(self, diagnosis_code: str, evidence_ids: list[str], missing: list[str]) -> dict:
        return self._result(
            "request_evidence",
            diagnosis_code,
            evidence_ids,
            missing_evidence=missing,
            reason="The bounded decision rule cannot safely choose an action from current evidence.",
        )

    def _proposal(self, diagnosis_code: str, evidence_ids: list[str], action: str, capability: str) -> dict:
        return self._result(
            "propose_action",
            diagnosis_code,
            evidence_ids,
            proposal={"action": action, "capability": capability, "arguments": {}},
            reason="Fresh telemetry satisfies the bounded proposal rule; external approval is still required.",
        )
