from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_release_identity_contract_0033.py"
SPEC = importlib.util.spec_from_file_location("verify_release_identity_contract_0033", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseIdentityContract0033Tests(unittest.TestCase):
    def test_frozen_contract_matches_repository(self) -> None:
        result = MODULE.evaluate(ROOT, "frozen")
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["candidate_selected"])
        self.assertEqual(result["selected_configuration"], "freshness-priority-lexical-v3")
        self.assertEqual(result["product_runtime_file_count"], 24)
        self.assertEqual(result["new_external_asset_count"], 0)

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
        for relative in (
            "eval/release-identity-contract-0033.json",
            "artifacts/evaluations/baseline-0033-retrieval-candidate-admissibility.json",
            "artifacts/verification/baseline-0033-adjudication-result-public.json",
            "eval/package-contract-0032.json",
            "eval/package-contract.json",
            "eval/container-contract-0032-v12.json",
            "eval/container-contract.json",
            "artifacts/verification/container-baseline-0032.json",
            "artifacts/verification/container-source-gate-baseline-0032-chainguard-python.json",
            "artifacts/verification/container-base-intake-baseline-0032.json",
            "pyproject.toml",
            "Dockerfile",
            ".dockerignore",
            "scripts/verify_baseline.py",
            "scripts/verify_live_api.ps1",
            "scripts/verify_mcp_stdio.py",
            "scripts/inspect_runtime_evidence.py",
            "scripts/build_zipapp.py",
            "scripts/verify_package_contract.py",
            "scripts/freeze_manifest.py",
        ):
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        shutil.copytree(ROOT / "src/runbook_sentinel", root / "src/runbook_sentinel", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        return temporary


if __name__ == "__main__":
    unittest.main()
