"""CLI exit codes for clinical HOLD: warnings cannot be interpreted as success."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from packages.cli.kernel.core import Decision, KernelDecision


class ClinicalCliExitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ce-cli-failclosed-")
        self.addCleanup(self.tmp.cleanup)
        self.input = Path(self.tmp.name) / "synthetic.json"
        self.input.write_text(json.dumps([{"fixture": True}]), encoding="utf-8")
        self.runner = CliRunner()

    def hold(self):
        return KernelDecision(
            decision=Decision.PENDING_REVIEW,
            policy_id="KERNEL-POLICY-001",
            policy_version="1.0.0",
            pending_count=1,
        )

    def test_main_cli_pending_returns_two(self):
        from packages.cli.main import app
        with patch("packages.cli.main.Kernel") as replacement:
            replacement.return_value.evaluate_batch.return_value = self.hold()
            result = self.runner.invoke(
                app, ["kernel", "validate", "--policy", "KERNEL-POLICY-001",
                      "--input", str(self.input)])
        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("PENDENTE", result.output)

    def test_standalone_cli_pending_returns_two(self):
        from packages.cli.kernel import cli
        with patch.object(cli.kernel_cli, "evaluate_batch", return_value=self.hold()):
            result = self.runner.invoke(
                cli.app, ["validate", "--policy", "KERNEL-POLICY-001",
                          "--input", str(self.input)])
        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("PENDENTE", result.output)

    def test_empty_main_input_is_blocking(self):
        from packages.cli.main import app
        self.input.write_text("[]", encoding="utf-8")
        result = self.runner.invoke(
            app, ["kernel", "validate", "--policy", "KERNEL-POLICY-001",
                  "--input", str(self.input)])
        self.assertEqual(result.exit_code, 2, result.output)

    def test_empty_standalone_input_is_blocking(self):
        from packages.cli.kernel import cli
        self.input.write_text("[]", encoding="utf-8")
        result = self.runner.invoke(
            cli.app, ["validate", "--policy", "KERNEL-POLICY-001",
                      "--input", str(self.input)])
        self.assertEqual(result.exit_code, 2, result.output)


if __name__ == "__main__":
    unittest.main()
