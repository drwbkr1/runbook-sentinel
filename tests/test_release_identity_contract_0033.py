from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_retrieval_successor_lifecycle_0034 import (  # noqa: E402
    successor_runtime_is_allowed,
)

SCRIPT = ROOT / "scripts/verify_release_identity_contract_0033.py"
SPEC = importlib.util.spec_from_file_location("verify_release_identity_contract_0033", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
START_COMMIT = "2d81bd4e4f4fe89192f88485ea616d36f59358a2"


class ReleaseIdentityContract0033Tests(unittest.TestCase):
    def test_current_contract_matches_repository_phase(self) -> None:
        phase = "implemented" if (ROOT / "eval/container-contract-0033-v13.json").is_file() else "frozen"
        if successor_runtime_is_allowed(ROOT):
            with self.fixture() as directory:
                result = MODULE.evaluate(Path(directory), "frozen")
        else:
            result = MODULE.evaluate(ROOT, phase)
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["candidate_selected"])
        self.assertEqual(result["selected_configuration"], "freshness-priority-lexical-v3")
        self.assertEqual(result["product_runtime_file_count"], 24)
        self.assertEqual(result["new_external_asset_count"], 0)

    def test_rendered_dashboard_successor_identity_is_hash_bound(self) -> None:
        contract = json.loads(
            (ROOT / "eval/release-identity-contract-0033.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            contract["mechanical_file_identities"]["scripts/verify_live_api.ps1"]["after_sha256"],
            "7a4e33095266acd30ae53341de4b7e880d3d6bd50c042cae21f11456d9c633dd",
        )
        correction = contract["lifecycle_correction"]
        self.assertEqual(correction["status"], "corrected_before_public_successor_identity_implementation")
        self.assertFalse(correction["runtime_behavior_changed"])
        self.assertFalse(correction["security_or_authority_changed"])

    def test_frozen_correction_matches_public_predecessor_tree(self) -> None:
        with self.fixture() as directory:
            result = MODULE.evaluate(Path(directory), "frozen")
            self.assertTrue(result["valid"], result["errors"])
            self.assertFalse(result["candidate_selected"])

    def test_candidate_selection_fails_closed(self) -> None:
        with self.fixture() as directory:
            root = Path(directory)
            result_path = root / "artifacts/evaluations/baseline-0033-retrieval-candidate-admissibility.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["candidate_selected"] = True
            result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            evaluated = MODULE.evaluate(root, "frozen")
            self.assertFalse(evaluated["valid"])
            self.assertTrue(any("result" in error or "candidate" in error for error in evaluated["errors"]))

    def test_unenumerated_runtime_file_fails_closed(self) -> None:
        with self.fixture() as directory:
            root = Path(directory)
            (root / "src/runbook_sentinel/unreviewed.py").write_text("VALUE = 1\n", encoding="utf-8")
            evaluated = MODULE.evaluate(root, "frozen")
            self.assertFalse(evaluated["valid"])
            self.assertIn("enumerated product runtime inventory changed", evaluated["errors"])

    def test_runtime_byte_change_fails_closed(self) -> None:
        with self.fixture() as directory:
            root = Path(directory)
            path = root / "src/runbook_sentinel/policy.py"
            path.write_bytes(path.read_bytes() + b"\n")
            evaluated = MODULE.evaluate(root, "frozen")
            self.assertFalse(evaluated["valid"])
            self.assertIn("path hash mismatch: src/runbook_sentinel/policy.py", evaluated["errors"])

    def test_successor_contract_before_public_freeze_fails_closed(self) -> None:
        with self.fixture() as directory:
            root = Path(directory)
            (root / "eval/package-contract-0033.json").write_text("{}\n", encoding="utf-8")
            evaluated = MODULE.evaluate(root, "frozen")
            self.assertFalse(evaluated["valid"])
            self.assertTrue(any("before public freeze" in error for error in evaluated["errors"]))

    def test_base_source_change_fails_closed(self) -> None:
        with self.fixture() as directory:
            root = Path(directory)
            path = root / "eval/container-contract-0032-v12.json"
            contract = json.loads(path.read_text(encoding="utf-8"))
            contract["base_image"]["reference"] = "example.invalid/python@sha256:" + "0" * 64
            path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
            evaluated = MODULE.evaluate(root, "frozen")
            self.assertFalse(evaluated["valid"])
            self.assertTrue(any("container" in error or "base" in error for error in evaluated["errors"]))

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        contract = json.loads(
            (ROOT / "eval/release-identity-contract-0033.json").read_text(encoding="utf-8")
        )
        for relative in (
            "eval/release-identity-contract-0033.json",
            "artifacts/evaluations/baseline-0033-retrieval-candidate-admissibility.json",
            "artifacts/verification/baseline-0033-adjudication-result-public.json",
            "eval/package-contract-0032.json",
            "eval/container-contract-0032-v12.json",
            "artifacts/verification/container-baseline-0032.json",
            "artifacts/verification/container-source-gate-baseline-0032-chainguard-python.json",
            "artifacts/verification/container-base-intake-baseline-0032.json",
        ):
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        frozen_paths = sorted(
            set(contract["mechanical_file_identities"])
            | set(contract["runtime_identity"]["mechanical_paths"])
            | set(contract["runtime_identity"]["unchanged_paths"])
            | {"eval/package-contract.json", "eval/container-contract.json"}
        )
        for relative in frozen_paths:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(
                subprocess.check_output(["git", "show", f"{START_COMMIT}:{relative}"], cwd=ROOT)
            )
        return temporary


if __name__ == "__main__":
    unittest.main()
