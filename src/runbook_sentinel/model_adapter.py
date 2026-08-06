from __future__ import annotations

import hashlib
import json
import re
import socket
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .policy import ACTION_SPECS


DIAGNOSIS_CODE_RE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
MISSING_EVIDENCE_RE = re.compile(r"^[a-z][a-z0-9_:,.-]{0,119}$")
MAX_RESPONSE_BYTES = 1024 * 1024
Transport = Callable[[str, dict, float], dict]


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        del req, fp, code, msg, headers, newurl
        return None


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _string_list(value: object, pattern: re.Pattern[str] | None = None) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("expected a string array")
    if len(set(value)) != len(value):
        raise ValueError("array values must be unique")
    if pattern and any(not pattern.fullmatch(item) for item in value):
        raise ValueError("array value does not match the allowed identifier pattern")
    return value


def parse_model_content(content: str, allowed_document_ids: set[str]) -> dict:
    payload = json.loads(content)
    if not isinstance(payload, dict):
        raise ValueError("model output must be an object")
    required_keys = {
        "outcome",
        "diagnosis_code",
        "evidence_ids",
        "missing_evidence",
        "proposal",
        "reason",
    }
    if set(payload) != required_keys:
        raise ValueError("model output keys do not match the contract")

    outcome = payload["outcome"]
    if outcome not in {"diagnose", "request_evidence", "propose_action", "abstain"}:
        raise ValueError("model outcome is not allowed")
    diagnosis_code = payload["diagnosis_code"]
    if not isinstance(diagnosis_code, str) or not DIAGNOSIS_CODE_RE.fullmatch(diagnosis_code):
        raise ValueError("diagnosis code is not a bounded identifier")
    evidence_ids = _string_list(payload["evidence_ids"])
    if not set(evidence_ids).issubset(allowed_document_ids):
        raise ValueError("model cited evidence outside the decision context")
    missing_evidence = _string_list(payload["missing_evidence"], MISSING_EVIDENCE_RE)
    reason = payload["reason"]
    if not isinstance(reason, str) or not 1 <= len(reason) <= 500:
        raise ValueError("model reason is outside the bounded string contract")

    proposal = payload["proposal"]
    if outcome == "propose_action":
        if not isinstance(proposal, dict) or set(proposal) != {"action", "capability", "arguments"}:
            raise ValueError("proposal does not match the exact contract")
        action = proposal["action"]
        if action not in ACTION_SPECS:
            raise ValueError("proposal action is not allowed")
        if proposal["capability"] != ACTION_SPECS[action]["capability"]:
            raise ValueError("proposal capability does not match the action")
        if proposal["arguments"] != {}:
            raise ValueError("proposal arguments must be empty")
    elif proposal is not None:
        raise ValueError("proposal must be null for non-proposal outcomes")

    return {
        "outcome": outcome,
        "diagnosis_code": diagnosis_code,
        "evidence_ids": evidence_ids,
        "missing_evidence": missing_evidence,
        "proposal": proposal,
        "reason": reason,
        "confidence": 0.5,
    }


def _default_transport(endpoint: str, payload: dict, timeout: float) -> dict:
    request = Request(
        endpoint,
        data=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = build_opener(ProxyHandler({}), _RejectRedirects())
    with opener.open(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("model response exceeded the byte limit")
    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise ValueError("model transport response must be an object")
    return parsed


class OllamaIncidentAgent:
    def __init__(self, contract_path: str | Path, transport: Transport | None = None):
        self.contract_path = Path(contract_path)
        self.contract = json.loads(self.contract_path.read_text(encoding="utf-8"))
        self.runtime = self.contract["runtime"]
        self.name = self.contract["evaluation_contract"]["candidate_configuration"]
        self._transport = transport or _default_transport
        self._validate_endpoint()

    def _validate_endpoint(self) -> None:
        parsed = urlparse(self.runtime["endpoint"])
        allowed_hosts = set(self.runtime["allowed_endpoint_hosts"])
        if (
            parsed.scheme != "http"
            or parsed.hostname not in allowed_hosts
            or parsed.hostname != "127.0.0.1"
            or parsed.port != 11434
            or parsed.path != "/api/chat"
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("model endpoint is outside the frozen loopback boundary")
        if self.runtime.get("stream") is not False:
            raise ValueError("model contract must explicitly disable streaming")
        if self.runtime.get("tools_supplied") is not False:
            raise ValueError("model contract must explicitly disable tools")

    def analyze(self, prompt: str, documents: list[dict], as_of: str) -> dict:
        evidence = [
            {
                "id": document["id"],
                "kind": document["kind"],
                "observed_at": document["observed_at"],
                "content": document["content"],
            }
            for document in documents
        ]
        input_payload = {
            "as_of": as_of,
            "operator_request": prompt,
            "evidence": evidence,
        }
        user_content = self.contract["user_template"].replace(
            "{{input_json}}",
            json.dumps(input_payload, sort_keys=True, separators=(",", ":")),
        )
        request_payload = {
            "model": self.runtime["model"],
            "stream": False,
            "messages": [
                {"role": "system", "content": self.contract["system_prompt"]},
                {"role": "user", "content": user_content},
            ],
            "format": self.contract["output_schema"],
            "options": self.runtime["options"],
            "keep_alive": "5m",
        }
        metadata = self._metadata(parse_status="transport_started", model_call_count=1)
        metadata["request_payload_sha256"] = _sha256(
            json.dumps(request_payload, sort_keys=True, separators=(",", ":"))
        )
        try:
            response = self._transport(
                self.runtime["endpoint"],
                request_payload,
                float(self.runtime["timeout_seconds"]),
            )
        except (TimeoutError, socket.timeout):
            return self._failure("model_timeout", "timeout", metadata)
        except (HTTPError, URLError, OSError):
            return self._failure("model_unavailable", "transport_error", metadata)
        except (ValueError, json.JSONDecodeError):
            return self._failure("model_output_invalid", "transport_response_invalid", metadata)
        except Exception:
            return self._failure("model_unavailable", "unexpected_transport_error", metadata)

        if not isinstance(response, dict):
            return self._failure("model_output_invalid", "transport_response_invalid", metadata)
        message = response.get("message")
        if not isinstance(message, dict):
            return self._failure("model_output_invalid", "content_missing", metadata)
        content = message.get("content")
        if not isinstance(content, str):
            return self._failure("model_output_invalid", "content_missing", metadata)
        metadata.update(
            {
                "raw_output_sha256": _sha256(content),
                "prompt_tokens": self._nonnegative_int(response.get("prompt_eval_count")),
                "completion_tokens": self._nonnegative_int(response.get("eval_count")),
                "total_duration_ns": self._nonnegative_int(response.get("total_duration")),
                "load_duration_ns": self._nonnegative_int(response.get("load_duration")),
            }
        )
        if response.get("model") != self.runtime["model"] or response.get("done") is not True:
            return self._failure("model_output_invalid", "response_identity_invalid", metadata)
        try:
            result = parse_model_content(content, {document["id"] for document in documents})
        except (ValueError, json.JSONDecodeError):
            return self._failure("model_output_invalid", "schema_invalid", metadata)
        metadata["parse_status"] = "valid"
        result["model_metadata"] = metadata
        return result

    def _metadata(self, parse_status: str, model_call_count: int) -> dict:
        return {
            "provider": self.runtime["provider"],
            "model": self.runtime["model"],
            "runtime_version": self.runtime["runtime_version"],
            "model_manifest_sha256": self.runtime["model_manifest_sha256"],
            "contract_id": self.contract["contract_id"],
            "system_prompt_sha256": _sha256(self.contract["system_prompt"]),
            "request_payload_sha256": None,
            "parse_status": parse_status,
            "raw_output_sha256": None,
            "model_call_count": model_call_count,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_duration_ns": 0,
            "load_duration_ns": 0,
        }

    @staticmethod
    def _nonnegative_int(value: object) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0

    @staticmethod
    def _failure(diagnosis_code: str, parse_status: str, metadata: dict) -> dict:
        metadata["parse_status"] = parse_status
        return {
            "outcome": "abstain",
            "diagnosis_code": diagnosis_code,
            "evidence_ids": [],
            "missing_evidence": [],
            "proposal": None,
            "reason": "The untrusted model output did not satisfy the frozen decision contract.",
            "confidence": 0.0,
            "model_metadata": metadata,
        }
