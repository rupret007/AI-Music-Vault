#!/usr/bin/env python3
"""
Whisper Pass — transcribes every voice memo in the intake folder.

WHAT THIS DOES
  Reads every .m4a in "Voice Memo Intake", transcribes it with Whisper
  (running fully locally, nothing leaves this Mac), and writes one .txt
  transcript per memo into a new "03 Voice Memos/Transcripts" folder.
  It never touches, renames, or moves the original .m4a files.

  It's resumable: if you stop it (Ctrl+C, closed Terminal, whatever) and
  run it again, it skips any memo that already has a transcript and just
  keeps going where it left off.

HOW TO RUN
  1. Open Terminal.
  2. cd into this vault folder, e.g.:
       cd "/Users/jeffstory/Music/Jeff Story Song Vault"
  3. Run:
       python3 whisper_pass.py
     (make sure whisper_pass.py is sitting in that same folder — if you
     saved it somewhere else, just run "python3 /full/path/to/whisper_pass.py"
     instead, the script finds the vault folders on its own either way as
     long as the paths below match your setup, which they should.)

  This will take a while — 916 memos, probably several hours on a Mac
  mini's CPU with the "base.en" model. That's fine: it's designed to run
  in the background. Start it, let it churn (overnight is a good bet, or
  just leave the Terminal tab open while you do other stuff), and check
  back on progress any time — it prints a running count as it goes.

  If Terminal shows a "model download" step the very first time you run
  it — that's normal, Whisper downloads its model once (~150MB for
  base.en) then reuses it forever.

WHEN IT'S DONE
  Tell me (in the Claude chat) that it finished. I'll read the
  Transcripts folder and start using it to: find real hidden gems by
  their LYRICS instead of blind listening, capture the "Better Than Now"
  lyric for Sean, and re-attempt matching the ~290 still-unmatched memos
  against known songs.
"""

import os
import sys
import time
import json
import re

# ---- Paths (matches the vault structure already on this Mac) ----
VAULT = os.path.expanduser("~/Music/Jeff Story Song Vault")
INTAKE = os.path.join(VAULT, "Voice Memo Intake")
TRANSCRIPTS = os.path.join(VAULT, "03 Voice Memos", "Transcripts")
MANIFEST_PATH = os.path.join(TRANSCRIPTS, "_manifest.json")
ERROR_LOG = os.path.join(TRANSCRIPTS, "_errors.log")

MODEL_NAME = "base.en"  # good speed/accuracy balance for a first full pass


def safe_filename(name: str) -> str:
    name = re.sub(r"[^\w\s\-\.]", "", name).strip()
    name = re.sub(r"\s+", "_", name)
    return name[:150] if name else "untitled"


def main():
    if not os.path.isdir(INTAKE):
        print(f"ERROR: can't find the intake folder at:\n  {INTAKE}")
        print("Edit the VAULT path near the top of this script if your folder is elsewhere.")
        sys.exit(1)

    os.makedirs(TRANSCRIPTS, exist_ok=True)

    try:
        import whisper
    except ImportError:
        print("ERROR: the 'whisper' package isn't importable. If the Workbench install")
        print("errored, paste the error back to Claude. Otherwise try:")
        print("  python3 -m pip install --user --break-system-packages openai-whisper")
        sys.exit(1)

    memos = sorted(f for f in os.listdir(INTAKE) if f.lower().endswith(".m4a"))
    if not memos:
        print(f"No .m4a files found in {INTAKE} — nothing to do.")
        sys.exit(0)

    print(f"Found {len(memos)} memos. Loading Whisper model '{MODEL_NAME}' "
          f"(first run downloads it, ~150MB)...")
    model = whisper.load_model(MODEL_NAME)
    print("Model loaded. Starting transcription pass.\n")

    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)

    start_time = time.time()
    done = 0
    skipped = 0
    errors = 0

    for i, fname in enumerate(memos, 1):
        base = os.path.splitext(fname)[0]
        out_path = os.path.join(TRANSCRIPTS, safe_filename(base) + ".txt")

        if os.path.exists(out_path):
            skipped += 1
            continue

        src_path = os.path.join(INTAKE, fname)
        try:
            result = model.transcribe(src_path, fp16=False)
            text = result.get("text", "").strip()
            with open(out_path, "w") as f:
                f.write(text)
            manifest[fname] = {
                "transcript_file": os.path.basename(out_path),
                "chars": len(text),
                "language": result.get("language", "en"),
            }
            done += 1
        except Exception as e:
            errors += 1
            with open(ERROR_LOG, "a") as f:
                f.write(f"{fname}: {e}\n")

        if i % 5 == 0 or i == len(memos):
            elapsed = time.time() - start_time
            rate = done / elapsed if elapsed > 0 else 0
            remaining = len(memos) - i
            eta_min = (remaining / rate / 60) if rate > 0 else 0
            print(f"[{i}/{len(memos)}] done={done} skipped={skipped} errors={errors} "
                  f"— est. {eta_min:.0f} min remaining")
            with open(MANIFEST_PATH, "w") as f:
                json.dump(manifest, f, indent=2)

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nFinished. Transcribed {done} new memos, skipped {skipped} already done, "
          f"{errors} errors (see _errors.log).")
    print(f"Transcripts are in: {TRANSCRIPTS}")
    print("Tell Claude it's done and it'll take it from here.")


if __name__ == "__main__":
    main()
