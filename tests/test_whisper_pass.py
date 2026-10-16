"""Verify transcript reporting with mocked Whisper and temporary synthetic text.

These tests never create or read playable audio. Intake names are empty
placeholders; transcription is mocked.
"""
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "whisper_pass.py"
SYNTHETIC = "synthetic lyric text; not a listen"


def transcribe_text(text):
    def transcribe(src, fp16=False):
        return {"text": text, "language": "en"}
    return transcribe


class WhisperPassTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.vault = Path(temporary.name)
        self.intake = self.vault / "Voice Memo Intake"
        self.intake.mkdir()
        self.transcripts = self.vault / "03 Voice Memos" / "Transcripts"
        self.manifest = self.transcripts / "_manifest.json"
        self.errors = self.transcripts / "_errors.log"

    def add_source(self, name="synthetic.m4a"):
        path = self.intake / name
        path.touch()
        return path

    def transcript_path(self, name="synthetic.m4a"):
        return self.transcripts / (Path(name).stem + ".txt")

    def run_cli(self, effect=None, whisper_importable=True):
        transcribe = Mock(side_effect=effect)
        package = types.ModuleType("whisper")
        package.load_model = Mock(return_value=Mock(transcribe=transcribe))
        output = io.StringIO()
        with (
            patch.dict(sys.modules, {"whisper": package if whisper_importable else None}),
            patch("os.path.expanduser", return_value=str(self.vault)),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(output),
        ):
            try:
                runpy.run_path(str(SCRIPT), run_name="__main__")
            except SystemExit as error:
                status = error.code
            else:
                status = 0
        return status, output.getvalue(), transcribe, package.load_model

    def read_manifest(self):
        if not self.manifest.exists():
            return {}
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def test_success_requires_nonempty_transcript(self):
        self.add_source()
        status, output, transcribe, load_model = self.run_cli(transcribe_text(SYNTHETIC))
        destination = self.transcript_path()
        self.assertEqual(status, 0)
        self.assertEqual(destination.read_text(encoding="utf-8"), SYNTHETIC)
        self.assertEqual(self.read_manifest()["synthetic.m4a"]["chars"], len(SYNTHETIC))
        self.assertIn("1 newly transcribed", output)
        self.assertIn("0 failed", output)
        self.assertIn("transcription is not listening", output)
        self.assertNotIn("OK:", output)
        self.assertEqual(load_model.call_args.args, ("base.en",))
        self.assertEqual(transcribe.call_count, 1)
        self.assertEqual(transcribe.call_args.kwargs, {"fp16": False})

    def test_empty_asr_text_is_failure_and_writes_no_file(self):
        self.add_source()
        for text in ("", "   ", None, 12):
            with self.subTest(text=text):
                self.transcript_path().unlink(missing_ok=True)
                self.manifest.unlink(missing_ok=True)
                self.errors.unlink(missing_ok=True)
                status, output, transcribe, _ = self.run_cli(transcribe_text(text))
                self.assertEqual(status, 1)
                self.assertFalse(self.transcript_path().exists())
                self.assertEqual(self.read_manifest(), {})
                self.assertIn("1 failed", output)
                self.assertIn("0 newly transcribed", output)
                self.assertEqual(transcribe.call_count, 1)

    def test_existing_nonempty_transcript_is_skipped(self):
        self.add_source()
        self.transcripts.mkdir(parents=True)
        self.transcript_path().write_text("synthetic existing transcript", encoding="utf-8")
        status, output, transcribe, _ = self.run_cli(transcribe_text(SYNTHETIC))
        self.assertEqual(status, 0)
        transcribe.assert_not_called()
        self.assertEqual(
            self.transcript_path().read_text(encoding="utf-8"),
            "synthetic existing transcript",
        )
        self.assertIn("1 existing/skipped", output)
        self.assertIn("0 newly transcribed", output)

    def test_empty_existing_transcript_is_retried(self):
        self.add_source()
        self.transcripts.mkdir(parents=True)
        self.transcript_path().write_text("", encoding="utf-8")
        status, output, transcribe, _ = self.run_cli(transcribe_text(SYNTHETIC))
        self.assertEqual(status, 0)
        self.assertEqual(transcribe.call_count, 1)
        self.assertEqual(self.transcript_path().read_text(encoding="utf-8"), SYNTHETIC)
        self.assertIn("1 newly transcribed", output)
        self.assertIn("0 existing/skipped", output)

    def test_whitespace_existing_transcript_is_retried(self):
        self.add_source()
        self.transcripts.mkdir(parents=True)
        self.transcript_path().write_text(" \n\t ", encoding="utf-8")
        status, _, transcribe, _ = self.run_cli(transcribe_text(SYNTHETIC))
        self.assertEqual(status, 0)
        self.assertEqual(transcribe.call_count, 1)
        self.assertEqual(self.transcript_path().read_text(encoding="utf-8"), SYNTHETIC)

    def test_inference_exception_is_failure_and_cleans_incomplete_output(self):
        self.add_source()

        def fail(src, fp16=False):
            self.transcripts.mkdir(parents=True, exist_ok=True)
            self.transcript_path().write_text("", encoding="utf-8")
            raise RuntimeError("synthetic inference failure")

        status, output, _, _ = self.run_cli(fail)
        self.assertEqual(status, 1)
        self.assertIn("synthetic inference failure", output + self.errors.read_text(encoding="utf-8"))
        self.assertFalse(self.transcript_path().exists())
        self.assertEqual(self.read_manifest(), {})
        self.assertIn("0 newly transcribed", output)

    def test_missing_source_file_is_nonzero_without_inference(self):
        self.intake.mkdir(exist_ok=True)
        directory = self.intake / "synthetic.m4a"
        directory.mkdir()
        status, output, transcribe, _ = self.run_cli(transcribe_text(SYNTHETIC))
        self.assertEqual(status, 1)
        transcribe.assert_not_called()
        self.assertIn("1 failed", output)
        self.assertFalse(self.transcript_path().exists())

    def test_mixed_run_counts_only_verified_outputs_and_exits_nonzero(self):
        self.add_source("first.m4a")
        self.add_source("second.m4a")

        def mixed(src, fp16=False):
            if Path(src).name == "first.m4a":
                return {"text": SYNTHETIC, "language": "en"}
            return {"text": "", "language": "en"}

        status, output, transcribe, _ = self.run_cli(mixed)
        self.assertEqual(status, 1)
        self.assertEqual(transcribe.call_count, 2)
        self.assertEqual(self.transcript_path("first.m4a").read_text(encoding="utf-8"), SYNTHETIC)
        self.assertFalse(self.transcript_path("second.m4a").exists())
        self.assertIn("1 newly transcribed", output)
        self.assertIn("1 failed", output)
        self.assertIn("first.m4a", self.read_manifest())
        self.assertNotIn("second.m4a", self.read_manifest())

    def test_missing_intake_exits_nonzero_without_whisper(self):
        self.intake.rmdir()
        status, output, transcribe, load_model = self.run_cli(transcribe_text(SYNTHETIC))
        self.assertEqual(status, 1)
        transcribe.assert_not_called()
        load_model.assert_not_called()
        self.assertIn("can't find the intake folder", output)

    def test_missing_whisper_exits_nonzero(self):
        self.add_source()
        status, output, transcribe, load_model = self.run_cli(
            transcribe_text(SYNTHETIC), whisper_importable=False,
        )
        self.assertEqual(status, 1)
        transcribe.assert_not_called()
        load_model.assert_not_called()
        self.assertIn("whisper", output.lower())
        self.assertFalse(self.transcript_path().exists())


if __name__ == "__main__":
    unittest.main()
