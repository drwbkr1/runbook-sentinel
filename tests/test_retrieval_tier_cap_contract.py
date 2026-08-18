from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_tier_cap_contract as verifier  # noqa: E402


class RetrievalTierCapContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frozen = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_current_contract_phase_passes(self) -> None:
        implemented = (
            verifier.CANDIDATE_CONFIGURATION
            in verifier.runtime_retrieval.RETRIEVAL_CONFIGURATIONS
        )
        selected = (
            verifier.runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION
            == verifier.CANDIDATE_CONFIGURATION
        )
        result = verifier.validate(
            require_implementation=implemented and not selected,
            require_selection=selected,
        )
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])

    def test_accepted_control_survives_latest_pointer_advance_exactly(self) -> None:
        control = self.frozen["accepted_control"]
        with tempfile.TemporaryDirectory(prefix="sentinel-control-") as directory:
            root = Path(directory)
            declared = root / "latest.json"
            archived = root / "baseline-0030-final-source-attempt-001.json"
            manifest = root / "manifest.json"
            baseline_0030 = verifier.ACCEPTED_CONTROL_ARCHIVE_PATH.read_bytes()
            baseline_0031 = (
                verifier.ROOT
                / "artifacts/evaluations/runs/baseline-0031-final-source-attempt-001.json"
            ).read_bytes()
            active_manifest = (
                verifier.ROOT
                / "artifacts/evaluations/runs/baseline-0031-final-source-attempt-001.manifest.json"
            ).read_bytes()
            self.assertEqual(
                hashlib.sha256(baseline_0030).hexdigest(),
                control["evaluation_sha256"],
            )

            declared.write_bytes(baseline_0030)
            errors: list[str] = []
            selected = verifier._resolve_accepted_control(
                control, declared, archived, manifest, errors
            )
            self.assertEqual(selected, declared)
            self.assertEqual(errors, [])

            declared.write_bytes(baseline_0031)
            archived.write_bytes(baseline_0030)
            manifest.write_bytes(active_manifest)
            errors = []
            selected = verifier._resolve_accepted_control(
                control, declared, archived, manifest, errors
            )
            self.assertEqual(selected, archived)
            self.assertEqual(errors, [])

            archived.write_bytes(baseline_0030 + b"tampered")
            errors = []
            selected = verifier._resolve_accepted_control(
                control, declared, archived, manifest, errors
            )
            self.assertEqual(selected, declared)
            self.assertEqual(errors, ["control_evaluation_archive_identity"])

    def test_reference_candidate_enforces_exact_caps_without_backfill(self) -> None:
        scenario = {
            "prompt": "worker backlog current evidence",
            "as_of": "2026-08-17T12:00:00Z",
            "documents": [
                {
                    "id": "fresh-a",
                    "kind": "telemetry",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T11:55:00Z",
                },
                {
                    "id": "fresh-b",
                    "kind": "status",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T11:54:00Z",
                },
                {
                    "id": "fresh-c",
                    "kind": "status",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T11:53:00Z",
                },
                {
                    "id": "stale-a",
                    "kind": "telemetry",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T08:00:00Z",
                },
                {
                    "id": "stale-b",
                    "kind": "status",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T07:00:00Z",
                },
                {
                    "id": "guidance-a",
                    "kind": "runbook",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T11:00:00Z",
                },
                {
                    "id": "guidance-b",
                    "kind": "runbook",
                    "title": "worker backlog",
                    "content": "current evidence",
                    "observed_at": "2026-08-17T10:00:00Z",
                },
            ],
        }
        selected = verifier.reference_candidate(scenario)
        selected_ids = [document["id"] for document in selected]
        self.assertEqual(len(selected_ids), 4)
        self.assertEqual(selected_ids[:2], ["fresh-a", "fresh-b"])
        self.assertEqual(selected_ids[2:], ["stale-a", "guidance-a"])
        self.assertNotIn("fresh-c", selected_ids)
        self.assertNotIn("stale-b", selected_ids)
        self.assertNotIn("guidance-b", selected_ids)

    def test_development_reference_preserves_required_evidence_and_ranks(self) -> None:
        result = verifier.validate()
        control = result["development_control"]
        candidate = result["development_reference_candidate"]
        self.assertEqual(control["all_expected_retrieved_rate"], 1.0)
        self.assertEqual(candidate["all_expected_retrieved_rate"], 1.0)
        self.assertEqual(candidate["expected_rank_1_count"], control["expected_rank_1_count"])
        self.assertEqual(candidate["expected_rank_2_count"], control["expected_rank_2_count"])

    def test_development_reference_improves_focus_without_claiming_relevance(self) -> None:
        result = verifier.validate()
        control = result["development_control"]
        candidate = result["development_reference_candidate"]
        self.assertGreater(
            candidate["expected_document_share_mean"],
            control["expected_document_share_mean"],
        )
        self.assertLess(
            candidate["extra_document_count"], control["extra_document_count"]
        )
        self.assertIn("not exhaustive relevance", self.frozen["limits"][0])

    def test_score_threshold_failures_are_retained_and_rejected(self) -> None:
        rejected = self.frozen["development_only_preflight"]["rejected_score_thresholds"]
        self.assertEqual(len(rejected), 3)
        self.assertTrue(
            all(
                item["development_complete_case_count"]
                < item["development_eligible_case_count"]
                for item in rejected
            )
        )
        self.assertTrue(all(item["rejection"] == "drops frozen required evidence" for item in rejected))

    def test_default_and_held_out_selection_boundaries_are_frozen(self) -> None:
        comparison = self.frozen["comparison_contract"]
        candidate = self.frozen["frozen_candidate"]
        self.assertTrue(comparison["no_default_change_before_complete_comparison"])
        self.assertFalse(comparison["held_out_split_used_for_optimization"])
        self.assertFalse(candidate["default_configuration_changed_before_selection"])
        self.assertFalse(candidate["policy_approval_executor_or_authority_changed"])


if __name__ == "__main__":
    unittest.main()
