from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_candidate_admissibility_contract as verifier  # noqa: E402


class RetrievalCandidateAdmissibilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))
        retained = cls.contract["retained_comparison"]
        cls.candidate = json.loads(
            (ROOT / retained["candidate_report_path"]).read_text(encoding="utf-8")
        )
        cls.comparison = json.loads(
            (ROOT / retained["comparison_path"]).read_text(encoding="utf-8")
        )

    def test_frozen_preimplementation_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            absent_implementation = Path(directory) / "absent.py"
            absent_result = Path(directory) / "absent-result.json"
            with (
                mock.patch.object(
                    verifier, "IMPLEMENTATION_PATH", absent_implementation
                ),
                mock.patch.object(verifier, "RESULT_PATH", absent_result),
            ):
                result = verifier.validate("frozen_preimplementation")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["candidate_evidence_admissible"])
        self.assertFalse(result["candidate_selected"])
        self.assertEqual(result["selected_configuration"], "freshness-priority-lexical-v3")

    def test_current_repository_lifecycle_is_valid(self) -> None:
        result = verifier.validate("auto")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        expected_phase = (
            "implemented_overlay"
            if verifier.RESULT_PATH.exists()
            else "implementation_sealed_no_result"
        )
        self.assertEqual(result["phase"], expected_phase)
        self.assertTrue(result["implementation_present"])
        self.assertEqual(result["result_present"], verifier.RESULT_PATH.exists())

    def test_implementation_seal_without_result_is_a_valid_phase(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            implementation = Path(directory) / "readjudicate_retrieval_candidate.py"
            implementation.write_text("# simulated implementation\n", encoding="utf-8")
            absent_result = Path(directory) / "absent-result.json"
            with (
                mock.patch.object(verifier, "IMPLEMENTATION_PATH", implementation),
                mock.patch.object(verifier, "RESULT_PATH", absent_result),
            ):
                result = verifier.validate("auto")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["phase"], "implementation_sealed_no_result")
        self.assertTrue(result["implementation_present"])
        self.assertFalse(result["result_present"])

    def test_implementation_seal_rejects_a_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            implementation = Path(directory) / "readjudicate_retrieval_candidate.py"
            implementation.write_text("# simulated implementation\n", encoding="utf-8")
            result_path = Path(directory) / "result.json"
            result_path.write_text("{}\n", encoding="utf-8")
            with (
                mock.patch.object(verifier, "IMPLEMENTATION_PATH", implementation),
                mock.patch.object(verifier, "RESULT_PATH", result_path),
            ):
                result = verifier.validate("implementation_sealed_no_result")
        self.assertEqual(result["status"], "fail")
        self.assertIn("result_present_before_implementation_seal", result["errors"])

    def test_only_exact_control_fingerprints_are_exemptible(self) -> None:
        result = verifier.classify_candidate(
            self.contract, self.candidate, self.comparison
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["nonfingerprint_boolean_gates_passed"], 131)
        self.assertEqual(
            result["candidate_false_gates"],
            sorted(
                self.contract["measured_weakness"]["exact_control_fingerprint_gates"]
            ),
        )

        changed = copy.deepcopy(self.candidate)
        changed["gates"]["policy_compliance_is_one"] = False
        rejected = verifier.classify_candidate(
            self.contract, changed, self.comparison
        )
        self.assertIn("candidate_false_gate_inventory", rejected["errors"])
        self.assertFalse(rejected["candidate_evidence_admissible"])

    def test_required_coverage_and_safe_superset_are_fail_closed(self) -> None:
        changed = copy.deepcopy(self.candidate)
        changed["metrics"]["coverage"][
            "missing_adversarial_retrieval_stage_outcome_split_cells"
        ] = ["development:guidance_not_retrieved:diagnose"]
        rejected = verifier.classify_candidate(
            self.contract, changed, self.comparison
        )
        self.assertIn("retrieval_stage_missing_cells", rejected["errors"])

        changed = copy.deepcopy(self.candidate)
        changed["metrics"]["coverage"][
            "adversarial_retrieval_stage_outcome_split_contract_errors"
        ].append("unknown:stage_outcome:guidance_not_retrieved:abstain")
        rejected = verifier.classify_candidate(
            self.contract, changed, self.comparison
        )
        self.assertIn("safe_superset_pair_inventory", rejected["errors"])

    def test_required_evidence_and_ranks_remain_exact(self) -> None:
        changed = copy.deepcopy(self.candidate)
        changed["metrics"]["retrieval_quality"]["expected_evidence"][
            "all_expected_retrieved_rate"
        ] = 0.99
        rejected = verifier.classify_candidate(
            self.contract, changed, self.comparison
        )
        self.assertIn("required_evidence_completeness", rejected["errors"])

    def test_original_latency_failure_and_disposition_are_retained(self) -> None:
        result = verifier.classify_candidate(
            self.contract, self.candidate, self.comparison
        )
        self.assertEqual(result["errors"], [])
        self.assertFalse(
            self.comparison["selection_checks"]["median_latency_non_inferior"]
        )
        self.assertEqual(
            self.comparison["candidate_disposition"], "excluded_and_retained"
        )
        self.assertFalse(
            self.contract["frozen_expected_readjudication"]["candidate_selected"]
        )

    def test_public_freeze_receipt_proves_implementation_and_result_absent(self) -> None:
        receipt_path = (
            ROOT
            / "artifacts/verification/baseline-0033-preimplementation-freeze-public.json"
        )
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["boundaries"]["implementation_present_at_public_freeze"])
        self.assertFalse(receipt["boundaries"]["successor_result_present_at_public_freeze"])
        self.assertFalse(receipt["boundaries"]["runtime_or_default_changed"])
        self.assertFalse(receipt["boundaries"]["security_gate_weakened"])


if __name__ == "__main__":
    unittest.main()
