from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_model_output_conformance_contract as verifier  # noqa: E402


class ModelOutputConformanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frozen = json.loads(verifier.CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.legacy = json.loads(
            (ROOT / "eval/model-contract-0018-v2.json").read_text(encoding="utf-8")
        )

    def test_preimplementation_contract_passes(self) -> None:
        result = verifier.validate(require_implementation=False)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["implementation_phase"], "frozen_preimplementation")

    def test_target_changes_only_identity_metadata_and_diagnosis_pattern(self) -> None:
        target = verifier.target_contract(self.legacy, self.frozen)
        self.assertEqual(
            verifier.changed_paths(self.legacy, target),
            [
                "$.checkpoint",
                "$.contract_id",
                "$.output_schema.properties.diagnosis_code.pattern",
                "$.schema_version",
            ],
        )
        self.assertEqual(target["system_prompt"], self.legacy["system_prompt"])
        self.assertEqual(target["runtime"], self.legacy["runtime"])
        self.assertEqual(target["parser_contract"], self.legacy["parser_contract"])

    def test_target_pattern_matches_the_existing_parser_language(self) -> None:
        pattern = re.compile(verifier.EXPECTED_PATTERN)
        accepted = ["a", "worker_stalled", "a" + "0" * 79]
        rejected = ["", "Worker Stalled", "1worker", "worker-stalled", "a" + "0" * 80]
        self.assertTrue(all(pattern.fullmatch(value) for value in accepted))
        self.assertTrue(all(not pattern.fullmatch(value) for value in rejected))

    def test_runtime_or_prompt_drift_is_outside_the_target(self) -> None:
        target = verifier.target_contract(self.legacy, self.frozen)
        drifted = copy.deepcopy(target)
        drifted["runtime"]["tools_supplied"] = True
        drifted["system_prompt"] += " drift"
        changes = verifier.changed_paths(target, drifted)
        self.assertEqual(changes, ["$.runtime.tools_supplied", "$.system_prompt"])

    def test_pattern_omission_is_detectable(self) -> None:
        target = verifier.target_contract(self.legacy, self.frozen)
        del target["output_schema"]["properties"]["diagnosis_code"]["pattern"]
        self.assertIn(
            "$.output_schema.properties.diagnosis_code.pattern",
            verifier.changed_paths(verifier.target_contract(self.legacy, self.frozen), target),
        )


if __name__ == "__main__":
    unittest.main()
