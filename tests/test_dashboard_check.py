"""The dashboard freshness gate must compare source projections without writing."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = "Jeff Story Song Vault Dashboard.html"


class DashboardCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        for source in (ROOT / "scripts").glob("*.py"):
            shutil.copy2(source, self.root / "scripts" / source.name)
        (self.root / "data").mkdir()
        self.catalog = {"version": "fixture", "songs": [{
            "song_id": "TEST-1", "canonical_title": "Fixture song",
            "artist_project": "Fixture project", "classification": "original",
            "next_action": "Write the first chorus.",
        }]}
        self.transcripts = [{
            "uid": "memo-1", "title": "Fixture memo", "date": "2026-01-01",
            "text": "A synthetic lyric long enough for the searchable memo index.",
        }]
        self.feed = {
            "schema_version": 3, "primary_consumer": "StoryBoard",
            "songs": [{"id": "TEST-1", "title": "Fixture song",
                       "import_scope": "not_live_band"}],
        }
        self.write_json("master_catalog.json", self.catalog)
        self.write_json("app_api.json", self.feed)
        self.write_json("vm_transcribed.json", self.transcripts)
        self.html = self.root / DASHBOARD
        self.assertEqual(self.run_builder().returncode, 0)

    def write_json(self, name, value):
        (self.root / "data" / name).write_text(json.dumps(value), encoding="utf-8")

    def run_builder(self, *args, root=None):
        root = root or self.root
        return subprocess.run(
            [sys.executable, str(root / "scripts/build_dashboard.py"), *args],
            cwd=self.root, capture_output=True, text=True, timeout=30,
        )

    def assert_check(self, code, diagnostic=""):
        before = self.html.read_bytes() if self.html.exists() else None
        modified = self.html.stat().st_mtime_ns if self.html.exists() else None
        result = self.run_builder("--check")
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stdout + result.stderr)
        self.assertEqual(self.html.read_bytes() if self.html.exists() else None, before)
        self.assertEqual(self.html.stat().st_mtime_ns if self.html.exists() else None, modified)

    def test_next_action_change_fails_until_rebuilt(self):
        self.assert_check(0)
        self.catalog["songs"][0]["next_action"] = "Revise the second chorus."
        self.write_json("master_catalog.json", self.catalog)
        self.assert_check(1, "DATA")
        self.assertEqual(self.run_builder().returncode, 0)
        self.assertIn("Revise the second chorus.", self.html.read_text(encoding="utf-8"))
        self.assert_check(0)

    def test_transcript_change_fails_until_rebuilt(self):
        self.transcripts[0]["text"] = "A revised synthetic lyric long enough for the memo index."
        self.write_json("vm_transcribed.json", self.transcripts)
        self.assert_check(1, "TX")
        self.assertEqual(self.run_builder().returncode, 0)
        self.assert_check(0)

    def test_other_song_projection_changes_fail(self):
        for field, value in (("potential", 75), ("key", "C"), ("alt_titles", ["Other title"])):
            with self.subTest(field=field):
                self.catalog["songs"][0][field] = value
                self.write_json("master_catalog.json", self.catalog)
                self.assert_check(1, "DATA")
                self.assertEqual(self.run_builder().returncode, 0)
                self.assert_check(0)

    def test_feed_scope_and_memo_match_changes_fail(self):
        self.feed["songs"][0]["import_scope"] = "default_live"
        self.write_json("app_api.json", self.feed)
        self.assert_check(1, "DATA")
        self.assertEqual(self.run_builder().returncode, 0)
        self.assert_check(0)
        match_path = self.root / "01_source_manifests/voicememo/vm_matches.json"
        match_path.parent.mkdir(parents=True)
        match_path.write_text(json.dumps({"TEST-1": ["memo-1"]}), encoding="utf-8")
        self.assert_check(1, "TX")
        self.assertEqual(self.run_builder().returncode, 0)
        self.assert_check(0)

    def test_script_escaping_round_trips(self):
        self.catalog["songs"][0]["next_action"] = "Write café lyrics with </script> and a ; marker."
        self.write_json("master_catalog.json", self.catalog)
        self.assertEqual(self.run_builder().returncode, 0)
        self.assert_check(0)

    def test_invalid_source_fails_without_writing(self):
        (self.root / "data/master_catalog.json").write_text("invalid", encoding="utf-8")
        self.assert_check(1, "CHECK FAILED")

    def test_missing_dashboard_fails_without_creating_it(self):
        self.html.unlink()
        self.assert_check(1, "missing")

    def test_missing_or_invalid_payload_fails_without_repairing_it(self):
        original = self.html.read_text(encoding="utf-8")
        for name in ("DATA", "TX"):
            for replacement in (f"const REMOVED_{name} = ", f"const {name} = invalid "):
                with self.subTest(name=name, replacement=replacement):
                    self.html.write_text(original.replace(f"const {name} = ", replacement), encoding="utf-8")
                    self.assert_check(1, name)

    def test_committed_dashboard_is_current_and_check_is_read_only(self):
        path = ROOT / DASHBOARD
        before, modified = path.read_bytes(), path.stat().st_mtime_ns
        result = self.run_builder("--check", root=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(path.stat().st_mtime_ns, modified)


if __name__ == "__main__":
    unittest.main()
