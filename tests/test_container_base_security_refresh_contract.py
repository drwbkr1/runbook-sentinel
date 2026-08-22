from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContainerBaseSecurityRefreshContractTests(unittest.TestCase):
    def test_implemented_contract_matches_successor_repository(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/verify_container_base_security_refresh_contract.py"),
                "--root",
                str(ROOT),
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


if __name__ == "__main__":
    unittest.main()
