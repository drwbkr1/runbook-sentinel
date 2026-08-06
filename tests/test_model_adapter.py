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

from runbook_sentinel.model_adapter import OllamaIncidentAgent, parse_model_content
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

        missing_identity = OllamaIncidentAgent(
            CONTRACT_PATH,
            transport=lambda *_: {"done": True, "message": {"content": json.dumps({})}},
        ).analyze("prompt", [], "2026-08-06T16:00:00Z")
        self.assertEqual(missing_identity["diagnosis_code"], "model_output_invalid")
        self.assertEqual(missing_identity["model_metadata"]["parse_status"], "response_identity_invalid")

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

    def test_timeout_fails_closed_without_deterministic_fallback(self):
        def timeout_transport(*_):
            raise TimeoutError("synthetic timeout")

        agent = OllamaIncidentAgent(CONTRACT_PATH, transport=timeout_transport)
        result = agent.analyze("prompt", [], "2026-08-06T16:00:00Z")
        self.assertEqual((result["outcome"], result["diagnosis_code"]), ("abstain", "model_timeout"))
        self.assertEqual(result["model_metadata"]["parse_status"], "timeout")
        self.assertEqual(result["model_metadata"]["model_call_count"], 1)

    def test_non_loopback_contract_is_rejected_before_transport(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        contract["runtime"]["endpoint"] = "https://models.example/api/chat"
        contract["runtime"]["allowed_endpoint_hosts"] = ["models.example"]
        altered = self.base / "remote-contract.json"
        altered.write_text(json.dumps(contract), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "loopback boundary"):
            OllamaIncidentAgent(altered, transport=lambda *_: {})

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
        self.assertEqual(report["metrics"]["cost"]["model_calls"], 18)
        self.assertEqual(report["metrics"]["cost"]["prompt_tokens"], 18 * 101)
        self.assertEqual(report["metrics"]["cost"]["completion_tokens"], 18 * 33)
        self.assertEqual(report["metrics"]["generation"]["structured_parse_success_rate"], 1.0)
        self.assertEqual(report["gates"]["baseline_disposition"], "remediate")
        self.assertIsNone(report["gates"]["all_exact_control_cases_pass"])
        self.assertEqual(report["cases"][0]["attempts"][0]["validated_output"]["reason"], content["reason"])
        self.assertTrue(all("tools" not in payload for payload in calls))
        self.assertNotIn(content["reason"], output.with_name("fake-candidate.traces.jsonl").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
