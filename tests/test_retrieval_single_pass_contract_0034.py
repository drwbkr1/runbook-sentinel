from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_single_pass_contract_0034 as verifier  # noqa: E402


class RetrievalSinglePassContract0034Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_current_preimplementation_phase_passes(self) -> None:
        result = verifier.validate(require_phase="frozen_preimplementation")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["boundaries"]["candidate_implemented"])
        self.assertFalse(result["boundaries"]["benchmark_result_present"])
        self.assertFalse(result["boundaries"]["comparison_result_present"])

    def test_product_default_remains_v3_before_selection(self) -> None:
        self.assertEqual(
            verifier.runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION,
            verifier.CONTROL_CONFIGURATION,
        )
        self.assertNotIn(
            verifier.CANDIDATE_CONFIGURATION,
            verifier.runtime_retrieval.RETRIEVAL_CONFIGURATIONS,
        )

    def test_development_reference_is_exact_without_loading_held_out(self) -> None:
        result = verifier._development_equivalence()
        self.assertEqual(result["scenario_count"], 31)
        self.assertEqual(result["mismatch_count"], 0)
        self.assertEqual(result["mismatches"], [])
        self.assertFalse(result["held_out_loaded"])

    def test_frozen_caps_no_backfill_and_no_cache_are_exact(self) -> None:
        candidate = self.contract["frozen_candidate"]
        self.assertEqual(
            candidate["tier_caps"],
            {
                "fresh_project_evidence": 2,
                "stale_project_evidence": 1,
                "untrusted_guidance": 1,
            },
        )
        self.assertFalse(candidate["quota_backfill"])
        self.assertFalse(candidate["cross_request_cache_added"])
        self.assertFalse(candidate["default_configuration_changed_before_selection"])

    def test_held_out_and_balanced_order_boundaries_are_frozen(self) -> None:
        benchmark = self.contract["benchmark_contract"]
        comparison = self.contract["whole_system_comparison_contract"]
        self.assertTrue(benchmark["held_out_prohibited"])
        self.assertFalse(comparison["held_out_split_used_for_optimization"])
        self.assertEqual(
            comparison["balanced_report_order"],
            ["control", "candidate", "candidate", "control", "control", "candidate"],
        )
        self.assertEqual(
            comparison["candidate_allowed_false_boolean_gates"],
            verifier.ALLOWED_FALSE_GATES,
        )
        self.assertEqual(comparison["candidate_required_true_boolean_gate_count"], 131)

    def test_official_specification_gate_imports_nothing(self) -> None:
        source_gate = json.loads(verifier.SOURCE_GATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(source_gate["status"], "pass")
        self.assertEqual(
            source_gate["decision"], "use_for_narrow_specification_basis_without_import"
        )
        self.assertFalse(any(source_gate["imports"].values()))

    def test_tier_cap_mutation_fails_closed(self) -> None:
        mutated = json.loads(json.dumps(self.contract))
        mutated["frozen_candidate"]["tier_caps"]["fresh_project_evidence"] = 3
        with tempfile.TemporaryDirectory(prefix="sentinel-contract-0034-") as directory:
            path = Path(directory) / "contract.json"
            path.write_text(json.dumps(mutated), encoding="utf-8")
            result = verifier.validate(contract_path=path)
        self.assertEqual(result["status"], "fail")
        self.assertIn("tier_caps", result["errors"])

    def test_held_out_optimization_mutation_fails_closed(self) -> None:
        mutated = json.loads(json.dumps(self.contract))
        mutated["whole_system_comparison_contract"][
            "held_out_split_used_for_optimization"
        ] = True
        with tempfile.TemporaryDirectory(prefix="sentinel-contract-0034-") as directory:
            path = Path(directory) / "contract.json"
            path.write_text(json.dumps(mutated), encoding="utf-8")
            result = verifier.validate(contract_path=path)
        self.assertEqual(result["status"], "fail")
        self.assertIn("held_out_optimization_boundary", result["errors"])

    def test_allowed_false_gate_inventory_mutation_fails_closed(self) -> None:
        mutated = json.loads(json.dumps(self.contract))
        mutated["whole_system_comparison_contract"][
            "candidate_allowed_false_boolean_gates"
        ].append("policy_compliance_is_one")
        with tempfile.TemporaryDirectory(prefix="sentinel-contract-0034-") as directory:
            path = Path(directory) / "contract.json"
            path.write_text(json.dumps(mutated), encoding="utf-8")
            result = verifier.validate(contract_path=path)
        self.assertEqual(result["status"], "fail")
        self.assertIn("allowed_false_gate_inventory", result["errors"])


if __name__ == "__main__":
    unittest.main()
