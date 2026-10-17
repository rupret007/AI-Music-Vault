"""Keep exact work-session selection through exploratory search and filters."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DashboardSessionFilterTests(unittest.TestCase):
    def test_session_selection_and_storage(self):
        result = subprocess.run(
            ["node", "--test", "tests/test_dashboard_session_filters.js"],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
