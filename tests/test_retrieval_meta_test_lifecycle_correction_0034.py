from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_successor_lifecycle_0034 as verifier  # noqa: E402


class RetrievalMetaTestLifecycleCorrection0034Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.correction = cls.contract["meta_test_lifecycle_correction"]

    def test_current_public_meta_test_identity_passes(self) -> None:
        self.assertTrue(verifier._fixture_meta_test_exact(ROOT, self.contract))
        result = verifier.validate(require_phase="bridge_public_predecessor")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["schema_version"], "1.2")
        self.assertEqual(result["schema_revision"], 3)

    def test_phase_aware_meta_test_identity_is_precomputed_exactly(self) -> None:
        path = ROOT / self.correction["allowed_test_path"]
        payload = path.read_bytes()
        identity = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        released = self.correction["released_meta_test_identity"]
        corrected = self.correction["corrected_meta_test_identity"]
        self.assertIn(identity, (released, corrected))
        if identity == released:
            source = payload.decode("utf-8")
            replacement = self.correction["exact_block_replacement"]
            self.assertEqual(
                source.count(replacement["from"]),
                replacement["required_occurrence_count"],
            )
            payload = source.replace(
                replacement["from"],
                replacement["to"],
                replacement["required_occurrence_count"],
            ).encode("utf-8")
        self.assertEqual(len(payload), corrected["bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), corrected["sha256"])

    def test_unknown_meta_test_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sentinel-meta-test-0034-") as directory:
            root = Path(directory)
            path = root / self.correction["allowed_test_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("unknown\n", encoding="utf-8")
            self.assertFalse(verifier._fixture_meta_test_exact(root, self.contract))

    def test_meta_test_correction_changes_no_runtime_or_verifier_boundary(self) -> None:
        for key in (
            "release_test_changed",
            "product_runtime_changed",
            "release_identity_verifier_changed",
            "current_tree_bridge_validators_changed",
            "admissibility_or_selection_rule_changed",
            "security_or_authority_changed",
        ):
            self.assertIs(self.correction[key], False)


if __name__ == "__main__":
    unittest.main()
