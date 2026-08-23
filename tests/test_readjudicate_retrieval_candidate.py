from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import readjudicate_retrieval_candidate as adjudicator  # noqa: E402


class RetrievalCandidateReadjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            adjudicator.CONTRACT_PATH.read_text(encoding="utf-8")
        )
        retained = cls.contract["retained_comparison"]
        cls.candidate = json.loads(
            (ROOT / retained["candidate_report_path"]).read_text(encoding="utf-8")
        )
        cls.comparison = json.loads(
            (ROOT / retained["comparison_path"]).read_text(encoding="utf-8")
        )

    def test_in_memory_result_matches_frozen_expected_readjudication(self) -> None:
        result = adjudicator.build_result()
        for key, value in self.contract["frozen_expected_readjudication"].items():
            self.assertEqual(result[key], value)
        self.assertTrue(result["candidate_evidence_admissible"])
        self.assertFalse(result["candidate_selected"])
        self.assertEqual(
            result["selected_configuration"], "freshness-priority-lexical-v3"
        )

    def test_result_bytes_are_deterministic(self) -> None:
        first = adjudicator.canonical_bytes(adjudicator.build_result())
        second = adjudicator.canonical_bytes(adjudicator.build_result())
        self.assertEqual(first, second)
        self.assertEqual(
            hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest()
        )

    def test_in_memory_evaluation_does_not_create_successor_result(self) -> None:
        self.assertFalse(adjudicator.RESULT_PATH.exists())
        adjudicator.build_result()
        self.assertFalse(adjudicator.RESULT_PATH.exists())

    def test_unlisted_false_gate_fails_closed(self) -> None:
        candidate = copy.deepcopy(self.candidate)
        candidate["gates"]["policy_compliance_is_one"] = False
        with self.assertRaisesRegex(
            adjudicator.AdjudicationError, "candidate_evidence_inadmissible"
        ):
            adjudicator.assemble_result(
                self.contract, candidate, self.comparison
            )

    def test_missing_safe_superset_pair_fails_closed(self) -> None:
        candidate = copy.deepcopy(self.candidate)
        candidate["metrics"]["coverage"][
            "adversarial_retrieval_stage_outcome_split_contract_errors"
        ].pop()
        with self.assertRaisesRegex(
            adjudicator.AdjudicationError, "candidate_evidence_inadmissible"
        ):
            adjudicator.assemble_result(
                self.contract, candidate, self.comparison
            )

    def test_writer_rejects_nonfrozen_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "other.json"
            with self.assertRaisesRegex(
                adjudicator.AdjudicationError, "output_path_not_frozen"
            ):
                adjudicator.write_result(output)
            self.assertFalse(output.exists())

    def test_writer_is_exclusive_and_written_result_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with (
                mock.patch.object(adjudicator, "RESULT_PATH", output),
                mock.patch.object(adjudicator.verifier, "RESULT_PATH", output),
            ):
                result = adjudicator.write_result(output)
                self.assertEqual(output.read_bytes(), adjudicator.canonical_bytes(result))
                validation = adjudicator.verifier.validate("implemented_overlay")
                self.assertEqual(validation["status"], "pass")
                with self.assertRaises(FileExistsError):
                    adjudicator.write_result(output)

    def test_source_identities_are_unchanged_by_build(self) -> None:
        before = adjudicator._source_snapshot(self.contract)
        adjudicator.build_result()
        after = adjudicator._source_snapshot(self.contract)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
