from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.model_adapter import (
    MODEL_OUTPUT_ERROR_CODES,
    ModelOutputValidationError,
    OllamaIncidentAgent,
    parse_model_content,
)
from runbook_sentinel.evaluation import MODEL_AGENT_CONFIGURATION, run_evaluation
from runbook_sentinel.service import RunbookSentinel


CONTRACT_PATH = ROOT / "eval/model-contract.json"


def model_response(content: dict) -> dict:
    return {
        "model": "llama3.2:3b",
        "done": True,
        "message": {"role": "assistant", "content": json.dumps(content, sort_keys=True)},
        "prompt_eval_count": 101,
        "eval_count": 33,
        "total_duration": 900,
        "load_duration": 100,
    }


class ModelAdapterTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sentinel-model-test-")
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_structured_output_crosses_only_the_proposal_boundary(self):
        calls = []
        content = {
            "outcome": "propose_action",
            "diagnosis_code": "worker_stalled",
            "evidence_ids": ["telemetry-worker-current"],
            "missing_evidence": [],
            "proposal": {
                "action": "restart_worker",
                "capability": "synthetic.worker.restart",
                "arguments": {},
            },
            "reason": "Fresh worker telemetry supports a bounded restart proposal.",
        }

        def transport(endpoint, payload, timeout):
            calls.append((endpoint, payload, timeout))
            return model_response(content)

        trace_path = self.base / "traces.jsonl"
        service = RunbookSentinel(
            str(self.base / "state.db"),
            str(trace_path),
            agent=OllamaIncidentAgent(CONTRACT_PATH, transport=transport),
        )
        result = service.run_scenario("dev-worker-backlog")

        self.assertEqual(result["proposal"]["action"], "restart_worker")
        self.assertEqual(result["agent"], "ollama-llama3.2-3b-instruct-q4-k-m-v1")
        self.assertEqual(calls[0][0], "http://127.0.0.1:11434/api/chat")
        self.assertNotIn("tools", calls[0][1])
        self.assertEqual(calls[0][2], 30.0)
        self.assertEqual(result["model_metadata"]["parse_status"], "valid")
        self.assertIsNone(result["model_metadata"]["model_output_error_code"])
        self.assertEqual(len(result["model_metadata"]["system_prompt_sha256"]), 64)
        self.assertEqual(len(result["model_metadata"]["request_payload_sha256"]), 64)
        raw = json.dumps(content, sort_keys=True)
        self.assertEqual(result["model_metadata"]["raw_output_sha256"], hashlib.sha256(raw.encode()).hexdigest())
        trace = trace_path.read_text(encoding="utf-8")
        self.assertIn(result["model_metadata"]["raw_output_sha256"], trace)
        self.assertNotIn(content["reason"], trace)

    def test_malformed_and_capability_mismatched_outputs_fail_closed(self):
        malformed = OllamaIncidentAgent(CONTRACT_PATH, transport=lambda *_: model_response({"outcome": "diagnose"}))
        result = malformed.analyze("prompt", [], "2026-08-06T16:00:00Z")
        self.assertEqual((result["outcome"], result["diagnosis_code"]), ("abstain", "model_output_invalid"))
        self.assertIsNone(result["proposal"])
        self.assertEqual(result["model_metadata"]["parse_status"], "schema_invalid")
        self.assertEqual(
            result["model_metadata"]["model_output_error_code"],
            "top_level_keys_mismatch",
        )

        missing_identity = OllamaIncidentAgent(
            CONTRACT_PATH,
            transport=lambda *_: {"done": True, "message": {"content": json.dumps({})}},
        ).analyze("prompt", [], "2026-08-06T16:00:00Z")
        self.assertEqual(missing_identity["diagnosis_code"], "model_output_invalid")
        self.assertEqual(missing_identity["model_metadata"]["parse_status"], "response_identity_invalid")
        self.assertIsNone(missing_identity["model_metadata"]["model_output_error_code"])

        mismatched = {
            "outcome": "propose_action",
            "diagnosis_code": "worker_stalled",
            "evidence_ids": ["evidence-1"],
            "missing_evidence": [],
            "proposal": {
                "action": "restart_worker",
                "capability": "synthetic.cache.warm",
                "arguments": {},
            },
            "reason": "Attempted mismatched capability.",
        }
        with self.assertRaises(ValueError):
            parse_model_content(json.dumps(mismatched), {"evidence-1"})

    def test_frozen_development_failure_taxonomy_is_exact(self):
        contract = json.loads(
            (ROOT / "eval/model-output-failure-contract.json").read_text(encoding="utf-8")
        )
        development_cases = [
            case for case in contract["cases"] if case["split"] == "development"
        ]
        self.assertEqual(len(development_cases), 8)
        for case in development_cases:
            with self.subTest(case_id=case["case_id"]):
                content = (
                    case["content_literal"]
                    if case["content_encoding"] == "literal"
                    else json.dumps(case["payload"], sort_keys=True, separators=(",", ":"))
                )
                if case["expected"]["accepted"]:
                    parse_model_content(content, set(case["allowed_document_ids"]))
                else:
                    with self.assertRaises(ModelOutputValidationError) as raised:
                        parse_model_content(content, set(case["allowed_document_ids"]))
                    self.assertEqual(raised.exception.code, case["expected"]["error_code"])

    def test_timeout_fails_closed_without_deterministic_fallback(self):
        def timeout_transport(*_):
            raise TimeoutError("synthetic timeout")

        agent = OllamaIncidentAgent(CONTRACT_PATH, transport=timeout_transport)
        result = agent.analyze("prompt", [], "2026-08-06T16:00:00Z")
        self.assertEqual((result["outcome"], result["diagnosis_code"]), ("abstain", "model_timeout"))
        self.assertEqual(result["model_metadata"]["parse_status"], "timeout")
        self.assertIsNone(result["model_metadata"]["model_output_error_code"])
        self.assertEqual(result["model_metadata"]["model_call_count"], 1)

    def test_non_loopback_contract_is_rejected_before_transport(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        contract["runtime"]["endpoint"] = "https://models.example/api/chat"
        contract["runtime"]["allowed_endpoint_hosts"] = ["models.example"]
        altered = self.base / "remote-contract.json"
        altered.write_text(json.dumps(contract), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "loopback boundary"):
            OllamaIncidentAgent(altered, transport=lambda *_: {})

    def test_metadata_only_stale_evidence_reaches_model_without_payload_fields(self):
        calls = []
        content = {
            "outcome": "request_evidence",
            "diagnosis_code": "insufficient_fresh_evidence",
            "evidence_ids": [],
            "missing_evidence": ["fresh_telemetry"],
            "proposal": None,
            "reason": "Fresh evidence is required before making a bounded decision.",
        }

        def transport(endpoint, payload, timeout):
            del endpoint, timeout
            calls.append(payload)
            return model_response(content)

        agent = OllamaIncidentAgent(CONTRACT_PATH, transport=transport)
        result = agent.analyze(
            "Assess stale cache telemetry.",
            [
                {
                    "id": "telemetry-cache-stale-dev",
                    "kind": "telemetry",
                    "observed_at": "2026-08-06T12:00:00Z",
                }
            ],
            "2026-08-06T16:00:00Z",
        )
        self.assertEqual(result["outcome"], "request_evidence")
        user_message = calls[0]["messages"][1]["content"]
        self.assertIn('"id":"telemetry-cache-stale-dev"', user_message)
        self.assertIn('"observed_at":"2026-08-06T12:00:00Z"', user_message)
        self.assertNotIn('"title"', user_message)
        self.assertNotIn('"content"', user_message)

    def test_candidate_evaluation_reports_model_metrics_without_tools(self):
        calls = []
        content = {
            "outcome": "diagnose",
            "diagnosis_code": "no_actionable_fault",
            "evidence_ids": [],
            "missing_evidence": [],
            "proposal": None,
            "reason": "The fake transport returns a bounded valid object.",
        }

        def transport(endpoint, payload, timeout):
            del endpoint, timeout
            calls.append(payload)
            return model_response(content)

        output = self.base / "fake-candidate.json"
        report = run_evaluation(
            output,
            trials=1,
            agent_configuration=MODEL_AGENT_CONFIGURATION,
            model_transport=transport,
        )
        self.assertEqual(report["agent_configuration"], MODEL_AGENT_CONFIGURATION)
        self.assertEqual(report["metrics"]["cost"]["model_calls"], 31)
        self.assertEqual(report["metrics"]["cost"]["prompt_tokens"], 31 * 101)
        self.assertEqual(report["metrics"]["cost"]["completion_tokens"], 31 * 33)
        self.assertEqual(report["metrics"]["generation"]["structured_parse_success_rate"], 1.0)
        self.assertIsNone(
            report["metrics"]["generation"]["schema_invalid_classification_rate"]
        )
        self.assertEqual(
            report["metrics"]["generation"]["unclassified_schema_invalid_count"], 0
        )
        self.assertEqual(
            report["metrics"]["generation"]["model_output_error_code_counts"],
            {code: 0 for code in MODEL_OUTPUT_ERROR_CODES},
        )
        self.assertEqual(report["gates"]["baseline_disposition"], "remediate")
        self.assertIsNone(report["gates"]["all_exact_control_cases_pass"])
        self.assertEqual(report["cases"][0]["attempts"][0]["validated_output"]["reason"], content["reason"])
        self.assertTrue(all("tools" not in payload for payload in calls))
        self.assertTrue(
            all(
                attempt["model"]["model_output_error_code"] is None
                for case in report["cases"]
                for attempt in case["attempts"]
            )
        )
        self.assertNotIn(content["reason"], output.with_name("fake-candidate.traces.jsonl").read_text(encoding="utf-8"))

    def test_candidate_evaluation_classifies_schema_failures_without_raw_content(self):
        raw_marker = "must-not-retain-model-content"

        def transport(endpoint, payload, timeout):
            del endpoint, payload, timeout
            return model_response({"sentinel_raw_marker": raw_marker})

        output = self.base / "fake-invalid-candidate.json"
        report = run_evaluation(
            output,
            trials=1,
            agent_configuration=MODEL_AGENT_CONFIGURATION,
            model_transport=transport,
        )
        generation = report["metrics"]["generation"]
        self.assertEqual(generation["structured_parse_success_rate"], 0.0)
        self.assertEqual(generation["schema_invalid_classification_rate"], 1.0)
        self.assertEqual(generation["unclassified_schema_invalid_count"], 0)
        self.assertEqual(
            generation["model_output_error_code_counts"]["top_level_keys_mismatch"],
            31,
        )
        self.assertTrue(
            all(
                attempt["model"]["model_output_error_code"]
                == "top_level_keys_mismatch"
                for case in report["cases"]
                for attempt in case["attempts"]
            )
        )
        self.assertNotIn(raw_marker, output.read_text(encoding="utf-8"))
        self.assertNotIn(
            raw_marker,
            output.with_name("fake-invalid-candidate.traces.jsonl").read_text(
                encoding="utf-8"
            ),
        )


if __name__ == "__main__":
    unittest.main()
