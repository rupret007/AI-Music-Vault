"""Run StoryBoard's real catalog-import.ts — not the Python contract mirror."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tests" / "test_storyboard_catalog_import.mjs"


class StoryBoardCatalogImportTests(unittest.TestCase):
    def test_real_importer_reimport_is_idempotent(self):
        result = subprocess.run(
            ["node", "--experimental-strip-types", str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            result.stdout + "\n" + result.stderr,
        )
        self.assertIn("storyboard importer OK", result.stdout)
        self.assertIn("title collision first-write-wins", result.stdout)
        self.assertIn("catalog-import.ts", result.stdout)


if __name__ == "__main__":
    unittest.main()
