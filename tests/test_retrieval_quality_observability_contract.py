from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_quality_observability_contract as verifier  # noqa: E402


class RetrievalQualityObservabilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "src/runbook_sentinel/data/scenarios.json").read_text(encoding="utf-8")
        )
        cls.report = json.loads(
            (
                ROOT
                / "artifacts/evaluations/runs/baseline-0028-final-source-attempt-004.json"
            ).read_text(encoding="utf-8")
        )
        cls.contract = json.loads(
            (ROOT / "eval/retrieval-quality-observability-contract.json").read_text(
                encoding="utf-8"
            )
        )

    def compute(self, report: dict | None = None, catalog: dict | None = None):
        return verifier.compute_quality(
            copy.deepcopy(catalog or self.catalog),
            copy.deepcopy(report or self.report),
        )

    def test_frozen_prechange_measurement_is_exact(self) -> None:
        result, errors = self.compute()
        self.assertEqual(errors, [])
        measurement = {
            key: value
            for key, value in result.items()
            if key
            not in {
                "contract_valid",
                "contract_errors",
                "conditional_rank_bucket_metrics",
            }
        }
        self.assertEqual(measurement, self.contract["frozen_measurement"])
        self.assertEqual(
            result["conditional_rank_bucket_metrics"],
            {
                "not_retrieved": {
                    "attempt_count": 6,
                    "policy_compliance_rate": 1.0,
                    "proposal_attack_success_rate": 0.0,
                    "terminal_attack_success_rate": 0.0,
                },
                "rank_1": {
                    "attempt_count": 30,
                    "policy_compliance_rate": 1.0,
                    "proposal_attack_success_rate": 0.0,
                    "terminal_attack_success_rate": 0.0,
                },
                "rank_2": {
                    "attempt_count": 45,
                    "policy_compliance_rate": 1.0,
                    "proposal_attack_success_rate": 0.0,
                    "terminal_attack_success_rate": 0.0,
                },
                "rank_3_4": {
                    "attempt_count": 9,
                    "policy_compliance_rate": 1.0,
                    "proposal_attack_success_rate": 0.0,
                    "terminal_attack_success_rate": 0.0,
                },
            },
        )

    def test_duplicate_retrieval_identity_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        retrieved = report["cases"][0]["attempts"][0]["actual"]["retrieved_document_ids"]
        self.assertGreaterEqual(len(retrieved), 2)
        retrieved[1] = retrieved[0]
        result, errors = self.compute(report=report)
        self.assertFalse(result["contract_valid"])
        self.assertIn("retrieved_ids", errors)

    def test_unknown_retrieval_identity_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["cases"][0]["attempts"][0]["actual"]["retrieved_document_ids"][0] = (
            "unknown-document"
        )
        result, errors = self.compute(report=report)
        self.assertFalse(result["contract_valid"])
        self.assertIn("retrieved_id_unknown", errors)

    def test_missing_retrieval_audit_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        del report["cases"][0]["attempts"][0]["actual"]["retrieved_document_ids"]
        result, errors = self.compute(report=report)
        self.assertFalse(result["contract_valid"])
        self.assertIn("retrieved_ids", errors)
        self.assertIn("retrieved_top_k", errors)

    def test_over_top_k_retrieval_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        scenarios = {scenario["id"]: scenario for scenario in self.catalog["scenarios"]}
        case = next(
            item
            for item in report["cases"]
            if len(scenarios[item["scenario_id"]]["documents"]) >= 5
        )
        document_ids = [
            item["id"] for item in scenarios[case["scenario_id"]]["documents"][:5]
        ]
        case["attempts"][0]["actual"]["retrieved_document_ids"] = document_ids
        result, errors = self.compute(report=report)
        self.assertFalse(result["contract_valid"])
        self.assertIn("retrieved_top_k", errors)

    def test_mixed_cross_trial_attack_rank_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        scenarios = {scenario["id"]: scenario for scenario in self.catalog["scenarios"]}
        case = next(
            item
            for item in report["cases"]
            if scenarios[item["scenario_id"]].get("attack_document_ids")
            and item["attempts"][0]["actual"]["retrieved_document_ids"].index(
                scenarios[item["scenario_id"]]["attack_document_ids"][0]
            )
            == 1
        )
        attack_id = scenarios[case["scenario_id"]]["attack_document_ids"][0]
        second = case["attempts"][1]["actual"]["retrieved_document_ids"]
        second.remove(attack_id)
        second.insert(0, attack_id)
        result, errors = self.compute(report=report)
        self.assertFalse(result["contract_valid"])
        self.assertIn("cross_trial_rank_bucket_ambiguity", errors)
        self.assertEqual(
            result["declared_attack_exposure"][
                "cross_trial_rank_bucket_ambiguity_count"
            ],
            1,
        )

    def test_report_catalog_bijection_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["cases"].pop()
        result, errors = self.compute(report=report)
        self.assertFalse(result["contract_valid"])
        self.assertIn("scenario_report_bijection", errors)


if __name__ == "__main__":
    unittest.main()
