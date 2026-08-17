from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_model_output_conformance_result.py"
SPEC = importlib.util.spec_from_file_location("verify_model_output_conformance_result", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
COMPARISON = ROOT / "artifacts/evaluations/baseline-0030-model-contract-comparison.json"


class ModelOutputConformanceResultTests(unittest.TestCase):
    def _mutated(self, mutate) -> Path:
        payload = json.loads(COMPARISON.read_text(encoding="utf-8"))
        mutate(payload)
        temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with temp:
            json.dump(payload, temp)
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def test_current_three_configuration_comparison_passes(self) -> None:
        self.assertEqual(MODULE.validate(COMPARISON)["status"], "pass")

    def test_product_default_change_fails_closed(self) -> None:
        path = self._mutated(lambda p: p["selection"].update({"product_default_changed": True}))
        self.assertIn("deterministic product default changed", MODULE.validate(path)["errors"])

    def test_false_development_improvement_fails_closed(self) -> None:
        path = self._mutated(lambda p: p["comparison"].update({"development_parse_improved": False}))
        self.assertIn("comparison development_parse_improved mismatch", MODULE.validate(path)["errors"])

    def test_report_identity_drift_fails_closed(self) -> None:
        path = self._mutated(lambda p: p["configurations"]["candidate_v3"].update({"report_sha256": "0" * 64}))
        self.assertIn("candidate_v3 report identity mismatch", MODULE.validate(path)["errors"])


if __name__ == "__main__":
    unittest.main()
