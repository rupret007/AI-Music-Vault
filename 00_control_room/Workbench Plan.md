# THE WORKBENCH — approved 2026-08-19 ("ok awesome lets put this in here")
*Owner-local audio workflow, separate from the public repository's build/test gate.
The plan below records the approved pipeline; it is not proof that every tool is
installed or every pass has completed. Audio processing stays local; initial
package/model downloads need network access. The repository itself is public.*

## The stack and what each piece does
| Tool | License | Job in Jeff's pipeline |
|---|---|---|
| **Whisper** (OpenAI) | MIT | Transcribe all 916 voice memos → find gems by their LYRICS; capture the Better Than Now lyric; transcribe untitled ideas |
| **Demucs** (Meta) | MIT | Stem separation → split the 1999 Blue Skies Fade mixdown into vocals/drums/bass/guitar (THE OPUS restoration path); isolate Jeff's vocal/melody from rough memos |
| **Basic Pitch** (Spotify) | Apache-2.0 | Audio → MIDI: hummed memo melodies become MIDI to drop into Logic |
| **Chromaprint** (AcoustID) | LGPL | Audio fingerprinting → auto-cluster the "multiple mixes all over the place" into version families |
| **Matchering** | GPL (used as app) | Automated album mastering pass: level-match the 6 tracks + fix the true-peak clipping (all 4 measured bounces exceed 0 dBFS) |
| librosa/ffmpeg | (already in use) | Key/tempo/structure analysis |

## Optional owner-local setup (not needed for dashboard builds or CI)

The audio stack has no pinned dependency lock or tested Python-version matrix in
this repo. Check compatibility for each tool before installing; the repository's
Python 3.12 CI gate does not test these audio dependencies. Use an isolated virtual
environment with a Python version supported by the selected packages:

```bash
brew install ffmpeg chromaprint
python3 -m venv .venv
source .venv/bin/activate
python -m pip install openai-whisper demucs basic-pitch matchering
```
Requires Homebrew for the system tools. Do not override a system-managed Python;
use the virtual environment. Installation and model downloads were **NOT RUN** in
the October 2026 build/docs pass; sizes and runtime depend on the chosen models.

From this repository root, the owner-local entry points are
`python scripts/whisper_pass.py`, `python scripts/chromaprint_pass.py`, and
`python scripts/basic_pitch_pass.py`. They use the `VAULT` constant in each script,
not an environment variable, and expect an existing `Voice Memo Intake` directory
in the separate local vault. Review paths before running. No Demucs or Matchering
runner ships here. Do not run these audio passes as part of a metadata build.

## Planned audio passes (confirm local inputs and completion separately)
1. **Whisper pass** over all 916 memos → transcripts into the vault → hidden-gem search by lyric → re-match the 590 unmatched.
2. **Chromaprint pass** over Drive audio (staged in batches) → duplicate/version clustering → catalog lineages verified.
3. **Demucs on Blue Skies Fade (Final).mp3** (once the file reaches the intake folder) → stems → the opus restoration brief becomes buildable.
4. **Basic Pitch** on the top hidden gems → MIDI files delivered into the vault for Logic.
5. **Matchering dry-run** on the album bounces → a preview of the level-matched album (originals untouched; outputs to 06 Working Copies).

## Boundaries (unchanged)
Originals never modified — all outputs are new files in working folders. Nothing uploads anywhere; this whole stack is local. Suno remains the only external service, under the existing rules (Jeff's solo material, private, logged).

## Watchlist addition — 2026-08-20
**Stable Audio 3 (open-weight)** — licensed-data-trained instrumental/texture generator whose open models could run LOCALLY on the mini (private by construction). Candidate for a future Workbench experiment (M-series performance unverified). Propose-first rule applies: not installed.
