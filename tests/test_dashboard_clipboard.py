"""Run offline clipboard outcome regressions in the standard unittest gate."""
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DashboardClipboardTests(unittest.TestCase):
    def test_dashboard_clipboard_behavior(self):
        result = subprocess.run(
            ["node", "--test", "tests/test_dashboard_clipboard.js"],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
