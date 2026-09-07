# AI Music Vault — Jeff Story

**27 years of songwriting, organized, scored, and moving toward finished.**

This is the working brain of the Jeff Story catalog: 150 song entities spanning 1999–2026 across Stalemate, Something Dirty, Trailer Swift, Rad Dad, and solo work — plus the tooling that found, matched, scored, and keeps track of all of it.

> ⚠️ **Private repository.** Contains unreleased album material, personal lyrics, collaborators' compositions, and home-address strings inside voice-memo titles. Not for public distribution. Audio masters are deliberately **not** stored here — they live in the local vault and Google Drive.

---

## Start here

| If you want to… | Open |
|---|---|
| Know what to work on next | [`00_control_room/Priority Queue.md`](00_control_room/Priority%20Queue.md) |
| See the whole plan | [`00_control_room/THE PLAN.md`](00_control_room/THE%20PLAN.md) |
| Know what's *alive* vs. sleeping | [`00_control_room/What's Alive — Momentum Index.md`](00_control_room/What's%20Alive%20—%20Momentum%20Index.md) |
| Browse every song interactively | `Jeff Story Song Vault Dashboard.html` (open in any browser; catalog rows are not the official set) |
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
node tests/test_dashboard_navigation.js
python3 scripts/export_app_api.py --check
python3 scripts/export_catalog_csv.py --check
```

These checks read the committed catalog metadata, StoryBoard export, and local
generated dashboard only.
They do not open or upload audio, modify originals, or contact an AI service.
Keep the repository and its test output private because catalog metadata can
still contain unreleased, personal, collaborator, or location information.
The private dashboard links catalog songs that have searchable matched voice
memos to that evidence, and each matched memo back to its song. Songs with
searchable matches can be scanned, filtered, and sorted by latest memo date;
the scoped set is newest-first and can copy the local intake filename. Songs
search finds existing aliases, folds punctuation, ranks the closest name
first, and Enter opens that row; a long enough query can also surface a song
from a searchable matched memo lyric. The
same song brain can filter write / produce / listen work from the existing
next action, open a resumable work session, sit down on a lane song, and copy
a sanitized work card (hook, next action, open questions, memo count/date)
without owner-audio or street locators. Expanded sit-down uses the sanitized
next action and latest memo intake name — it does not reprint Logic / WAV /
best_source paths. The primary work buttons open the highest-momentum matching
song immediately, name its position in a bounded queue, and keep secondary
catalog filters collapsed until they are needed. The session header puts the
sanitized catalog next step in front of Jeff with **Copy next step** and, when
searchable matched memos exist, **Review memo evidence**. Sit-down also names
the existing Logic-ready cluster and a sanitized **Logic-ready next** for the
Mac; **Copy Logic-ready next** stays hidden if that sentence is empty or unsafe.
It never invents a key and never names a Logic project or bounce file. After
Escape, the Resume strip keeps that same **Do this now** line and copy action
for the exact stored song, plus the Logic-ready next when it is safe. Sit-down
and memo scope reuse the same fail-closed catalog step — they do not reprint
leftover listen verbs. Missing evidence is labeled plainly; an empty or unsafe
next step produces no copy action. After a song is opened, the
dashboard can resume that exact local session after a refresh. The browser
stores only a schema version, work kind, and catalog ID; **Forget** clears it,
and invalid, stale, or mismatched records are discarded. No title, note,
transcript, next action, filename, or audio locator is stored. These are local
navigation links over the existing index;
they do not open, upload, or modify audio. Logic projects, keys, and WAVs
stay owner-only.

### Click-test the private session

Open `Jeff Story Song Vault Dashboard.html` locally. Do not upload it.

1. Click Write, Produce, or Listen. Note the song name and `N of M` position.
2. Click Next once if you want a non-first song. Note the new name and position.
3. Read **Do this now** on the session strip, then click **Copy next step**. The clipboard text must match the visible sanitized action and contain no audio filename or location. Sit-down **Next** must match that same text, or say there is no safe catalog next step.
4. If **Review memo evidence** appears, click it. It opens the existing scoped memo search; it never opens audio. If no matched memo exists, the session says so instead of inventing evidence.
5. Refresh. The same kind and song should reopen. **Resume** still names that song and repeats the same **Do this now** line.
6. Press Escape (or Clear filters). The Resume strip still names that song and keeps **Copy next step** when the action is safe. Click **Copy next step** there if it is visible, then click **Resume**. The same song returns.
7. If **Do this now** is absent, **Copy next step** stays hidden. That is fail-closed, not a missing song.
8. Click **Forget**. Resume disappears and the status says the browser record was forgotten. Forget also drops the leftover work hash so a later refresh cannot mint a new record. A blocked browser store soft-fails instead of crashing.
9. Refresh again. Resume stays gone.
10. In this browser's storage for the page, the record may only hold a schema version, work kind, and catalog ID. Extra fields, a stale schema, an unknown id, or a kind that no longer matches the catalog next action are rejected and removed.
11. On Songs, type a remembered alias or a title without apostrophes. The closest name is first. Press Enter to open that row. Escape clears the search. A long enough query may also list a song from a searchable matched memo lyric — that is a lead, not a listen.
12. Read **Logic-ready next** on sit-down and on the session strip. It must name only a cluster and an owner-only Mac step. It must not name a Logic project, WAV, key path, or street. If **Copy Logic-ready next** is visible, the clipboard text matches that sentence.
13. After Escape, Resume still shows **Logic-ready next** / **Copy Logic-ready next** when that sentence is safe. More filters can narrow or sort by Logic-ready. That is existing evidence, not a new score and not a key fill.

StoryBoard consumes a local `data/app_api.json` — the spine is rejected as
an import, remote catalog URLs are rejected, and this is not a public
catalog dump. Nothing auto-posts.

## The three lanes (+ on deck)

- **Flagship** — mix v1.6, two overdubs left
- **Quick win** — one overdub: lead guitar on choruses + solos
- **Experimental** — Suno arrangement test queued
- **On deck** — catalog, not the official set, lyric ~85% recovered, unrecorded
- **The Opus** — its own protected lane

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
| **Demucs** | Stem separation (protected-opus restoration path) |
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

The vault is the **song brain**. **StoryBoard** is the band-management OS that consumes it (`data/app_api.json` — schema 3; local JSON only after StoryBoard #12 — Band operations → Music & setlists; remote catalog URLs are rejected; StoryBoard #16 rejects the spine as an import; StoryBoard reads `id` / `title` / `project` / `is_original` / `key` / `bpm` / `bpm_int` / `vault_id` / `vault_ref` / `played_live` / `import_scope`; default live is the published `setlist_ready_default_import` **Vault default-live** slice, including parked-named rows as current-artist repertoire, not an empty list and not a fourth live band; catalog rows are not the official set; Show Night owns official sets; Show Night binds planned Vault titles only; Show Night official set is owner-only; StoryBoard #19 binds a local official-set dump as **Rad Dad — official set**; guest/parked slugs stay opt-in; Show Night is the live set surface; Travis is `travis_books`; nothing auto-posts; not a second catalog, not StoryDesk/StoryOps, StoryLiner is promo only). See [`APPS.md`](APPS.md).

## Current state

Catalog v1.6 · 150 entities (126 originals) · 916 memos transcribed, 372 matched · 59 songs scored · 6-track Stalemate album ~16 small items from done. StoryBoard import: `data/app_api.json` (40 setlist-ready keyed originals; 20-row Vault default-live slice). Validate: `python3 scripts/validate_catalog.py`.

*Maintained with Claude in the "2026 Song Organization" project. Sessions append to the Decision Log and Session Log — read those first to pick up where the last one left off.*
