from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_successor_lifecycle_0034 as verifier  # noqa: E402


class RetrievalSuccessorLifecycle0034Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_current_bridge_freeze_passes_with_predecessor_exact(self) -> None:
        result = verifier.validate(require_phase="bridge_frozen")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["targets_original"])
        self.assertFalse(result["implementation_result_present"])
        self.assertFalse(result["public_bridge_receipt_present"])
        self.assertFalse(result["held_out_loaded_by_bridge"])

    def test_exact_future_candidate_identity_is_frozen(self) -> None:
        successor = self.contract["retrieval_lifecycle"]["exact_experimental_successor"]
        self.assertEqual(successor["bytes"], 6079)
        self.assertEqual(
            successor["sha256"],
            "f5514cb7cb0b7686987d3374bcd80849f868509a2d32676a88585dd40d456b37",
        )
        self.assertEqual(successor["default_before_selection"], verifier.CONTROL_CONFIGURATION)
        self.assertTrue(successor["held_out_may_not_be_loaded_by_bridge"])

    def test_unknown_predecessor_hash_fails_closed(self) -> None:
        mutated = json.loads(json.dumps(self.contract))
        mutated["retrieval_lifecycle"]["released_predecessor"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="sentinel-successor-contract-") as directory:
            path = Path(directory) / "contract.json"
            path.write_text(json.dumps(mutated), encoding="utf-8")
            result = verifier.validate(contract_path=path)
        self.assertEqual(result["status"], "fail")
        self.assertIn("retrieval_identity", result["errors"])

    def test_bridge_changes_no_product_runtime_path(self) -> None:
        bridge = self.contract["bridge_implementation"]
        self.assertEqual(bridge["allowed_product_runtime_paths"], [])
        self.assertEqual(
            bridge["allowed_validator_paths"],
            [
                "scripts/verify_release_identity_contract_0033.py",
                "scripts/verify_retrieval_candidate_admissibility_contract.py",
                "scripts/verify_retrieval_tier_cap_contract.py",
            ],
        )

    def test_results_remain_absent_at_bridge_freeze(self) -> None:
        result = verifier.validate()
        self.assertFalse(result["benchmark_result_present"])
        self.assertFalse(result["comparison_result_present"])
        self.assertEqual(result["default_configuration"], verifier.CONTROL_CONFIGURATION)


if __name__ == "__main__":
    unittest.main()
