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


class RetrievalFixturePhaseCorrection0034Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.correction = cls.contract["fixture_phase_correction"]

    def test_current_governed_lifecycle_phase_passes(self) -> None:
        result = verifier.validate()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["schema_version"], "1.2")
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

    def test_corrected_test_identity_is_precomputed_exactly(self) -> None:
        path = ROOT / self.correction["allowed_test_path"]
        payload = path.read_bytes()
        identity = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        released = self.correction["released_bridge_test_identity"]
        corrected = self.correction["corrected_test_identity"]
        self.assertIn(identity, (released, corrected))
        if identity == released:
            source = payload.decode("utf-8")
            replacement = self.correction["exact_replacement"]
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

    def test_unknown_test_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sentinel-fixture-phase-0034-") as directory:
            root = Path(directory)
            relative = self.correction["allowed_test_path"]
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("unknown\n", encoding="utf-8")
            self.assertFalse(
                verifier._bridge_changed_path_exact(
                    root,
                    relative,
                    self.correction["released_bridge_test_identity"],
                    self.contract,
                )
            )

    def test_historical_release_verifier_remains_exact(self) -> None:
        release = next(
            item
            for item in self.contract["historical_validator_predecessors"]
            if item["path"] == "scripts/verify_release_identity_contract_0033.py"
        )
        path = ROOT / release["path"]
        self.assertEqual(path.stat().st_size, release["bytes"])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), release["sha256"])


if __name__ == "__main__":
    unittest.main()
