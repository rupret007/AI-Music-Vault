"""Zero is a recorded score; absent/null scores must stay absent/null."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_app_api import build_payload
from test_validate_catalog import extras_ok, fixture
from validate_catalog import validate


def score_fixture():
    cat = fixture()
    for row, value in zip(cat["songs"], (0, 100, None, None, None, None)):
        row.update(potential=value, readiness=value, momentum=value)
    cat["songs"][5].update(potential="", readiness="", momentum="")
    # Other scores alone do not make a song "scored".
    cat["songs"][4].update(readiness=80, momentum=90)
    return cat


class ScoreZeroTests(unittest.TestCase):
    def test_export_counts_zero_and_preserves_missing_scores(self):
        cat = score_fixture()
        for field in ("potential", "readiness", "momentum"):
            del cat["songs"][3][field]
        payload = build_payload(cat)
        self.assertEqual(payload["counts"]["scored"], 2)
        for field in ("potential", "readiness", "momentum"):
            self.assertEqual(payload["songs"][0][field], 0)
            self.assertEqual(payload["songs"][1][field], 100)
            self.assertIsNone(payload["songs"][2][field])
            self.assertIsNone(payload["songs"][3][field])
            self.assertEqual(payload["songs"][5][field], "")

    def test_validator_accepts_count_including_zero(self):
        cat = score_fixture()
        extra = extras_ok(cat)
        extra["app_api"]["counts"]["scored"] = 2
        self.assertEqual(validate(cat, extra), [])

    def test_validator_rejects_count_that_omits_zero(self):
        cat = score_fixture()
        extra = extras_ok(cat)
        extra["app_api"]["counts"]["scored"] = 1
        errors = validate(cat, extra)
        self.assertTrue(any("counts.scored=" in error for error in errors), errors)

    def test_real_catalog_stays_59_until_a_zero_is_added_in_memory(self):
        cat = json.loads((ROOT / "data/master_catalog.json").read_text())
        baseline = build_payload(cat)
        self.assertEqual(baseline["counts"]["scored"], 59)
        row = next(row for row in cat["songs"] if row.get("potential") is None)
        row["potential"] = 0
        changed = build_payload(cat)
        self.assertEqual(changed["counts"]["scored"], 60)
        changed_by_id = {song["id"]: song for song in changed["songs"]}
        for song in baseline["songs"]:
            if song["id"] != row["song_id"]:
                self.assertEqual(changed_by_id[song["id"]], song)

    def test_dashboard_score_behavior(self):
        result = subprocess.run(
            ["node", "--test", "tests/test_dashboard_score_zero.js"],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
