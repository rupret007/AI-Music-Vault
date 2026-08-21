#!/usr/bin/env python3
"""
Basic Pitch Pass — turns your best memo melodies into MIDI files for Logic.

WHAT THIS DOES
  Runs Spotify's Basic Pitch (installed with the Workbench) on a hand-picked
  list of your most important memos — the 9 recovered gems, the It's Alright
  takes, and the Blue Skies Fade beginning — and writes one .mid file per memo
  into "06 Working Copies/MIDI For Logic/".

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
import os, sys

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

def main():
    os.makedirs(OUT, exist_ok=True)
    try:
        from basic_pitch.inference import predict_and_save
        from basic_pitch import ICASSP_2022_MODEL_PATH
    except ImportError:
        print("ERROR: basic_pitch not importable. Run:")
        print("  python3 -m pip install --user basic-pitch")
        sys.exit(1)

    done, missing = 0, 0
    for fname, nice in TARGETS:
        src = os.path.join(INTAKE, fname)
        if not os.path.exists(src):
            print(f"skip (not found): {fname}")
            missing += 1
            continue
        # predict_and_save writes <input>_basic_pitch.mid into OUT
        try:
            predict_and_save([src], OUT, save_midi=True, sonify_midi=False,
                             save_model_outputs=False, save_notes=False,
                             model_or_model_path=ICASSP_2022_MODEL_PATH)
            # rename to the friendly name
            base = os.path.splitext(os.path.basename(src))[0]
            midi_in = os.path.join(OUT, base + "_basic_pitch.mid")
            midi_out = os.path.join(OUT, nice + ".mid")
            if os.path.exists(midi_in) and not os.path.exists(midi_out):
                os.rename(midi_in, midi_out)
            print(f"OK: {nice}.mid")
            done += 1
        except Exception as e:
            print(f"FAILED {fname}: {e}")

    print(f"\nDone: {done} MIDI files in '06 Working Copies/MIDI For Logic/' "
          f"({missing} source files not found).")
    print("Drag any .mid straight into Logic. Tell Claude when you've run this.")

if __name__ == "__main__":
    main()
