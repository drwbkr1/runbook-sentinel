from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from time import perf_counter
from uuid import uuid4

from .agent import DeterministicIncidentAgent
from .catalog import load_scenarios, scenario_by_id
from .errors import ApprovalError, NotFoundError, ReplayRejected
from .policy import action_spec, apply_action, postconditions_hold, validate_proposal
from .retrieval import DEFAULT_DECISION_CONTEXT, LexicalRetriever, select_decision_documents
from .storage import Storage
from .telemetry import TraceWriter, utc_now


def _canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class RunbookSentinel:
    def __init__(
        self,
        db_path: str,
        trace_path: str | None = None,
        decision_context_configuration: str = DEFAULT_DECISION_CONTEXT,
        agent=None,
    ):
        self.storage = Storage(db_path)
        self.traces = TraceWriter(trace_path)
        self.retriever = LexicalRetriever()
        self.agent = agent or DeterministicIncidentAgent()
        self.decision_context_configuration = decision_context_configuration

    def list_scenarios(self) -> list[dict]:
        return [
            {
                "id": item["id"],
                "split": item["split"],
                "domain": item["domain"],
                "adversarial": item["adversarial"],
                "prompt": item["prompt"],
            }
            for item in load_scenarios()
        ]

    def run_scenario(self, scenario_id: str) -> dict:
        try:
            scenario = scenario_by_id(scenario_id)
        except KeyError as error:
            raise NotFoundError(f"Unknown scenario: {scenario_id}") from error

        started = perf_counter()
        incident_id = "inc-" + uuid4().hex
        run_id = "run-" + uuid4().hex
        now = utc_now()
        with self.storage.connect() as connection:
            connection.execute(
                "INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?)",
                (incident_id, scenario_id, "open", _canonical(scenario["initial_state"]), now, now),
            )

        retrieved = self.retriever.retrieve(scenario["prompt"], scenario["documents"])
        decision_documents = select_decision_documents(self.decision_context_configuration, retrieved)
        decision_ids = {document["id"] for document in decision_documents}
        guidance_documents = [document for document in retrieved if document["id"] not in decision_ids]
        result = self.agent.analyze(scenario["prompt"], decision_documents, scenario["as_of"])
        result.update(
            {
                "incident_id": incident_id,
                "run_id": run_id,
                "scenario_id": scenario_id,
                "retriever": self.retriever.name,
                "agent": self.agent.name,
                "decision_context_configuration": self.decision_context_configuration,
                "retrieved_document_ids": [document["id"] for document in retrieved],
                "decision_document_ids": [document["id"] for document in decision_documents],
                "guidance_document_ids": [document["id"] for document in guidance_documents],
            }
        )

        if result["outcome"] == "propose_action":
            proposal = self._persist_proposal(incident_id, result["proposal"])
            result["proposal"] = proposal

        latency_ms = (perf_counter() - started) * 1000
        result["latency_ms"] = round(latency_ms, 3)
        with self.storage.connect() as connection:
            connection.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?)",
                (run_id, incident_id, _canonical(result), latency_ms, utc_now()),
            )
        self._audit("diagnosis.completed", run_id, {"incident_id": incident_id, "outcome": result["outcome"]})
        trace_attributes = {
            "run.id": run_id,
            "incident.id": incident_id,
            "scenario.id": scenario_id,
            "retrieval.operation": self.retriever.name,
            "retrieval.decision_context": self.decision_context_configuration,
            "retrieval.document_count": len(retrieved),
            "retrieval.decision_document_count": len(decision_documents),
            "agent.operation": self.agent.name,
            "sentinel.outcome": result["outcome"],
            "latency.ms": result["latency_ms"],
        }
        model_metadata = result.get("model_metadata")
        if model_metadata:
            trace_attributes.update(
                {
                    "gen_ai.provider.name": model_metadata["provider"],
                    "gen_ai.request.model": model_metadata["model"],
                    "gen_ai.response.model_manifest_sha256": model_metadata["model_manifest_sha256"],
                    "gen_ai.operation.name": model_metadata["contract_id"],
                    "gen_ai.request.system_prompt_sha256": model_metadata["system_prompt_sha256"],
                    "gen_ai.request.payload_sha256": model_metadata["request_payload_sha256"],
                    "gen_ai.response.raw_output_sha256": model_metadata["raw_output_sha256"],
                    "gen_ai.response.parse_status": model_metadata["parse_status"],
                    "gen_ai.usage.input_tokens": model_metadata["prompt_tokens"],
                    "gen_ai.usage.output_tokens": model_metadata["completion_tokens"],
                    "gen_ai.response.total_duration_ns": model_metadata["total_duration_ns"],
                    "gen_ai.response.load_duration_ns": model_metadata["load_duration_ns"],
                }
            )
        self.traces.write("sentinel.run", trace_attributes)
        return result

    def _persist_proposal(self, incident_id: str, model_proposal: dict) -> dict:
        spec = validate_proposal(model_proposal)
        proposal_id = "prop-" + uuid4().hex
        proposal = {
            "id": proposal_id,
            "incident_id": incident_id,
            "action": model_proposal["action"],
            "capability": model_proposal["capability"],
            "arguments": model_proposal.get("arguments", {}),
            "preconditions": spec["preconditions"],
            "postconditions": spec["postconditions"],
        }
        action_hash = _hash(_canonical(proposal))
        now = utc_now()
        with self.storage.connect() as connection:
            connection.execute(
                "INSERT INTO proposals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    proposal_id,
                    incident_id,
                    proposal["action"],
                    proposal["capability"],
                    _canonical(proposal["arguments"]),
                    _canonical({"items": proposal["preconditions"]}),
                    _canonical({"items": proposal["postconditions"]}),
                    action_hash,
                    "pending",
                    now,
                    now,
                ),
            )
        proposal.update({"action_hash": action_hash, "status": "pending"})
        return proposal

    def get_incident(self, incident_id: str) -> dict:
        with self.storage.connect() as connection:
            row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if not row:
            raise NotFoundError(f"Unknown incident: {incident_id}")
        return {"id": row["id"], "scenario_id": row["scenario_id"], "status": row["status"], "state": json.loads(row["state_json"])}

    def list_incidents(self, limit: int = 20) -> list[dict]:
        with self.storage.connect() as connection:
            rows = connection.execute("SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [
            {"id": row["id"], "scenario_id": row["scenario_id"], "status": row["status"], "state": json.loads(row["state_json"])}
            for row in rows
        ]

    def approve(self, proposal_id: str, actor: str, ttl_seconds: int = 300) -> dict:
        if not actor.strip():
            raise ApprovalError("Approval actor is required")
        with self.storage.connect() as connection:
            proposal = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            if not proposal:
                raise NotFoundError(f"Unknown proposal: {proposal_id}")
            if proposal["status"] != "pending":
                raise ApprovalError(f"Proposal is not pending: {proposal['status']}")
            raw_token = secrets.token_urlsafe(32)
            nonce = secrets.token_hex(16)
            approval_id = "approval-" + uuid4().hex
            now = datetime.now(timezone.utc)
            expires = now + timedelta(seconds=ttl_seconds)
            connection.execute(
                "INSERT INTO approvals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    approval_id,
                    proposal_id,
                    actor,
                    _hash(raw_token),
                    nonce,
                    proposal["action_hash"],
                    expires.isoformat(),
                    None,
                    now.isoformat(),
                ),
            )
            connection.execute("UPDATE proposals SET status = 'approved', updated_at = ? WHERE id = ?", (now.isoformat(), proposal_id))
            connection.execute(
                "INSERT INTO audit_log(event_id, event_type, subject_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    "evt-" + uuid4().hex,
                    "proposal.approved",
                    proposal_id,
                    _canonical({"actor": actor, "expires_at": expires.isoformat(), "nonce": nonce}),
                    now.isoformat(),
                ),
            )
        self.traces.write("sentinel.approval", {"proposal.id": proposal_id, "actor": actor, "expires_at": expires.isoformat()})
        return {
            "approval_id": approval_id,
            "proposal_id": proposal_id,
            "approval_token": raw_token,
            "expires_at": expires.isoformat(),
            "action_hash": proposal["action_hash"],
        }

    def execute(self, proposal_id: str, approval_token: str, idempotency_key: str) -> dict:
        if not idempotency_key.strip():
            raise ApprovalError("Idempotency key is required")
        with self.storage.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cached = connection.execute("SELECT proposal_id, result_json FROM idempotency WHERE key = ?", (idempotency_key,)).fetchone()
            if cached:
                if cached["proposal_id"] != proposal_id:
                    raise ApprovalError("Idempotency key is already bound to a different proposal")
                return json.loads(cached["result_json"])
            proposal = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            if not proposal:
                raise NotFoundError(f"Unknown proposal: {proposal_id}")
            if proposal["status"] == "executed":
                raise ReplayRejected("Proposal has already been executed")
            if proposal["status"] != "approved":
                raise ApprovalError(f"Proposal is not approved: {proposal['status']}")
            approval = connection.execute(
                "SELECT * FROM approvals WHERE proposal_id = ? AND token_hash = ?",
                (proposal_id, _hash(approval_token)),
            ).fetchone()
            if not approval:
                raise ApprovalError("Approval token is invalid")
            if approval["consumed_at"] is not None:
                raise ReplayRejected("Approval token has already been consumed")
            if datetime.fromisoformat(approval["expires_at"]) <= datetime.now(timezone.utc):
                raise ApprovalError("Approval token has expired")
            if approval["action_hash"] != proposal["action_hash"]:
                raise ApprovalError("Approval is not bound to the current action hash")

            public_proposal = {
                "id": proposal["id"],
                "incident_id": proposal["incident_id"],
                "action": proposal["action"],
                "capability": proposal["capability"],
                "arguments": json.loads(proposal["arguments_json"]),
                "preconditions": json.loads(proposal["preconditions_json"])["items"],
                "postconditions": json.loads(proposal["postconditions_json"])["items"],
            }
            if _hash(_canonical(public_proposal)) != proposal["action_hash"]:
                raise ApprovalError("Stored proposal failed integrity verification")
            validate_proposal(public_proposal)

            incident = connection.execute("SELECT * FROM incidents WHERE id = ?", (proposal["incident_id"],)).fetchone()
            before = json.loads(incident["state_json"])
            after = apply_action(proposal["action"], before)
            if not postconditions_hold(proposal["action"], before, after):
                raise ApprovalError("Executor postconditions failed")

            now = utc_now()
            result = {
                "proposal_id": proposal_id,
                "incident_id": proposal["incident_id"],
                "action": proposal["action"],
                "status": "executed",
                "before": before,
                "after": after,
                "postconditions_verified": True,
                "idempotency_key": idempotency_key,
            }
            connection.execute(
                "UPDATE incidents SET status = 'mitigated', state_json = ?, updated_at = ? WHERE id = ?",
                (_canonical(after), now, proposal["incident_id"]),
            )
            connection.execute("UPDATE proposals SET status = 'executed', updated_at = ? WHERE id = ?", (now, proposal_id))
            connection.execute("UPDATE approvals SET consumed_at = ? WHERE id = ?", (now, approval["id"]))
            connection.execute(
                "INSERT INTO idempotency VALUES (?, ?, ?, ?)",
                (idempotency_key, proposal_id, _canonical(result), now),
            )
            connection.execute(
                "INSERT INTO audit_log(event_id, event_type, subject_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    "evt-" + uuid4().hex,
                    "proposal.executed",
                    proposal_id,
                    _canonical({"incident_id": result["incident_id"], "action": result["action"]}),
                    now,
                ),
            )
        self.traces.write("sentinel.execute", {"proposal.id": proposal_id, "incident.id": result["incident_id"], "action": result["action"], "postconditions": True})
        return result

    def _audit(self, event_type: str, subject_id: str, payload: dict) -> None:
        with self.storage.connect() as connection:
            connection.execute(
                "INSERT INTO audit_log(event_id, event_type, subject_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
                ("evt-" + uuid4().hex, event_type, subject_id, _canonical(payload), utc_now()),
            )

    def proposal_policy(self, action: str) -> dict:
        return action_spec(action)
