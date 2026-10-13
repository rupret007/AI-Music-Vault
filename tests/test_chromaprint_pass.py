"""Exercise the CLI with synthetic fingerprints; never create or read audio."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "chromaprint_pass.py"
FINGERPRINT = list(range(32))


def result(payload=None, returncode=0):
    if payload is None:
        payload = {"fingerprint": FINGERPRINT}
    return subprocess.CompletedProcess(
        ["fpcalc"], returncode, json.dumps(payload), "synthetic diagnostic",
    )


class ChromaprintPassTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.vault = Path(temporary.name)
        self.output = self.vault / "03 Voice Memos"
        self.output.mkdir()
        self.cache_path = self.output / "_fingerprints.json"
        self.clusters_path = self.output / "audio_fingerprint_clusters.json"

    def run_cli(self, files, responses):
        output = io.StringIO()
        with (
            patch("os.path.expanduser", return_value=str(self.vault)),
            patch("os.listdir", return_value=files),
            patch("shutil.which", return_value="/mock/fpcalc"),
            patch("subprocess.run", side_effect=responses) as run,
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(output),
        ):
            try:
                runpy.run_path(str(SCRIPT), run_name="__main__")
            except SystemExit as error:
                status = error.code
            else:
                status = 0
        return status, output.getvalue(), run

    def read_cache(self):
        return json.loads(self.cache_path.read_text())

    def test_failed_process_is_checked_before_parsing_even_valid_stdout(self):
        with patch("json.loads", wraps=json.loads) as loads:
            status, output, _ = self.run_cli(["failed.m4a"], [result(returncode=1)])
        loads.assert_not_called()
        self.assertNotIn("failed.m4a", self.read_cache())
        self.assertEqual(status, 1)
        self.assertIn("failed.m4a", output)
        self.assertIn("exit 1", output)

    def test_process_and_json_failures_are_not_cached_and_can_be_retried(self):
        failures = [
            subprocess.TimeoutExpired("fpcalc", 60),
            OSError("synthetic launch failure"),
            subprocess.CompletedProcess(["fpcalc"], 0, "not JSON", ""),
            result(returncode=2),
        ]
        for failure in failures:
            with self.subTest(failure=failure):
                self.cache_path.unlink(missing_ok=True)
                status, output, _ = self.run_cli(["retry.m4a"], [failure])
                self.assertEqual(self.read_cache(), {})
                self.assertEqual(status, 1)
                self.assertIn("1 file(s) failed", output)
                status, _, run = self.run_cli(["retry.m4a"], [result()])
                self.assertEqual(status, 0)
                self.assertEqual(run.call_count, 1)
                self.assertEqual(self.read_cache(), {"retry.m4a": FINGERPRINT})

    def test_invalid_success_payloads_are_failures(self):
        payloads = [{}, [], None, {"fingerprint": []}, {"fingerprint": None},
                    {"fingerprint": "1,2,3"}, {"fingerprint": [1, "2"]},
                    {"fingerprint": [True]}, {"fingerprint": [1.5]}]
        for payload in payloads:
            with self.subTest(payload=payload):
                response = subprocess.CompletedProcess(["fpcalc"], 0, json.dumps(payload), "")
                status, _, _ = self.run_cli(["invalid.m4a"], [response])
                self.assertEqual(self.read_cache(), {})
                self.assertEqual(status, 1)

    def test_invalid_legacy_cache_entries_are_retried(self):
        for fingerprint in ([], None, "1,2,3", [True], [1, "2"], {}, [1.5]):
            with self.subTest(fingerprint=fingerprint):
                self.cache_path.write_text(json.dumps({"legacy.m4a": fingerprint}))
                status, _, run = self.run_cli(["legacy.m4a"], [result()])
                self.assertEqual(run.call_count, 1)
                self.assertEqual(status, 0)
                self.assertEqual(self.read_cache(), {"legacy.m4a": FINGERPRINT})

    def test_failed_retry_removes_legacy_empty_entry(self):
        self.cache_path.write_text(json.dumps({"legacy.m4a": []}))
        status, _, run = self.run_cli(["legacy.m4a"], [result(returncode=1)])
        self.assertEqual(run.call_count, 1)
        self.assertEqual(self.read_cache(), {})
        self.assertEqual(status, 1)

    def test_mixed_pass_preserves_successes_and_retries_only_failure(self):
        files = ["a.m4a", "b.m4a", "c.m4a"]
        status, output, run = self.run_cli(files, [result(), result(returncode=1), result()])
        self.assertEqual(run.call_count, 3)
        self.assertEqual(self.read_cache(), {"a.m4a": FINGERPRINT, "c.m4a": FINGERPRINT})
        self.assertEqual(status, 1)
        self.assertNotIn("Done:", output)
        self.assertFalse(self.clusters_path.exists())
        status, _, run = self.run_cli(files, [result()])
        self.assertEqual(status, 0)
        run.assert_called_once_with(
            ["/mock/fpcalc", "-raw", "-length", "120", "-json",
             str(self.vault / "Voice Memo Intake" / "b.m4a")],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(json.loads(self.clusters_path.read_text())["clusters"], [files])

    def test_failed_pass_leaves_previous_clusters_untouched(self):
        previous = b'{"clusters": [["old-a.m4a", "old-b.m4a"]]}\n'
        self.clusters_path.write_bytes(previous)
        status, _, _ = self.run_cli(["failed.m4a"], [result(returncode=1)])
        self.assertEqual(self.clusters_path.read_bytes(), previous)
        self.assertEqual(status, 1)

    def test_complete_cache_skips_subprocess_and_still_clusters(self):
        files = ["a.m4a", "b.m4a"]
        self.cache_path.write_text(json.dumps(dict.fromkeys(files, FINGERPRINT)))
        status, _, run = self.run_cli(files, [])
        run.assert_not_called()
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(self.clusters_path.read_text())["clusters"], [files])

    def test_valid_short_fingerprint_is_cached_but_not_clustered(self):
        status, _, _ = self.run_cli(["short.m4a"], [result({"fingerprint": [0, 1]})])
        self.assertEqual(status, 0)
        self.assertEqual(self.read_cache(), {"short.m4a": [0, 1]})
        self.assertEqual(json.loads(self.clusters_path.read_text())["clusters"], [])
        status, _, run = self.run_cli(["short.m4a"], [])
        self.assertEqual(status, 0)
        run.assert_not_called()

    def test_checkpoint_keeps_successes_without_failed_entries(self):
        files = [f"memo-{i:02d}.m4a" for i in range(26)]

        def check_checkpoint(*args, **kwargs):
            cached = self.read_cache()
            self.assertEqual(len(cached), 24)
            self.assertNotIn(files[0], cached)
            return result()

        responses = iter([result(returncode=1)] + [result()] * 24)

        def respond(*args, **kwargs):
            return next(responses, None) or check_checkpoint()

        status, _, run = self.run_cli(files, respond)
        self.assertEqual(run.call_count, 26)
        self.assertEqual(status, 1)
        self.assertEqual(len(self.read_cache()), 25)
        self.assertNotIn(files[0], self.read_cache())


if __name__ == "__main__":
    unittest.main()
