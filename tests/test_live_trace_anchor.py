from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runbook_sentinel.errors import TraceIntegrityError
from runbook_sentinel.live_trace_anchor_evaluation import (
    run_live_trace_anchor_evaluation,
)
from runbook_sentinel.telemetry import (
    TraceWriter,
    live_trace_anchor_path,
    verify_anchored_trace_files,
)


class LiveTraceAnchorDevelopmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.trace = self.base / "live.jsonl"
        self.anchor = live_trace_anchor_path(self.trace)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def writer(self) -> TraceWriter:
        return TraceWriter(self.trace, self.anchor)

    def test_dev_empty_start(self) -> None:
        writer = self.writer()
        self.assertEqual(writer.anchor()["event_count"], 0)
        self.assertFalse(self.trace.exists())
        self.assertFalse(self.anchor.exists())

    def test_dev_first_write_exact(self) -> None:
        event = self.writer().write("sentinel.run", {"case": "first"})
        verification = verify_anchored_trace_files(self.trace, self.anchor)
        anchor = json.loads(self.anchor.read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(verification["anchored"])
        self.assertEqual(verification["event_count"], 1)
        self.assertEqual(verification["final_event_sha256"], event["event_sha256"])
        self.assertEqual(anchor["trace_file_name"], self.trace.name)
        self.assertEqual(anchor["event_count"], 1)
        self.assertEqual(anchor["final_event_sha256"], event["event_sha256"])
        self.assertEqual(len(anchor["anchor_sha256"]), 64)
        self.assertEqual(list(self.base.glob(f".{self.anchor.name}.*.tmp")), [])

    def test_dev_tail_truncation_detected(self) -> None:
        writer = self.writer()
        for index in range(3):
            writer.write("sentinel.run", {"index": index})
        lines = self.trace.read_text(encoding="utf-8").splitlines()
        self.trace.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8", newline="\n")
        verification = verify_anchored_trace_files(self.trace, self.anchor)
        codes = {error["code"] for error in verification["errors"]}
        self.assertFalse(verification["valid"])
        self.assertEqual(
            codes,
            {
                "expected_event_count_mismatch",
                "expected_final_event_sha256_mismatch",
            },
        )
        with self.assertRaises(TraceIntegrityError):
            self.writer()
        self.assertEqual(len(self.trace.read_text(encoding="utf-8").splitlines()), 2)

    def test_dev_anchor_digest_mutation_detected(self) -> None:
        writer = self.writer()
        writer.write("sentinel.run", {"index": 1})
        writer.write("sentinel.run", {"index": 2})
        anchor = json.loads(self.anchor.read_text(encoding="utf-8"))
        anchor["event_count"] = 1
        self.anchor.write_text(
            json.dumps(anchor, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        verification = verify_anchored_trace_files(self.trace, self.anchor)
        self.assertFalse(verification["valid"])
        self.assertIn(
            "anchor_sha256_mismatch",
            {error["code"] for error in verification["errors"]},
        )
        with self.assertRaises(TraceIntegrityError):
            self.writer()

    def test_revealed_frozen_contract_is_exact(self) -> None:
        report = run_live_trace_anchor_evaluation()
        self.assertEqual(report["case_count"], 10)
        self.assertTrue(report["gates"]["development_exact"])
        self.assertTrue(report["gates"]["test_exact"])
        self.assertTrue(report["gates"]["all_selected_cases_exact"])


if __name__ == "__main__":
    unittest.main()
