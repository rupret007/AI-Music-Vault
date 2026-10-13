"""Importing the dashboard builder must not read inputs or write its output."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_NAME = "Jeff Story Song Vault Dashboard.html"


def fixture_inputs():
    return {
        "data/master_catalog.json": {
            "version": "fixture",
            "songs": [{
                "song_id": "ST-0001", "canonical_title": "Fixture song",
                "artist_project": "Fixture project", "classification": "original",
                "next_action": "Read lyrics for the second verse.",
            }],
            "covers": [],
        },
        "data/app_api.json": {
            "schema_version": 3, "primary_consumer": "StoryBoard",
            "songs": [{"id": "ST-0001", "title": "Fixture song",
                       "import_scope": "default_live"}],
        },
        "data/version_chains.json": {},
        "data/vm_transcribed.json": [{
            "uid": "fixture-memo", "title": "Fixture memo",
            "text": "A synthetic transcript long enough to search.",
        }],
        "01_source_manifests/voicememo/vm_matches.json": {
            "ST-0001": ["fixture-memo"],
        },
    }


class DashboardBuilderIOTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.scripts = self.root / "scripts"
        self.scripts.mkdir()
        for name in ("build_dashboard.py", "catalog_surface.py", "storyboard_contract.py"):
            shutil.copyfile(ROOT / "scripts" / name, self.scripts / name)
        self.cwd = self.root / "unrelated-working-directory"
        self.cwd.mkdir()
        self.output = self.root / OUTPUT_NAME

    def write_inputs(self):
        for relative, value in fixture_inputs().items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")

    def import_builder(self):
        return subprocess.run(
            [sys.executable, "-B", "-c",
             "import sys, importlib; sys.path.insert(0, sys.argv[1]); "
             "import build_dashboard; importlib.reload(build_dashboard)",
             str(self.scripts)],
            cwd=self.cwd, capture_output=True, text=True, timeout=30,
        )

    def test_import_without_inputs_does_not_create_dashboard(self):
        result = self.import_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.cwd.iterdir()), [])

    def test_import_and_reload_leave_existing_dashboard_untouched(self):
        self.write_inputs()
        self.output.write_bytes(b"Keep this dashboard exactly as it is.\n")
        before = self.output.stat()
        result = self.import_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.output.read_bytes(), b"Keep this dashboard exactly as it is.\n")
        after = self.output.stat()
        self.assertEqual(after.st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(after.st_ino, before.st_ino)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertEqual(list(self.cwd.iterdir()), [])

    def test_cli_builds_from_an_unrelated_working_directory(self):
        self.write_inputs()
        result = subprocess.run(
            [sys.executable, "-B", str(self.scripts / "build_dashboard.py")],
            cwd=self.cwd, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn(f"dashboard written, {self.output}", result.stdout)
        self.assertIn("1 searchable transcripts from 1 transcribed", result.stdout)
        page = self.output.read_text(encoding="utf-8")
        self.assertIn('"t": "Fixture song"', page)
        self.assertIn('"scope": "default_live"', page)
        self.assertIn('"s": "ST-0001"', page)
        self.assertIn('class="pill wk-write lane-work">write</span>', page)
        self.assertIn("Catalog vfixture.", page)
        self.assertNotIn("__DATA__", page)
        self.assertNotIn("__TX__", page)
        self.assertEqual(list(self.cwd.iterdir()), [])


class DashboardBuilderFunctionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "dashboard_builder_under_test", ROOT / "scripts" / "build_dashboard.py",
        )
        cls.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.builder)

    def build_fixture(self, inputs):
        return self.builder.build_payload(
            inputs["data/master_catalog.json"], inputs["data/app_api.json"],
            inputs["data/version_chains.json"], inputs["data/vm_transcribed.json"],
            inputs["01_source_manifests/voicememo/vm_matches.json"],
        )

    def test_build_and_render_are_io_free_and_use_each_payload(self):
        inputs = fixture_inputs()
        before = copy.deepcopy(inputs)
        with patch("builtins.open", side_effect=AssertionError("Unexpected file I/O")):
            payload = self.build_fixture(inputs)
            original_page = self.builder.render_dashboard(payload)
            self.assertEqual(inputs, before)
            inputs["data/master_catalog.json"]["songs"][0]["next_action"] = "Listen to the latest take."
            changed_payload = self.build_fixture(inputs)
            changed_page = self.builder.render_dashboard(changed_payload)
            self.assertEqual(self.builder.render_dashboard(payload), original_page)
        self.assertIn('class="pill wk-write lane-work">write</span>', original_page)
        self.assertIn('class="pill wk-listen lane-work">listen</span>', changed_page)
        self.assertEqual(changed_payload["data"][0]["nx"], "Listen to the latest take.")
        self.assertEqual(payload["memo_counts"], {
            "transcribed": 1, "matched": 1, "searchable": 1, "searchable_matched": 1,
        })

    def test_write_dashboard_uses_only_requested_destination(self):
        payload = self.build_fixture(fixture_inputs())
        with tempfile.TemporaryDirectory() as tmp:
            default = Path(tmp) / "default.html"
            default.write_bytes(b"Leave the default dashboard alone.")
            destination = Path(tmp) / "requested.html"
            with patch.object(self.builder, "OUT_PATH", default):
                page = self.builder.write_dashboard(payload, destination)
            self.assertEqual(destination.read_bytes(), page.encode("utf-8"))
            self.assertEqual(default.read_bytes(), b"Leave the default dashboard alone.")


if __name__ == "__main__":
    unittest.main()
