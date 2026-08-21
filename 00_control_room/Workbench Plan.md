# THE WORKBENCH — approved 2026-08-19 ("ok awesome lets put this in here")
*Free, open-source AI audio tools running privately on Jeff's mac mini. Nothing leaves the machine; no subscriptions. This completes the memo-to-demo pipeline.*

## The stack and what each piece does
| Tool | License | Job in Jeff's pipeline |
|---|---|---|
| **Whisper** (OpenAI) | MIT | Transcribe all 916 voice memos → find gems by their LYRICS; capture the Better Than Now lyric; transcribe untitled ideas |
| **Demucs** (Meta) | MIT | Stem separation → split the 1999 Blue Skies Fade mixdown into vocals/drums/bass/guitar (THE OPUS restoration path); isolate Jeff's vocal/melody from rough memos |
| **Basic Pitch** (Spotify) | Apache-2.0 | Audio → MIDI: hummed memo melodies become MIDI to drop into Logic |
| **Chromaprint** (AcoustID) | LGPL | Audio fingerprinting → auto-cluster the "multiple mixes all over the place" into version families |
| **Matchering** | GPL (used as app) | Automated album mastering pass: level-match the 6 tracks + fix the true-peak clipping (all 4 measured bounces exceed 0 dBFS) |
| librosa/ffmpeg | (already in use) | Key/tempo/structure analysis |

## Install (ONE paste into Terminal on the mac mini — Jeff runs this; ~10-15 min, mostly downloads)
```
brew install ffmpeg chromaprint && python3 -m pip install --user openai-whisper demucs basic-pitch matchering
```
Notes: needs Homebrew (brew.sh if missing). If `pip` complains about "externally managed environment," add `--break-system-packages`. First Whisper/Demucs runs download their models once (~1-3 GB total). I'll verify everything and handle version issues in the session after install — Jeff just pastes and tells me when it's done (or if it errored — paste the error, I'll fix the command).

## What happens the session after install (no Jeff time needed)
1. **Whisper pass** over all 916 memos → transcripts into the vault → hidden-gem search by lyric → re-match the 590 unmatched.
2. **Chromaprint pass** over Drive audio (staged in batches) → duplicate/version clustering → catalog lineages verified.
3. **Demucs on Blue Skies Fade (Final).mp3** (once the file reaches the intake folder) → stems → the opus restoration brief becomes buildable.
4. **Basic Pitch** on the top hidden gems → MIDI files delivered into the vault for Logic.
5. **Matchering dry-run** on the album bounces → a preview of the level-matched album (originals untouched; outputs to 06 Working Copies).

## Boundaries (unchanged)
Originals never modified — all outputs are new files in working folders. Nothing uploads anywhere; this whole stack is local. Suno remains the only external service, under the existing rules (Jeff's solo material, private, logged).

## Watchlist addition — 2026-08-20
**Stable Audio 3 (open-weight)** — licensed-data-trained instrumental/texture generator whose open models could run LOCALLY on the mini (private by construction). Candidate for a future Workbench experiment (M-series performance unverified). Propose-first rule applies: not installed.
