from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_tier_cap_result as verifier  # noqa: E402


class RetrievalTierCapResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.accepted = json.loads(
            (ROOT / "artifacts/evaluations/latest.json").read_text(encoding="utf-8")
        )

    def _focused_candidate(self) -> dict:
        candidate = copy.deepcopy(self.accepted)
        candidate["retrieval_configuration"] = verifier.CANDIDATE_CONFIGURATION
        development = candidate["metrics"]["retrieval_quality"]["splits"][
            "development"
        ]
        development["expected_document_share_mean"] = 0.75
        development["extra_document_count"] = 45
        candidate["metrics"]["latency"]["median_ms"] -= 1
        candidate["metrics"]["latency"]["p95_ms"] -= 1
        return candidate

    def test_precomparison_phase_passes_without_result_files(self) -> None:
        result = verifier.validate()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["phase"], "precomparison")
        self.assertFalse(result["control_present"])
        self.assertFalse(result["candidate_present"])

    def test_frozen_selection_accepts_only_complete_pareto_candidate(self) -> None:
        selection = verifier._selection(self.accepted, self._focused_candidate())
        self.assertTrue(all(selection.values()))

    def test_required_evidence_drop_fails_closed(self) -> None:
        candidate = self._focused_candidate()
        candidate["cases"][0]["attempts"][0]["actual"][
            "retrieved_document_ids"
        ] = []
        selection = verifier._selection(self.accepted, candidate)
        self.assertFalse(selection["development_required_evidence_complete"])
        self.assertFalse(selection["required_evidence_ranks_exact"])

    def test_latency_regression_cannot_be_traded_for_focus(self) -> None:
        candidate = self._focused_candidate()
        candidate["metrics"]["latency"]["median_ms"] = (
            self.accepted["metrics"]["latency"]["median_ms"] + 0.001
        )
        selection = verifier._selection(self.accepted, candidate)
        self.assertFalse(selection["median_latency_non_inferior"])

    def test_runtime_default_remains_control_before_comparison(self) -> None:
        self.assertEqual(
            verifier.runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION,
            verifier.CONTROL_CONFIGURATION,
        )


if __name__ == "__main__":
    unittest.main()
