# Jeff Story Song Vault — Producer README
*How this system works, and how a future session resumes. Last updated: 2026-08-18 (Session 1).*

## Mission
Jeff does not need more songs. He needs the strongest songs he already wrote to be recognized, organized, protected, and FINISHED. Max 3 active songs (flagship / quick win / experimental). Every active song has one clear next action at three energy levels.

## Resume procedure (future sessions: START HERE)
1. Read the claude.ai project docs: `claude/session-log.md`, `claude/priority-queue.md`, `claude/master-catalog.csv`, `claude/needs-jeff.md`. Do NOT re-scan sources already marked complete in the Session Log unless they changed.
2. The full raw manifests are in the project under `claude/manifests/` (gdrive-inventory.jsonl = 357 records with Drive file IDs; soundcloud-inventory.json; gdrive-doc-texts.md = 10 key docs in full).
3. Check `Music/Jeff Story Song Vault/Voice Memo Intake/` on jeffs-mac-mini-local for new files (folder access to ~/Music and ~/Documents was granted in Session 1; re-request if expired).
4. Continue from "NOT done / next continuation point" in the Session Log.

## Structure (cloud workspace `/home/claude/vault/`, mirrored to the project)
```
00_control_room/    README, master_catalog.{json,csv,xlsx}, covers_reference.csv,
                    Priority Queue, Needs Jeff, Session Log, Decision Log,
                    Access Gaps, Rights and AI Provenance
01_source_manifests/ gdrive/ soundcloud/ voicememo/ local/ logic/
02_song_records/    one folder per song, created only when a song goes active
03_unmatched_voice_memos/  (VM-YYYYMMDD-### ids, original names preserved)
04_suno_experiments/  one brief per experiment (see Rights doc)
05_producer_briefs/   ST-0001 Turn Over The Flag - Producer Brief.md
06_exports/           working copies only — originals are NEVER edited
99_source_links/      links/manifests, no bulk audio duplication
```

## Song IDs
`ST-####` Stalemate · `SD-####` Something Dirty · `JS-####` Jeff Story solo · `UNK-####` authorship uncertain. ST-01xx block = 2010 *My Mom Says We're Cool* album tracks. A "song" = the underlying composition; files/versions link to it. Covers live in `covers_reference.csv` and are never ranked against originals.

## Scoring (two numbers, never merged)
**Potential /100:** hook+melody 25, lyric 20, emotional truth/POV 20, structure+payoff 15, identity fit 10, replay/live 10.
**Readiness /100:** completeness 25, clarity of melody/chords/structure 20, source usability 15, manageable remaining work 25, recording feasibility 15.
Every score must cite concrete evidence. Confidence: high / medium / low / insufficient evidence.

## Safety rules (non-negotiable)
- Never delete, overwrite, rename, or relocate an original file. Never open-and-resave a Logic project. Work in copies under 06_exports.
- Audio honesty: every audio item carries a status (fully analyzed / partially sampled / metadata only / transcription only / unable to access / corrupt). **As of Session 1, everything is metadata-only — no audio has been listened to.** Transcriptions are clues, not lyrics.
- Recording quality ≠ song quality. Lyric-only evaluation happens before polish/stats can bias the ranking. Normalize loudness when comparing audio.
- Rights: classify every song; no external/AI upload of co-writes, covers, band masters, or uncertain material without established rights. No voice cloning without separate explicit permission. All AI contributions logged; Jeff's originals preserved verbatim next to any proposed edit.
- Suno: per-song one-time approval, default max 4 generations, private only, prefer demos over irreplaceable masters.

## Current state (end of Session 1)
Catalog v1: 113 originals + 93 covers. Active: ST-0001 Turn Over The Flag (flagship), ST-0004 Manic (quick win), ST-0009 Long Long Drive (experimental). The campaign: **finish the 6-track Stalemate album** using Jeff's own Overdubs doc as the checklist.
