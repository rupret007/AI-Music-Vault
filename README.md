# AI Music Vault

A songwriting catalog, local browser dashboard, and Python tools for finding song
ideas, tracking evidence, and choosing the next writing or production step.
`data/master_catalog.json` is the source of truth; generated views are indexes,
not audio players or finished exports.

**This repository is PUBLIC.** Committed metadata, lyrics, transcripts, and the
dashboard are publicly readable and include sensitive historical material.
“Private session” or “private sit-down” means browser-local navigation and resume
state, not private repository contents. Audio masters and Logic projects stay
outside this repo. Do not commit audio, personal data, or local session notes.

## Features

- Search songs by title, existing aliases, punctuation-folded names, or searchable
  matched memo lyrics; Enter opens the closest result. Navigate between a song
  and its matched memo evidence, with date sorting and scoped search.
- Start Write / Produce / Listen on the highest-momentum matching song, move
  through a bounded queue, and resume the exact song after refresh. Copy a
  sanitized work card or next step; unsafe or missing actions fail closed.
- **Recent changes (September–October 2026):** Logic-ready sit-down shows
  **Assets on file**, **Logic-ready next**, and **Copy Logic-ready next** from
  catalog evidence. Memo intake names and work actions reject owner-audio
  locators; session, memo, and handoff copy preserve export honesty.
- Keep potential, readiness, momentum, rights gates, and next actions separate.
  Work stays capped at three active lanes: Flagship, Quick win, Experimental.
  On deck and the protected Opus remain separate.
- Generate a StoryBoard import as local `data/app_api.json`, plus a catalog CSV
  and a self-contained HTML dashboard. Nothing auto-posts.

## Quick start

Open [Jeff Story Song Vault Dashboard.html](Jeff%20Story%20Song%20Vault%20Dashboard.html)
locally in a browser. No server, account, API key, or package install is needed
to browse the committed dashboard. Clipboard and resume storage depend on browser
permissions; blocked storage soft-fails.

For development, use **Python 3.12** (the CI version) and **Node.js** for the
navigation smoke test (verified locally with Node 22). The core build and checks
use the standard libraries only. Where older docs use `python3`, ensure it selects
the same Python version. There is no npm project, Makefile, required
environment variable, `.env` file, or desktop packaging step.

## Build and test

From the repository root, regenerate derived files after catalog or dashboard
changes:

```bash
python3.12 scripts/export_app_api.py
python3.12 scripts/export_catalog_csv.py
python3.12 scripts/build_dashboard.py
```

Run the full [catalog-validate workflow](.github/workflows/catalog-validate.yml)
gate locally (CI uses `python` after selecting 3.12):

```bash
python3.12 scripts/validate_catalog.py
python3.12 -m unittest discover -s tests -v
node tests/test_dashboard_navigation.js
node tests/test_dashboard_resume.js
python3.12 scripts/export_app_api.py --check
python3.12 scripts/export_catalog_csv.py --check
```

These commands read committed metadata and generated files; they do not open or
upload audio or contact an AI service. Local validation is the catalog gate;
a hosted empty-runner is not a catalog fail or a successful validation.

Optional: `python3.12 scripts/build_xlsx.py` needs `openpyxl` and writes
`data/Jeff Story Master Song Catalog.xlsx`. It is untracked, not gitignored, and
contains historical work-plan/read-me text; it is not the current handoff.
Do not commit the workbook. `build_catalog.py`, `build_organized_vault.py`, and
`patch_catalog_v*.py` are historical one-shot scripts, not current build steps.
Owner-local audio tools and their separate dependencies are described in the
[Workbench Plan](00_control_room/Workbench%20Plan.md); they are not CI prerequisites.

## Click-test the private session

Open the dashboard locally. This manual browser check complements the Node smoke
test; it does not establish that any audio has been heard or exported.

1. Click Write, Produce, or Listen. Note the song and `N of M` position; use Next
   to check a non-first song.
2. Read **Do this now** and use **Copy next step**. The clipboard must match the
   sanitized action without audio filenames or locations. Sit-down Next matches
   it or reports no safe catalog next step; unsafe actions have no copy button.
3. Use **Review memo evidence** when present. It opens scoped memo search, never
   audio. Missing evidence is labeled plainly.
4. Refresh: the exact song and work kind reopen. Escape / Clear filters leaves
   the same song and safe next step in Resume; **Resume** returns to that song.
5. Click **Forget**, then refresh. Resume stays gone and the work hash is cleared.
   Browser storage holds only schema version, work kind, and catalog ID. Extra
   fields, stale schemas, unknown IDs, and mismatched kinds are rejected.
6. Search Songs by an alias or a title without apostrophes; Enter opens the
   closest result and Escape clears search. Memo lyric matches are leads, not listens.
7. Check **Logic-ready next**, **Assets on file**, and **Copy Logic-ready next**
   when shown. Pair Voice Memo Intake name + **Copy next step** in your local
   Session Log handoff. Work in Logic (export honesty, WAVs/AIFF/MIDI preference,
   no Ableton-first). This page does not open audio — export to WAV/AIFF/MIDI
   from Logic on Jeff's Mac. Logic / WAV / AIFF / MIDI export stays **not done
   until a real file exists**. Asset labels are catalog evidence, not completed exports.

## Status and limits

Catalog v1.6: **150 entities / 126 originals / 59 scored**; 916 transcribed memos,
372 matched, 807 searchable transcripts. Searchable evidence excludes short,
collapsed transcripts, so search totals differ from source totals.
StoryBoard feed: **40 setlist-ready keyed originals; 20-row Vault default-live
slice**. Catalog rows are not the official set; Show Night owns official sets.
StoryBoard consumes local JSON, rejects the spine and remote catalog URLs, and
owns band operations. StoryLiner is promo only. See [APPS.md](APPS.md) for the
recorded integration contract; this repo does not run those apps or an event ingester.

Transcription is not listening. Logic-ready is not an export. The rights validator
checks catalog gates (128 YES / 20 NO / 2 NEEDS-CONSENT); it does not grant upload
permission or control external services. Originals stay untouched, lyric edits
require approval, and voice cloning requires separate explicit permission.

## Working docs

- [Producer README](00_control_room/Producer%20README.md): resume from the latest
  [Session Log](00_control_room/Session%20Log.md) entry.
- [Priority Queue](00_control_room/Priority%20Queue.md),
  [The Plan](00_control_room/THE%20PLAN.md), and
  [Needs Jeff](00_control_room/Needs%20Jeff.md): current work and open decisions.
- [Rights and AI Provenance](00_control_room/Rights%20and%20AI%20Provenance.md):
  rights boundaries and experiment records.
- `01_source_manifests/`: source inventories; `02_song_records/`: song workups;
  `04_suno_experiments/` and `05_producer_briefs/`: experiment and production plans.
