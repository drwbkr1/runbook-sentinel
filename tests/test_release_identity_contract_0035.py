from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_release_identity_contract_0035 as verifier  # noqa: E402


class ReleaseIdentityContract0035Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            verifier.CONTRACT_PATH.read_text(encoding="utf-8")
        )

    def test_current_frozen_transition_passes(self) -> None:
        result = verifier.evaluate(ROOT, "frozen")
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["product_runtime_file_count"], 24)
        self.assertFalse(result["candidate_selected"])
        self.assertFalse(result["selection_performed"])
        self.assertEqual(result["selected_configuration"], "freshness-priority-lexical-v3")
        self.assertFalse(result["successor_package_present"])
        self.assertFalse(result["successor_container_present"])

    def test_future_product_identities_are_precomputed_exactly(self) -> None:
        for relative, identity in self.contract["runtime_identity"]["mechanical_paths"].items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for old, new, count in identity["replacements"]:
                self.assertEqual(text.count(old), count)
                text = text.replace(old, new)
            import hashlib

            self.assertEqual(
                hashlib.sha256(text.encode("utf-8")).hexdigest(),
                identity["after_sha256"],
            )

    def test_classification_cannot_be_rewritten_as_selection(self) -> None:
        with self.fixture() as root:
            path = root / self.contract["classification_result"]["path"]
            result = json.loads(path.read_text(encoding="utf-8"))
            result["candidate_selected"] = True
            path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            evaluated = verifier.evaluate(root, "frozen")
            self.assertEqual(evaluated["status"], "fail")
            self.assertTrue(
                any("classification" in error for error in evaluated["errors"])
            )

    def test_unenumerated_runtime_file_fails_closed(self) -> None:
        with self.fixture() as root:
            path = root / "src/runbook_sentinel/unreviewed.py"
            path.write_text("VALUE = 1\n", encoding="utf-8")
            result = verifier.evaluate(root, "frozen")
            self.assertIn("runtime_inventory", result["errors"])

    def test_unchanged_policy_mutation_fails_closed(self) -> None:
        with self.fixture() as root:
            path = root / "src/runbook_sentinel/policy.py"
            path.write_bytes(path.read_bytes() + b"\n")
            result = verifier.evaluate(root, "frozen")
            self.assertIn(
                "runtime_unchanged:src/runbook_sentinel/policy.py", result["errors"]
            )

    def test_successor_before_public_freeze_fails_closed(self) -> None:
        with self.fixture() as root:
            path = root / self.contract["successors"]["package_contract"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")
            result = verifier.evaluate(root, "frozen")
            self.assertIn(
                "successor_present_before_public_freeze:package_contract",
                result["errors"],
            )

    def test_external_base_identity_mutation_fails_closed(self) -> None:
        with self.fixture() as root:
            path = root / self.contract["external_asset_reuse"]["source_gate"]["path"]
            path.write_bytes(path.read_bytes() + b"\n")
            result = verifier.evaluate(root, "frozen")
            self.assertIn("base_source_gate_identity", result["errors"])

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        paths = set(self.contract["runtime_identity"]["mechanical_paths"])
        paths.update(self.contract["runtime_identity"]["unchanged_paths"])
        paths.update(
            {
                "eval/release-identity-contract-0035.json",
                self.contract["classification_result"]["path"],
                self.contract["classification_result"]["public_receipt_path"],
                self.contract["external_asset_reuse"]["source_gate"]["path"],
                self.contract["external_asset_reuse"]["intake_receipt"]["path"],
            }
        )
        paths.update(record["path"] for record in self.contract["predecessors"].values())
        for relative in paths:
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return _TemporaryRoot(temporary, root)


class _TemporaryRoot:
    def __init__(self, temporary: tempfile.TemporaryDirectory[str], root: Path) -> None:
        self.temporary = temporary
        self.root = root

    def __enter__(self) -> Path:
        return self.root

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
