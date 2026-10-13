"""Exercise the real builder in temporary roots with synthetic metadata only."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DashboardFeedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "scripts").mkdir()
        (self.root / "data").mkdir()
        for name in ("build_dashboard.py", "catalog_surface.py", "storyboard_contract.py"):
            shutil.copyfile(ROOT / "scripts" / name, self.root / "scripts" / name)
        self.song = {
            "song_id": "TEST-0001", "canonical_title": "Fixture song",
            "artist_project": "Fixture project", "classification": "Original",
        }
        self.feed = {
            "schema_version": 3, "primary_consumer": "StoryBoard",
            "songs": [{"id": "TEST-0001", "title": "Fixture song",
                       "import_scope": "not_live_band"}],
        }
        self.write_json("master_catalog.json", {"songs": [self.song]})
        self.write_json("app_api.json", self.feed)
        self.write_json("vm_transcribed.json", [])
        self.output = self.root / "Jeff Story Song Vault Dashboard.html"

    def write_json(self, name, value):
        (self.root / "data" / name).write_text(json.dumps(value), encoding="utf-8")

    def build(self):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "build_dashboard.py")],
            cwd=self.root, capture_output=True, text=True, timeout=15,
        )

    def assert_rejected_without_writing(self, *diagnostics):
        for existing in (False, True):
            with self.subTest(existing_html=existing):
                self.output.unlink(missing_ok=True)
                if existing:
                    self.output.write_bytes(b"previous dashboard\n")
                    before = self.output.stat().st_mtime_ns
                result = self.build()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("dashboard INVALID", result.stderr)
                for diagnostic in diagnostics:
                    self.assertIn(diagnostic, result.stderr)
                self.assertNotIn("dashboard written", result.stdout)
                if existing:
                    self.assertEqual(self.output.read_bytes(), b"previous dashboard\n")
                    self.assertEqual(self.output.stat().st_mtime_ns, before)
                else:
                    self.assertFalse(self.output.exists())

    def test_missing_feed(self):
        (self.root / "data" / "app_api.json").unlink()
        self.assert_rejected_without_writing("app_api.json")

    def test_feed_io_error(self):
        path = self.root / "data" / "app_api.json"
        path.unlink()
        path.mkdir()
        self.assert_rejected_without_writing("app_api.json")

    def test_malformed_or_non_utf8_feed(self):
        for contents in (b'{"songs":', b"\xff"):
            with self.subTest(contents=contents):
                (self.root / "data" / "app_api.json").write_bytes(contents)
                self.assert_rejected_without_writing("app_api.json")

    def test_invalid_feed_shape(self):
        for feed in (None, [], "bad", {}, {"songs": None}, {"songs": {}},
                     {"songs": []}, {"songs": [None]}):
            with self.subTest(feed=feed):
                self.write_json("app_api.json", feed)
                self.assert_rejected_without_writing("app_api.json")

    def test_invalid_feed_envelope(self):
        for key, value in (("schema_version", 2), ("primary_consumer", "Other")):
            with self.subTest(key=key):
                feed = copy.deepcopy(self.feed)
                feed[key] = value
                self.write_json("app_api.json", feed)
                self.assert_rejected_without_writing("app_api.json")

    def test_feed_ids_must_match_catalog_without_duplicates(self):
        row = self.feed["songs"][0]
        for rows in ([row, row], [dict(row, id="OTHER")],
                     [row, dict(row, id="OTHER")], [dict(row, id=None)],
                     [dict(row, id=[])], [dict(row, id=" TEST-0001 ")]):
            with self.subTest(rows=rows):
                self.write_json("app_api.json", dict(self.feed, songs=rows))
                self.assert_rejected_without_writing("app_api.json")

    def test_missing_or_invalid_scope(self):
        for scope in (None, "", "unknown", [], {}):
            with self.subTest(scope=scope):
                row = dict(self.feed["songs"][0], import_scope=scope)
                if scope is None:
                    del row["import_scope"]
                self.write_json("app_api.json", dict(self.feed, songs=[row]))
                self.assert_rejected_without_writing("app_api.json", "TEST-0001")

    def test_non_list_live_presence(self):
        for presence in (None, {}, "played", 0, False):
            with self.subTest(presence=presence):
                song = dict(self.song, live_presence=presence)
                self.write_json("master_catalog.json", {"songs": [song]})
                self.assert_rejected_without_writing("TEST-0001", "live_presence")

    def test_invalid_live_presence_event(self):
        for event in (None, "played", {}, {"band": "Fixture"},
                      {"band": "", "date": "2026-01-01"}):
            with self.subTest(event=event):
                song = dict(self.song, live_presence=[event])
                self.write_json("master_catalog.json", {"songs": [song]})
                self.assert_rejected_without_writing("TEST-0001", "live_presence[0]")

    def test_valid_feed_overlays_scope_and_play_history(self):
        for presence in (None, [], [{"band": "Fixture", "date": "2026-01-01"}]):
            with self.subTest(presence=presence):
                song = dict(self.song)
                if presence is not None:
                    song["live_presence"] = presence
                self.write_json("master_catalog.json", {"songs": [song]})
                result = self.build()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("dashboard written", result.stdout)
                html = self.output.read_text(encoding="utf-8")
                data = json.loads(html.split("const DATA = ", 1)[1].split(";\n", 1)[0])
                self.assertEqual(data[0]["scope"], "not_live_band")
                self.assertEqual(data[0]["scope_label"], "Not a live band")
                self.assertEqual(data[0]["lp"], ["Fixture (2026-01-01)"] if presence else [])


if __name__ == "__main__":
    unittest.main()
