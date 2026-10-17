"""Verify export reporting with mocked inference and temporary synthetic bytes.

These tests do not generate playable MIDI or verify Logic compatibility.
"""
import contextlib
import errno
import importlib.util
import io
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "basic_pitch_pass.py"
SPEC = importlib.util.spec_from_file_location("basic_pitch_pass", SCRIPT)
pitch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pitch)
SYNTHETIC = b"synthetic output; not playable MIDI"


class BasicPitchPassTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="tmp_basic_pitch_", dir=SCRIPT.parent.parent)
        self.addCleanup(temporary.cleanup)
        self.vault = Path(temporary.name)
        self.intake = self.vault / "Voice Memo Intake"
        self.intake.mkdir()
        self.out = self.vault / "06 Working Copies" / "MIDI For Logic"
        self.out.mkdir(parents=True)
        self.targets = [("synthetic.m4a", "Synthetic melody")]
        (self.intake / self.targets[0][0]).touch()
        self.destination = self.out / "Synthetic melody.mid"

    def write_output(self, sources, output, **kwargs):
        path = Path(output) / (Path(sources[0]).stem + "_basic_pitch.mid")
        path.write_bytes(SYNTHETIC)

    def run_pass(self, effect=None, cli=False, dependency_available=True):
        predict = Mock(side_effect=effect)
        package = types.ModuleType("basic_pitch")
        package.ICASSP_2022_MODEL_PATH = "synthetic-model"
        inference = types.ModuleType("basic_pitch.inference")
        inference.predict_and_save = predict
        modules = {"basic_pitch": package, "basic_pitch.inference": inference}
        if not dependency_available:
            modules = dict.fromkeys(modules)
        output = io.StringIO()
        with (
            patch.dict(sys.modules, modules),
            patch.multiple(pitch, INTAKE=str(self.intake), OUT=str(self.out),
                           TARGETS=self.targets),
            patch("os.path.expanduser", return_value=str(self.vault)),
            contextlib.redirect_stdout(output),
        ):
            if cli:
                try:
                    runpy.run_path(str(SCRIPT), run_name="__main__")
                except SystemExit as error:
                    status = error.code
                else:
                    status = 0
            else:
                status = pitch.main()
        return status, output.getvalue(), predict

    def assert_no_success(self, output):
        self.assertNotIn("OK:", output)
        self.assertIn("0 newly exported", output)

    def test_success_requires_nonempty_friendly_output(self):
        status, output, predict = self.run_pass(self.write_output)
        self.assertEqual(self.destination.read_bytes(), SYNTHETIC)
        self.assertEqual(status, 0)
        self.assertIn("OK: Synthetic melody.mid", output)
        self.assertIn("1 newly exported", output)
        self.assertEqual(predict.call_count, 1)
        self.assertEqual(predict.call_args.kwargs, {
            "save_midi": True, "sonify_midi": False,
            "save_model_outputs": False, "save_notes": False,
            "model_or_model_path": "synthetic-model",
        })
        self.assertEqual(list(self.out.iterdir()), [self.destination])

    def test_missing_output_is_failure(self):
        status, output, _ = self.run_pass()
        self.assertEqual(status, 1)
        self.assertIn("FAILED", output)
        self.assert_no_success(output)
        self.assertFalse(self.destination.exists())

    def test_output_with_unexpected_filename_is_failure_and_is_cleaned(self):
        def unexpected(sources, output, **kwargs):
            (Path(output) / "unexpected.mid").write_bytes(SYNTHETIC)
        status, output, predict = self.run_pass(unexpected)
        self.assertEqual(status, 1)
        predict.assert_called_once()
        self.assert_no_success(output)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_empty_output_is_failure(self):
        def empty(sources, output, **kwargs):
            (Path(output) / "synthetic_basic_pitch.mid").touch()
        status, output, _ = self.run_pass(empty)
        self.assertEqual(status, 1)
        self.assert_no_success(output)
        self.assertFalse(self.destination.exists())

    def test_directory_output_is_failure(self):
        def directory(sources, output, **kwargs):
            (Path(output) / "synthetic_basic_pitch.mid").mkdir()
        status, output, _ = self.run_pass(directory)
        self.assertEqual(status, 1)
        self.assert_no_success(output)

    def test_symlink_output_is_rejected_without_changing_target(self):
        target = self.vault / "synthetic-link-target.mid"
        for broken in (False, True):
            with self.subTest(broken=broken):
                if broken:
                    target.unlink()
                else:
                    target.write_bytes(SYNTHETIC)
                def symlink(sources, output, **kwargs):
                    (Path(output) / "synthetic_basic_pitch.mid").symlink_to(target)
                status, output, predict = self.run_pass(symlink)
                self.assertEqual(status, 1)
                predict.assert_called_once()
                self.assert_no_success(output)
                self.assertEqual(list(self.out.iterdir()), [])
                self.assertEqual(target.exists(), not broken)
                if not broken:
                    self.assertEqual(target.read_bytes(), SYNTHETIC)

    def test_inference_exception_is_failure_and_cleans_partial_output(self):
        def fail(*args, **kwargs):
            self.write_output(*args, **kwargs)
            raise RuntimeError("synthetic inference failure")
        status, output, _ = self.run_pass(fail)
        self.assertEqual(status, 1)
        self.assertIn("synthetic inference failure", output)
        self.assert_no_success(output)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_existing_friendly_file_is_preserved_and_skipped(self):
        self.destination.write_bytes(b"synthetic existing file")
        status, output, predict = self.run_pass(self.write_output)
        self.assertEqual(status, 0)
        predict.assert_not_called()
        self.assertEqual(self.destination.read_bytes(), b"synthetic existing file")
        self.assertIn("existing/skipped", output)
        self.assert_no_success(output)

    def test_existing_output_needs_neither_source_nor_basic_pitch(self):
        self.destination.write_bytes(SYNTHETIC)
        (self.intake / self.targets[0][0]).unlink()
        status, output, predict = self.run_pass(dependency_available=False)
        self.assertEqual(status, 0)
        predict.assert_not_called()
        self.assertEqual(self.destination.read_bytes(), SYNTHETIC)
        self.assertIn("1 existing/skipped", output)
        self.assertIn("0 source files not found", output)
        self.assertNotIn("not importable", output)
        self.assert_no_success(output)

    def test_invalid_existing_destination_is_preserved_and_fails(self):
        for directory in (False, True):
            with self.subTest(directory=directory):
                if directory:
                    self.destination.unlink()
                    self.destination.mkdir()
                else:
                    self.destination.touch()
                status, output, predict = self.run_pass(self.write_output)
                self.assertEqual(status, 1)
                predict.assert_not_called()
                self.assertTrue(self.destination.exists())
                self.assert_no_success(output)

    def test_existing_symlink_is_preserved_and_fails(self):
        target = self.vault / "synthetic-existing-target.mid"
        for broken in (False, True):
            with self.subTest(broken=broken):
                if broken:
                    target.unlink()
                else:
                    target.write_bytes(SYNTHETIC)
                self.destination.symlink_to(target)
                status, output, predict = self.run_pass(self.write_output)
                self.assertEqual(status, 1)
                predict.assert_not_called()
                self.assert_no_success(output)
                self.assertTrue(self.destination.is_symlink())
                self.assertEqual(self.destination.readlink(), target)
                self.assertEqual(target.exists(), not broken)
                if not broken:
                    self.assertEqual(target.read_bytes(), SYNTHETIC)
                self.destination.unlink()

    def test_stale_default_output_is_not_claimed_as_new(self):
        stale = self.out / "synthetic_basic_pitch.mid"
        stale.write_bytes(SYNTHETIC)
        status, output, _ = self.run_pass()
        self.assertEqual(status, 1)
        self.assert_no_success(output)
        self.assertEqual(stale.read_bytes(), SYNTHETIC)
        self.assertFalse(self.destination.exists())

    def test_destination_created_during_inference_is_not_overwritten(self):
        def race(*args, **kwargs):
            self.write_output(*args, **kwargs)
            self.destination.write_bytes(b"another synthetic export")
        status, output, _ = self.run_pass(race)
        self.assertEqual(status, 1)
        self.assert_no_success(output)
        self.assertEqual(self.destination.read_bytes(), b"another synthetic export")

    def test_publication_error_fails_and_cleans_inference_output(self):
        for error in (PermissionError("synthetic publication denied"),
                      OSError(errno.ENOSPC, "synthetic disk full")):
            with self.subTest(error=error):
                with patch.object(pitch.os, "link", side_effect=error):
                    status, output, predict = self.run_pass(self.write_output)
                self.assertEqual(status, 1)
                predict.assert_called_once()
                self.assertIn(str(error), output)
                self.assert_no_success(output)
                self.assertEqual(list(self.out.iterdir()), [])

    def test_output_directory_error_returns_nonzero_without_inference(self):
        with patch.object(pitch.os, "makedirs", side_effect=PermissionError(
                "synthetic output directory denied")):
            status, output, predict = self.run_pass(self.write_output)
        self.assertEqual(status, 1)
        predict.assert_not_called()
        self.assertIn("ERROR", output)
        self.assertIn("synthetic output directory denied", output)
        self.assertNotIn("OK:", output)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_temporary_directory_error_returns_nonzero_without_inference(self):
        with patch.object(pitch.tempfile, "TemporaryDirectory",
                          side_effect=PermissionError("synthetic staging denied")):
            status, output, predict = self.run_pass(self.write_output)
        self.assertEqual(status, 1)
        predict.assert_not_called()
        self.assertIn("synthetic staging denied", output)
        self.assert_no_success(output)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_temporary_cleanup_error_is_reported_without_success(self):
        temporary_directory = tempfile.TemporaryDirectory
        @contextlib.contextmanager
        def cleanup_failure(*args, **kwargs):
            with temporary_directory(*args, **kwargs) as work:
                yield work
            raise PermissionError("synthetic staging cleanup denied")
        with patch.object(pitch.tempfile, "TemporaryDirectory", cleanup_failure):
            status, output, predict = self.run_pass(self.write_output)
        self.assertEqual(status, 1)
        predict.assert_called_once()
        self.assertIn("synthetic staging cleanup denied", output)
        self.assertIn("1 failed", output)
        self.assert_no_success(output)
        self.assertEqual(self.destination.read_bytes(), SYNTHETIC)
        self.assertEqual(list(self.out.iterdir()), [self.destination])

    def test_output_removed_during_cleanup_is_not_reported_as_success(self):
        temporary_directory = tempfile.TemporaryDirectory
        @contextlib.contextmanager
        def remove_during_cleanup(*args, **kwargs):
            with temporary_directory(*args, **kwargs) as work:
                yield work
            self.destination.unlink()
        with patch.object(pitch.tempfile, "TemporaryDirectory", remove_during_cleanup):
            status, output, predict = self.run_pass(self.write_output)
        self.assertEqual(status, 1)
        predict.assert_called_once()
        self.assertIn("1 failed", output)
        self.assert_no_success(output)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_missing_source_is_nonzero_without_inference(self):
        (self.intake / self.targets[0][0]).unlink()
        status, output, predict = self.run_pass()
        self.assertEqual(status, 1)
        predict.assert_not_called()
        self.assertIn("1 source files not found", output)
        self.assert_no_success(output)

    def test_missing_source_is_reported_without_basic_pitch(self):
        (self.intake / self.targets[0][0]).unlink()
        status, output, predict = self.run_pass(dependency_available=False)
        self.assertEqual(status, 1)
        predict.assert_not_called()
        self.assertIn("1 source files not found", output)
        self.assertIn("0 failed", output)
        self.assertNotIn("not importable", output)
        self.assert_no_success(output)

    def test_missing_dependency_reports_failure_with_installation_guidance(self):
        status, output, predict = self.run_pass(dependency_available=False)
        self.assertEqual(status, 1)
        predict.assert_not_called()
        self.assertIn("python3 -m pip install --user basic-pitch", output)
        self.assertIn("1 failed", output)
        self.assert_no_success(output)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_mixed_run_counts_only_verified_outputs_and_exits_nonzero(self):
        self.targets.append(("second.m4a", "Second melody"))
        (self.intake / "second.m4a").touch()
        def mixed(sources, output, **kwargs):
            if Path(sources[0]).name == "synthetic.m4a":
                self.write_output(sources, output, **kwargs)
        status, output, predict = self.run_pass(mixed)
        self.assertEqual(status, 1)
        self.assertEqual(predict.call_count, 2)
        self.assertEqual(output.count("OK:"), 1)
        self.assertIn("1 newly exported", output)
        self.assertIn("1 failed", output)
        self.assertEqual(self.destination.read_bytes(), SYNTHETIC)
        self.assertFalse((self.out / "Second melody.mid").exists())

    def test_inference_failure_does_not_prevent_later_success(self):
        self.targets.append(("second.m4a", "Second melody"))
        (self.intake / "second.m4a").touch()
        def first_fails(sources, output, **kwargs):
            self.write_output(sources, output, **kwargs)
            if Path(sources[0]).name == "synthetic.m4a":
                raise RuntimeError("synthetic first inference failure")
        status, output, predict = self.run_pass(first_fails)
        second_destination = self.out / "Second melody.mid"
        self.assertEqual(status, 1)
        self.assertEqual(predict.call_count, 2)
        self.assertIn("synthetic first inference failure", output)
        self.assertNotIn("OK: Synthetic melody.mid", output)
        self.assertIn("OK: Second melody.mid", output)
        self.assertIn("1 newly exported", output)
        self.assertIn("1 failed", output)
        self.assertEqual(second_destination.read_bytes(), SYNTHETIC)
        self.assertEqual(list(self.out.iterdir()), [second_destination])

    def test_cli_propagates_success_missing_output_and_exception_status(self):
        # Use configured names only inside the temporary vault; no real inputs.
        for fname, _ in pitch.TARGETS:
            (self.intake / fname).touch()
        for effect, expected in ((None, 1), (RuntimeError("synthetic failure"), 1),
                                 (self.write_output, 0)):
            with self.subTest(effect=effect):
                status, output, predict = self.run_pass(effect, cli=True)
                self.assertEqual(status, expected)
                self.assertEqual(predict.call_count, len(pitch.TARGETS))
                if expected:
                    self.assert_no_success(output)
                else:
                    self.assertEqual(output.count("OK:"), len(pitch.TARGETS))


if __name__ == "__main__":
    unittest.main()
