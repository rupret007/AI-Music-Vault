# Jeff Story Song Vault — Producer README
*How this system works, and how a future session resumes. Last updated: 2026-09-03 (usable catalog: local app_api.json after StoryBoard #20, spine rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived master_catalog.csv must match the spine. Song-level Logic-ready discovery is a control-room walk, not a second catalog. Cover-book leftover is the 93-cover walk (Trailer Swift originals stay 0; official-set originals stay 0). Private dashboard find-and-act on searchable matched memos; write/produce/listen starts on one highest-momentum match with bounded progress and collapsed secondary filters; browser-local resume stores only work kind + catalog ID and has an explicit Forget control; Logic keys/WAVs stay owner-only. Session Log #12 heading listed once. Resume from the latest Session Log H2, not Session 1. Local validate is the catalog gate; hosted empty-runner is not a catalog fail. Jeff-facing README/APPS.md are roles and counts only. Catalog-gate success output is roles and counts only).*

## Mission
Jeff does not need more songs. He needs the strongest songs he already wrote to be recognized, organized, protected, and FINISHED. Max 3 active songs (flagship / quick win / experimental). Every active song has one clear next action at three energy levels.

## Resume procedure (future sessions: START HERE)
1. This **repo** is the source of truth (not the old `claude/` Cowork copies). Read `00_control_room/Session Log.md`, `00_control_room/Priority Queue.md`, `00_control_room/Needs Jeff.md`, `data/master_catalog.json`.
2. Confirm the catalog: `python3 scripts/validate_catalog.py`. StoryBoard import: local `data/app_api.json` only — not `master_catalog.json`, not a remote URL (see `APPS.md` and `00_control_room/Vault to StoryBoard.md`). Band OS = StoryBoard, not StoryDesk/StoryOps. Nothing auto-posts.
3. Raw manifests live under `01_source_manifests/` (gdrive inventory + doc texts, voicememo matches).
4. Check `Music/Jeff Story Song Vault/Voice Memo Intake/` on jeffs-mac-mini-local for new files (Mac-local only; this repo holds no audio).
5. Continue from the **latest Session Log H2 pass** — its Next continuation point and honesty ledger. Do not resume from the first Session 1 "NOT done / next continuation point". Do not expand the three-song cap.
6. Dashboard session resume is convenience state, not the control-room handoff: it stores only schema version + work kind + catalog ID in this browser. **Forget** clears it. The latest Session Log remains authoritative.

## Structure (this repo)
```
00_control_room/    plan, queue, needs-jeff, logs, rights, Vault→StoryBoard pointer
01_source_manifests/ gdrive/ voicememo/ (inventories + lyric texts)
02_song_records/    per-song deep workups (only when a song goes active)
04_suno_experiments/  one brief per experiment
05_producer_briefs/   ST-0001, ST-0004, …
data/               master_catalog.json (spine) + app_api.json (StoryBoard import)
scripts/            validate_catalog.py · export_app_api.py · Mac-local workbench
events/             drop-file inbox for StoryBoard / Show Night / WebJam
```
Mac-local organized vault (00–99, working copies, intake audio) stays on Jeff's machine — never in this repo.

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

## Current state (2026-08-23)
Catalog v1.6: **150 entities / 126 originals** + 93 covers. Active (max 3): ST-0001 Turn Over The Flag (flagship), ST-0004 Manic (quick win), ST-0009 Long Long Drive (experimental). On deck: JS-0128 It's Alright. Protected opus: JS-0107 Blue Skies Fade. The campaign: **finish the 6-track Stalemate album** using Jeff's own Overdubs doc as the checklist. StoryBoard consumes `data/app_api.json`.
