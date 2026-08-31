from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_successor_lifecycle_0034 as verifier  # noqa: E402


class RetrievalSuccessorPhaseTestCorrection0034Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.correction = cls.contract["successor_phase_test_correction"]

    def test_current_governed_phase_passes(self) -> None:
        result = verifier.validate()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["schema_revision"], 3)
        self.assertEqual(result["successor_phase_test_addendum"], 1)
        self.assertIn(
            result["phase"],
            {
                "bridge_frozen",
                "bridge_implemented_predecessor",
                "bridge_public_predecessor",
                "implementation_sealed_no_result",
                "evaluated_unselected",
                "selected",
            },
        )

    def test_only_three_test_paths_are_allowed(self) -> None:
        self.assertEqual(
            self.correction["allowed_test_paths"],
            [
                "tests/test_retrieval_fixture_phase_correction_0034.py",
                "tests/test_retrieval_successor_lifecycle_0034.py",
                "tests/test_retrieval_meta_test_lifecycle_correction_0034.py",
            ],
        )

    def test_current_and_future_identities_are_frozen(self) -> None:
        expected = {
            "tests/test_retrieval_fixture_phase_correction_0034.py": (
                {"bytes": 3159, "sha256": "ee7c67c27d222761e30e6c45a24b4054cbf5e4e439b16e2b3720370bf026a63f"},
                {"bytes": 3449, "sha256": "ee640f79aba920746e6bfc93550b1d8a6986da4d975b8270285beee8573ab3d6"},
            ),
            "tests/test_retrieval_successor_lifecycle_0034.py": (
                {"bytes": 4029, "sha256": "7d019d8dcf1bc96ed4365d2482a66839bd2d05d1a067afb5bc47cb2d45b57caa"},
                {"bytes": 5178, "sha256": "42cd3888be6c180d64a378cda093f96c9dac902f4703bbcc8f2867ba7ee411bc"},
            ),
            "tests/test_retrieval_meta_test_lifecycle_correction_0034.py": (
                {"bytes": 3029, "sha256": "a9f499dc4960748bb498ea2370688eec252ebc6fa4114b9e54ead8a873b8909d"},
                {"bytes": 3656, "sha256": "b50247ed37b143d67843c23aaa4ad60044ac5b351ceaa9cd707ff6f37f477a35"},
            ),
        }
        for record in self.correction["tests"]:
            current, future = expected[record["path"]]
            self.assertEqual(record["current_identity"], current)
            self.assertEqual(record["future_identity"], future)
            self.assertTrue(verifier._successor_phase_test_exact(ROOT, self.contract, record["path"]))
            self.assertTrue(verifier._successor_phase_test_source_valid(ROOT, self.contract, record["path"]))

    def test_unknown_test_identity_fails_closed(self) -> None:
        relative = self.correction["allowed_test_paths"][2]
        with tempfile.TemporaryDirectory(prefix="sentinel-successor-phase-test-") as directory:
            root = Path(directory)
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("unknown\n", encoding="utf-8")
            self.assertFalse(verifier._successor_phase_test_exact(root, self.contract, relative))
            self.assertFalse(verifier._successor_phase_test_source_valid(root, self.contract, relative))

    def test_security_and_result_boundaries_remain_closed(self) -> None:
        for key in (
            "product_runtime_changed",
            "benchmark_or_comparison_result_created",
            "default_changed",
            "release_identity_or_bridge_validator_weakened",
            "admissibility_or_selection_rule_changed",
            "security_or_authority_changed",
        ):
            self.assertFalse(self.correction[key])
        result = verifier.validate()
        if result["phase"] in {
            "bridge_frozen",
            "bridge_implemented_predecessor",
            "bridge_public_predecessor",
            "implementation_sealed_no_result",
        }:
            self.assertFalse(verifier.BENCHMARK_RESULT_PATH.exists())
            self.assertFalse(verifier.COMPARISON_RESULT_PATH.exists())
        else:
            self.assertTrue(verifier.BENCHMARK_RESULT_PATH.is_file())
            self.assertTrue(verifier.COMPARISON_RESULT_PATH.is_file())
        expected_default = (
            verifier.CANDIDATE_CONFIGURATION
            if result["phase"] == "selected"
            else verifier.CONTROL_CONFIGURATION
        )
        self.assertEqual(
            verifier.runtime_retrieval.DEFAULT_RETRIEVAL_CONFIGURATION,
            expected_default,
        )


if __name__ == "__main__":
    unittest.main()
