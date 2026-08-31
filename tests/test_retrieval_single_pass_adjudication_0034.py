from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import adjudicate_retrieval_single_pass_0034 as adjudicator  # noqa: E402


class RetrievalSinglePassAdjudication0034Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.benchmark = json.loads(adjudicator.BENCHMARK_PATH.read_text(encoding="utf-8"))
        cls.comparison = json.loads(adjudicator.COMPARISON_PATH.read_text(encoding="utf-8"))

    def test_five_process_benchmark_passes_exact_frozen_gate(self) -> None:
        self.assertEqual(self.benchmark["status"], "pass")
        self.assertEqual(self.benchmark["process_count"], 5)
        self.assertTrue(self.benchmark["summary"]["benchmark_gate_pass"])
        self.assertLessEqual(
            self.benchmark["summary"]["maximum_candidate_over_control_ratio"],
            self.benchmark["summary"]["ratio_ceiling"],
        )
        self.assertTrue(
            all(
                item["returned_id_mismatch_count"] == 0
                and item["held_out_loaded"] is False
                for item in self.benchmark["process_results"]
            )
        )

    def test_in_memory_comparison_reproduces_immutable_result(self) -> None:
        rebuilt = adjudicator.build_comparison()
        rebuilt.pop("observed_at_utc")
        recorded = json.loads(json.dumps(self.comparison))
        recorded.pop("observed_at_utc")
        self.assertEqual(rebuilt, recorded)

    def test_historical_comparison_uses_immutable_companion_manifest(self) -> None:
        self.assertEqual(
            adjudicator.MANIFEST_PATH,
            ROOT / "artifacts/verification/baseline-0033-prebuild-source-manifest.json",
        )
        self.assertNotEqual(adjudicator.MANIFEST_PATH, ROOT / "eval/manifest.json")
        self.assertEqual(
            adjudicator._historical_manifest_identity(),
            {
                "path": "eval/manifest.json",
                "bytes": 18484,
                "sha256": "4f9e9880a9f3a7dd75e94f83018d3f2bef996d4f49b05fd42160f7f62f281b20",
            },
        )

    def test_frozen_gate_inventory_mismatch_excludes_candidate(self) -> None:
        self.assertEqual(self.comparison["status"], "complete_candidate_excluded")
        self.assertFalse(self.comparison["candidate_selected"])
        self.assertEqual(
            self.comparison["failed_selection_checks"],
            ["exact_allowed_false_gate_inventory_and_all_other_131_boolean_gates_true"],
        )
        self.assertEqual(
            self.comparison["selected_configuration"],
            adjudicator.CONTROL_CONFIGURATION,
        )
        self.assertFalse(
            self.comparison["candidate_boolean_gates"]["exact_inventory"]
        )

    def test_candidate_preserves_safety_utility_and_both_split_v4_retrieval(self) -> None:
        self.assertEqual(self.comparison["v4_v5_equivalence"]["mismatch_count"], 0)
        self.assertTrue(all(self.comparison["metric_invariants"].values()))
        self.assertEqual(self.comparison["metrics"]["proposal_attack_success"], 0.0)
        self.assertEqual(self.comparison["metrics"]["terminal_attack_success"], 0.0)
        self.assertEqual(
            self.comparison["metrics"]["benign_utility"]["benign_case_pass_rate"],
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
