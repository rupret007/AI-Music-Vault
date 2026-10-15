#!/usr/bin/env python3
"""
Basic Pitch Pass — turns your best memo melodies into MIDI files for Logic.

WHAT THIS DOES
  Runs Spotify's Basic Pitch (installed with the Workbench) on a hand-picked
  list of your most important memos — the 9 recovered gems, the It's Alright
  takes, and the Blue Skies Fade beginning — and writes one .mid file per memo
  into "06 Working Copies/MIDI For Logic/".

  Reports a new export only after checking for a nonempty output file.
  Existing friendly files are skipped, never replaced. A failed export or
  missing source makes the command exit nonzero. File checks do not verify
  musical accuracy or Logic compatibility; actual Logic/MIDI export remains
  NOT RUN until a real file is verified separately.

  Drag any .mid into a Logic project and you get the melody/chords as editable
  notes — instant scratch track to build on. Originals untouched, as always.

HOW TO RUN (Terminal on the mac mini)
  cd "/Users/jeffstory/Music/Jeff Story Song Vault"
  python3 basic_pitch_pass.py

  Takes a few minutes total. First run may download the model once.
  If it says basic_pitch isn't importable, run:
    python3 -m pip install --user basic-pitch
  then try again. Tell Claude when it's done (or paste any error).
"""
import os
import stat
import sys
import tempfile

VAULT = os.path.expanduser("~/Music/Jeff Story Song Vault")
INTAKE = os.path.join(VAULT, "Voice Memo Intake")
OUT = os.path.join(VAULT, "06 Working Copies", "MIDI For Logic")

# (memo file, friendly output name)
TARGETS = [
    ("20220207 213742-172B0370.m4a", "Its Alright - vocals take (Feb 2022)"),
    ("20220210 181236-1B633469.m4a", "Its Alright - v1 take (Feb 2022)"),
    ("20251002 213050-E6FAD858.m4a", "I Fall Pretty Down - Crescent Dr 56 (Oct 2025)"),
    ("20230525 173806-D3F23CD4.m4a", "Been Loving You - Maxwell Dr 99 (May 2023)"),
    ("20210326 175544-7D6256BB.m4a", "Dont Put Your Life Away (Mar 2021)"),
    ("20221217 154751-DAC508CE.m4a", "Happy v1 (Dec 2022)"),
    ("20240305 211611-0C989E93.m4a", "A Place Where You Might - Crescent Dr 21 (Mar 2024)"),
    ("20230623 203422-ED7627B6.m4a", "Anyone Can See - Maxwell Dr 104 (Jun 2023)"),
    ("20191013 213641-3077FA20.m4a", "Chasing Rainbows (Oct 2019)"),
    ("20221217 171510-8248104D.m4a", "Find My Island (Dec 2022)"),
    ("20240727 142059-11B66CEA.m4a", "Blue Skies Beginning (Jul 2024)"),
    ("20240822 211138-11CAA9C0.m4a", "Blue Skies Fade full memo (Aug 2024)"),
]

def verify_output(path):
    """Check the artifact, not MIDI semantics or compatibility with Logic."""
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode) or info.st_size == 0:
        raise ValueError(f"expected a nonempty regular output file: {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    try:
        from basic_pitch.inference import predict_and_save
        from basic_pitch import ICASSP_2022_MODEL_PATH
    except ImportError:
        print("ERROR: basic_pitch not importable. Run:")
        print("  python3 -m pip install --user basic-pitch")
        return 1

    done, existing, missing, failed = 0, 0, 0, 0
    for fname, nice in TARGETS:
        src = os.path.join(INTAKE, fname)
        midi_out = os.path.join(OUT, nice + ".mid")
        try:
            if os.path.lexists(midi_out):
                verify_output(midi_out)
                print(f"existing/skipped: {nice}.mid")
                existing += 1
                continue
            if not os.path.isfile(src):
                print(f"skip (not found): {fname}")
                missing += 1
                continue
            # A fresh directory prevents stale default output from being
            # mistaken for this inference's result. Partial files are cleaned.
            with tempfile.TemporaryDirectory(prefix=".basic-pitch-", dir=OUT) as work:
                predict_and_save([src], work, save_midi=True, sonify_midi=False,
                                 save_model_outputs=False, save_notes=False,
                                 model_or_model_path=ICASSP_2022_MODEL_PATH)
                base = os.path.splitext(os.path.basename(src))[0]
                midi_in = os.path.join(work, base + "_basic_pitch.mid")
                verify_output(midi_in)
                # Same-filesystem link publishes without overwriting even if
                # another process creates the friendly destination meanwhile.
                os.link(midi_in, midi_out)
                verify_output(midi_out)
            print(f"OK: {nice}.mid")
            done += 1
        except Exception as e:
            print(f"FAILED {fname}: {e}")
            failed += 1

    print(f"\nResults: {done} newly exported MIDI files in '06 Working Copies/MIDI For Logic/' "
          f"({existing} existing/skipped, {missing} source files not found, {failed} failed).")
    print("File checks only; actual Logic/MIDI export remains NOT RUN "
          "until a real file is verified separately.")
    return 1 if failed or missing else 0

if __name__ == "__main__":
    sys.exit(main())
