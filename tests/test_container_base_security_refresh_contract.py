from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContainerBaseSecurityRefreshContractTests(unittest.TestCase):
    def test_implemented_contract_matches_released_v0_0_32_fixture(self) -> None:
        fixture_paths = (
            "eval/container-base-security-refresh-contract-0032.json",
            "artifacts/verification/container-source-gate-baseline-0032-chainguard-python.json",
            "artifacts/verification/container-scout-critical-high-baseline-0031-final-audit-failure-001.json",
            "artifacts/verification/release-audit-baseline-0031-attempt-001-blocked.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            for relative in fixture_paths:
                destination = fixture / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)
            released_contract = json.loads(
                (ROOT / "eval/container-contract-0032-v12.json").read_text(encoding="utf-8")
            )
            dockerfile_lines = released_contract["dockerfile_contract"]["expected_lines"]
            (fixture / "Dockerfile").write_text(
                "\n".join(dockerfile_lines) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/verify_container_base_security_refresh_contract.py"),
                    "--root",
                    str(fixture),
                    "--phase",
                    "implemented",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertEqual(result["source_gate_status"], "ready")
        self.assertEqual(result["retained_failed_check"], ["CHECK-007"])
        current_dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines()
        self.assertEqual(current_dockerfile[0], dockerfile_lines[0])
        self.assertIn(
            'LABEL dev.runbook-sentinel.base.digest="sha256:1f6779775c9f466890da563e411cb677045a6c20b6a65160eefad1deffb5012c"',
            current_dockerfile,
        )


if __name__ == "__main__":
    unittest.main()
