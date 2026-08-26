# AI Music Vault — Jeff Story

**27 years of songwriting, organized, scored, and moving toward finished.**

This is the working brain of the Jeff Story catalog: 150 song entities spanning 1999–2026 across Stalemate, Something Dirty, Trailer Swift, Rad Dad, and solo work — plus the tooling that found, matched, scored, and keeps track of all of it.

> ⚠️ **Private repository.** Contains unreleased album material, personal lyrics, collaborators' compositions (Dustin Duffy, Sean, Paco Estrada, Greg Baldia), and home-address strings inside voice-memo titles. Not for public distribution. Audio masters are deliberately **not** stored here — they live in the local vault and Google Drive.

---

## Start here

| If you want to… | Open |
|---|---|
| Know what to work on next | [`00_control_room/Priority Queue.md`](00_control_room/Priority%20Queue.md) |
| See the whole plan | [`00_control_room/THE PLAN.md`](00_control_room/THE%20PLAN.md) |
| Know what's *alive* vs. sleeping | [`00_control_room/What's Alive — Momentum Index.md`](00_control_room/What's%20Alive%20—%20Momentum%20Index.md) |
| Browse every song interactively | `Jeff Story Song Vault Dashboard.html` (open in any browser) |
| Understand the songs as a body of work | [`00_control_room/Song Map.md`](00_control_room/Song%20Map.md) |
| Co-write with an AI without it sounding like AI | [`00_control_room/Jeff Story Style Guide.md`](00_control_room/Jeff%20Story%20Style%20Guide.md) |
| See what needs Jeff's answer | [`00_control_room/Needs Jeff.md`](00_control_room/Needs%20Jeff.md) |
| Know why any decision was made | [`00_control_room/Decision Log.md`](00_control_room/Decision%20Log.md) |
| Feed StoryBoard (band OS) | [`data/app_api.json`](data/app_api.json) — mapping in [`APPS.md`](APPS.md) and [`00_control_room/Vault to StoryBoard.md`](00_control_room/Vault%20to%20StoryBoard.md) |
| Confirm the catalog isn't broken | `python3 scripts/validate_catalog.py` |

## Verify safely

Run the same offline gates used by catalog validation:

```bash
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests -v
python3 scripts/export_app_api.py --check
```

These checks read the committed catalog metadata and StoryBoard export only.
They do not open or upload audio, modify originals, or contact an AI service.
Keep the repository and its test output private because catalog metadata can
still contain unreleased, personal, collaborator, or location information.
StoryBoard consumes a local `data/app_api.json` — not the spine, not a remote
URL, and not a public catalog dump. Nothing auto-posts.

## The three lanes (+ on deck)

- **Flagship** — Turn Over The Flag (mix v1.6, two overdubs left)
- **Quick win** — Manic (one overdub: lead guitar on choruses + solos)
- **Experimental** — Long Long Drive (Suno arrangement test queued)
- **On deck** — It's Alright (in the live set, lyric ~85% recovered, unrecorded)
- **The Opus** — Blue Skies Fade (its own protected lane; Kimberly's suite)

Work is capped at three active songs. That cap is the point.

---

## What's in here

```
00_control_room/    The docs that drive decisions — plan, queue, scores, rules, logs
02_song_records/    Per-song deep workups
04_suno_experiments/  AI experiment briefs (what's allowed, what's being tested, results)
05_producer_briefs/ Track-by-track production plans
01_source_manifests/  Where everything came from — Drive inventory, memo DB, lyric texts
data/               master_catalog.json (the spine) + CSV + transcripts + version chains
scripts/            The tooling (see below)
```

### The catalog is the spine
`data/master_catalog.json` — 150 entities, each carrying: IDs and alt-titles, writers and rights confidence, stage, lyric/audio status, **potential** and **readiness** scores (deliberately never merged), **momentum** and last-activity, live-set presence, resolved latest source file, machine-readable **AI-upload gate**, next action, and an open-questions list.

### Scoring, in brief
- **Potential /100** — hook 25, lyric 20, emotional truth 20, structure 15, identity fit 10, replay 10
- **Readiness /100** — completeness 25, clarity 20, source usability 15, remaining work 25, feasibility 15
- **Momentum /100** — recency 55%, number of returns 30%, years carried 15%

Potential says how good it is. Readiness says how close it is. Momentum says how alive it is in Jeff's hands. Crossing them is where the answers live.

---

## The Workbench (local, free, private)

Everything runs on Jeff's own Mac — no audio ever leaves the machine.

| Tool | Job |
|---|---|
| **Whisper** | Transcribed all 916 voice memos → songs findable by lyric |
| **Demucs** | Stem separation (Blue Skies Fade restoration path) |
| **Basic Pitch** | Memo melodies → MIDI for Logic (`scripts/basic_pitch_pass.py`) |
| **Chromaprint** | Fingerprint clustering → version families (`scripts/chromaprint_pass.py`) |
| **Matchering** | Album-wide level match + true-peak fix |
| **librosa / ffmpeg** | Key, tempo, loudness analysis |

Run order and rationale: [`00_control_room/Workbench Plan.md`](00_control_room/Workbench%20Plan.md).

---

## House rules (non-negotiable)

1. **Originals are never modified, renamed, moved, or deleted.** Everything here is an index layered on top.
2. **Transcription ≠ listening.** Every audio claim states exactly what was done. Signal analysis is not an opinion about a song.
3. **Rights walls are machine-enforced.** Every entity carries `ai_upload_ok` — currently 128 YES (Jeff-written, solo recordings only) / 20 NO / 2 NEEDS-CONSENT. Covers, co-writes, and collaborators' songs never go to an AI service.
4. **AI output is a decision aid, never a release.** Sketches inform arrangement choices; finished Jeff Story songs are 100% human.
5. **Never silently replace Jeff's words.** Every lyric suggestion is shown as ORIGINAL → PROPOSED → WHY, and Jeff approves or it doesn't happen.
6. **No voice cloning** without separate, explicit, per-case permission.
7. **Max three active songs.** Interesting ideas get parked, not promoted.

See [`00_control_room/Rights and AI Provenance.md`](00_control_room/Rights%20and%20AI%20Provenance.md) and [`00_control_room/AI Music Services — Field Guide 2026.md`](00_control_room/AI%20Music%20Services%20—%20Field%20Guide%202026.md).

---

## Related projects

The vault is the **song brain**. **StoryBoard** is the band-management OS that consumes it (`data/app_api.json` — schema 3; the spine is not a substitute import; StoryBoard reads `id` / `title` / `project` / `is_original` / `key` / `bpm` / `bpm_int` / `vault_id` / `vault_ref` / `played_live` / `import_scope`; default live is the published `setlist_ready_default_import` **Vault default-live** slice, including parked-named rows as current-artist repertoire, not an empty list and not a fourth live band; Show Night binds planned Vault titles only; Travis is `travis_books`; nothing auto-posts; not a second catalog, not StoryDesk/StoryOps, StoryLiner is promo only). See [`APPS.md`](APPS.md).

## Current state

Catalog v1.6 · 150 entities (126 originals) · 916 memos transcribed, 372 matched · 59 songs scored · 6-track Stalemate album ~16 small items from done. StoryBoard import: `data/app_api.json` (40 setlist-ready keyed originals; 20-id Vault default-live slice). Validate: `python3 scripts/validate_catalog.py`.

*Maintained with Claude in the "2026 Song Organization" project. Sessions append to the Decision Log and Session Log — read those first to pick up where the last one left off.*
