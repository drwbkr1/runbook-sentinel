from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runbook_sentinel.errors import TraceIntegrityError
from runbook_sentinel.telemetry import TraceWriter, verify_trace_file


class TraceIntegrityDevelopmentTests(unittest.TestCase):
    def test_writer_emits_valid_anchored_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "trace.jsonl"
            writer = TraceWriter(trace_path)
            writer.write("sentinel.run", {"outcome": "propose_action"})
            writer.write("sentinel.execute", {"postconditions": True})
            anchor = writer.anchor()

            result = verify_trace_file(
                trace_path,
                expected_event_count=anchor["event_count"],
                expected_final_event_sha256=anchor["final_event_sha256"],
            )

            self.assertTrue(result["valid"])
            self.assertTrue(result["anchored"])
            self.assertEqual(2, result["event_count"])

    def test_content_mutation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "trace.jsonl"
            writer = TraceWriter(trace_path)
            writer.write("sentinel.execute", {"postconditions": True})
            event = json.loads(trace_path.read_text(encoding="utf-8"))
            event["attributes"]["postconditions"] = False
            trace_path.write_text(json.dumps(event) + "\n", encoding="utf-8")

            result = verify_trace_file(trace_path)

            self.assertFalse(result["valid"])
            self.assertIn(
                "event_hash_mismatch", {error["code"] for error in result["errors"]}
            )

    def test_writer_refuses_corrupt_existing_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "trace.jsonl"
            trace_path.write_text('{"not":"a-trace-event"}\n', encoding="utf-8")

            with self.assertRaises(TraceIntegrityError):
                TraceWriter(trace_path)

    def test_writer_resumes_valid_prefix_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "trace.jsonl"
            first_writer = TraceWriter(trace_path)
            first_writer.write("sentinel.run", {"outcome": "propose_action"})
            first_writer.write("sentinel.execute", {"postconditions": True})
            first_anchor = first_writer.anchor()

            resumed_writer = TraceWriter(trace_path)
            appended = resumed_writer.write("sentinel.resume", {"result": "continued"})
            resumed_anchor = resumed_writer.anchor()
            result = verify_trace_file(
                trace_path,
                expected_event_count=resumed_anchor["event_count"],
                expected_final_event_sha256=resumed_anchor["final_event_sha256"],
            )

            self.assertEqual(3, appended["sequence"])
            self.assertEqual(
                first_anchor["final_event_sha256"],
                appended["previous_event_sha256"],
            )
            self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
