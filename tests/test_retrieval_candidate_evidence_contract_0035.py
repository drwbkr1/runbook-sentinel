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

import verify_retrieval_candidate_evidence_contract_0035 as verifier  # noqa: E402


class RetrievalCandidateEvidenceContract0035Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))
        frozen = cls.contract["frozen_inputs"]
        cls.controls = [
            json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
            for record in frozen["control_reports"]
        ]
        cls.candidates = [
            json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
            for record in frozen["candidate_reports"]
        ]

    def test_frozen_preimplementation_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            absent_implementation = Path(directory) / "absent.py"
            absent_result = Path(directory) / "absent.json"
            with (
                mock.patch.object(verifier, "IMPLEMENTATION_PATH", absent_implementation),
                mock.patch.object(verifier, "RESULT_PATH", absent_result),
            ):
                result = verifier.validate("frozen_preimplementation")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["candidate_evidence_admissible_count"], 3)
        self.assertFalse(result["candidate_selected"])

    def test_current_repository_lifecycle_is_valid(self) -> None:
        result = verifier.validate("auto")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        expected_phase = (
            "implemented_result"
            if verifier.RESULT_PATH.exists()
            else (
                "implementation_sealed_no_result"
                if verifier.IMPLEMENTATION_PATH.exists()
                else "frozen_preimplementation"
            )
        )
        self.assertEqual(result["phase"], expected_phase)

    def test_all_v5_reports_are_semantically_admissible_not_selected(self) -> None:
        expected = self.contract["frozen_reveal"]
        for report in self.candidates:
            result = verifier.reference_classify(self.contract, report)
            self.assertTrue(result["candidate_evidence_admissible"])
            self.assertFalse(result["candidate_selected"])
            self.assertFalse(result["selection_performed"])
            self.assertEqual(result["hard_invariant_failures"], [])
            self.assertEqual(
                result["selected_default_observation_differences"],
                sorted(expected["observed_default_observation_differences"]),
            )
            self.assertEqual(
                [item["source_error"] for item in result["safe_superset_pairs"]],
                sorted(expected["observed_safe_superset_pairs"]),
            )

    def test_all_v3_controls_remain_exact(self) -> None:
        for report in self.controls:
            result = verifier.reference_classify(self.contract, report)
            self.assertTrue(result["candidate_evidence_admissible"])
            self.assertEqual(result["false_gates"], [])
            self.assertEqual(result["safe_superset_pairs"], [])

    def test_hard_policy_failure_is_never_observational(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        changed["gates"]["policy_compliance_is_one"] = False
        result = verifier.reference_classify(self.contract, changed)
        self.assertFalse(result["candidate_evidence_admissible"])
        self.assertIn("policy_compliance_is_one", result["hard_invariant_failures"])

    def test_unknown_contextual_stage_fails_closed(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        changed["metrics"]["coverage"][
            "adversarial_retrieval_stage_outcome_split_contract_errors"
        ][0] = "dev-database-injection-coverage:stage_outcome:unknown_stage:request_evidence"
        result = verifier.reference_classify(self.contract, changed)
        self.assertFalse(result["candidate_evidence_admissible"])
        self.assertIn("safe_superset_closed_stage", result["errors"])

    def test_missing_required_cell_fails_closed(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        changed["metrics"]["coverage"][
            "missing_adversarial_retrieval_stage_outcome_split_cells"
        ] = [{"stage": "guidance_not_retrieved", "outcome": "diagnose", "split": "test"}]
        result = verifier.reference_classify(self.contract, changed)
        self.assertFalse(result["candidate_evidence_admissible"])
        self.assertIn("safe_superset_missing_required_cells", result["errors"])

    def test_cross_trial_ambiguity_fails_closed(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        changed["metrics"]["coverage"]["cross_trial_stage_ambiguity_count"] = 1
        result = verifier.reference_classify(self.contract, changed)
        self.assertFalse(result["candidate_evidence_admissible"])
        self.assertIn("safe_superset_cross_trial_ambiguity", result["errors"])

    def test_contextual_outcome_mismatch_fails_closed(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        case = next(
            case
            for case in changed["cases"]
            if case["scenario_id"] == "dev-database-injection-coverage"
        )
        case["attempts"][0]["actual"]["outcome"] = "abstain"
        result = verifier.reference_classify(self.contract, changed)
        self.assertFalse(result["candidate_evidence_admissible"])
        self.assertIn("safe_superset_outcome_evidence", result["errors"])

    def test_required_evidence_incomplete_fails_closed(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        changed["metrics"]["retrieval_quality"]["expected_evidence"][
            "all_expected_retrieved_rate"
        ] = 0.99
        result = verifier.reference_classify(self.contract, changed)
        self.assertFalse(result["candidate_evidence_admissible"])
        self.assertIn("required_evidence_incomplete", result["errors"])

    def test_observation_category_does_not_require_exact_false_inventory(self) -> None:
        changed = copy.deepcopy(self.candidates[0])
        changed["gates"]["retrieval_quality_extra_document_attempt_rate_exact"] = False
        result = verifier.reference_classify(self.contract, changed)
        self.assertTrue(result["candidate_evidence_admissible"])
        self.assertIn(
            "retrieval_quality_extra_document_attempt_rate_exact",
            result["selected_default_observation_differences"],
        )
        self.assertEqual(result["hard_invariant_failures"], [])

    def test_historical_exclusion_is_not_rewritten(self) -> None:
        comparison = json.loads(
            (
                ROOT
                / self.contract["frozen_inputs"]["comparison"]["path"]
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(comparison["candidate_selected"])
        self.assertEqual(comparison["selected_configuration"], "freshness-priority-lexical-v3")
        self.assertEqual(comparison["candidate_disposition"], "exclude_and_retain")


if __name__ == "__main__":
    unittest.main()
