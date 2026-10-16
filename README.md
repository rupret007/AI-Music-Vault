# AI Music Vault

A songwriting catalog, local browser dashboard, and Python tools for finding song
ideas, tracking evidence, and choosing the next writing or production step.
`data/master_catalog.json` is the source of truth; generated views are indexes,
not audio players or finished exports.

**This repository is PUBLIC.** This public catalog is not a remote fetch.
Committed metadata, lyrics, transcripts, and the dashboard are publicly
readable and include sensitive historical material. “Private session” or
“private sit-down” means browser-local navigation and resume state, not
private repository contents. Audio masters and Logic projects stay
outside this repo. Do not commit audio, personal data, or local session notes.

## Features

- Search songs by title, existing aliases, punctuation-folded names, or searchable
  matched memo lyrics; Enter opens the closest result. Memo Search folds the same
  apostrophes and punctuation, so `its alright` finds It’s Alright. Navigate
  between a song and its matched memo evidence, with date sorting and scoped search.
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
locally in a browser. The dashboard is dark by default (Jeff's preference) and
does not follow the OS light preference. Native controls use `color-scheme: dark`.
A complete WCAG AA light palette remains in the stylesheet so contrast gates stay
dual-theme. No server, account, API key, or package install is needed to browse
the committed dashboard. Clipboard and resume storage depend on browser
permissions; blocked storage soft-fails.
Copy buttons confirm success only after the browser accepts the copy. If both
clipboard methods fail, an inline status explains the failure and keeps retry
available; you can also select and copy the displayed text manually.

For development, use **Python 3.12** (the CI version) and **Node.js** for the
navigation smoke test (verified locally with Node 22). The core build and checks
use the standard libraries only. The StoryBoard importer test loads
`catalog-import.ts` from StoryBoard and installs `zod` into a temp directory.
Where older docs use `python3`, ensure it selects the same Python version.
There is no repo-level npm project, Makefile, required environment variable,
`.env` file, or desktop packaging step.

## Build and test

From the repository root, regenerate derived files after catalog or dashboard
changes:

```bash
python3.12 scripts/export_app_api.py
python3.12 scripts/export_catalog_csv.py
python3.12 scripts/build_dashboard.py
```

Importing `scripts/build_dashboard.py` does not read catalog files or write HTML.
Its `load_payload()` reads inputs explicitly; `build_payload()` and
`render_dashboard()` work in memory. `write_dashboard()` writes the rendered
page, and the guarded `main()` runs the CLI build.

Run the full [catalog-validate workflow](.github/workflows/catalog-validate.yml)
gate locally (CI uses `python` after selecting 3.12):

```bash
python3.12 scripts/validate_catalog.py
python3.12 scripts/build_dashboard.py --check
python3.12 -m unittest discover -s tests -v
node --experimental-strip-types tests/test_storyboard_catalog_import.mjs
node tests/test_dashboard_navigation.js
node tests/test_dashboard_resume.js
python3.12 scripts/export_app_api.py --check
python3.12 scripts/export_catalog_csv.py --check
```

The dashboard check rebuilds slim `DATA` and `TX` in memory and fails if either
committed HTML payload is missing, invalid, or stale. It never rewrites the HTML;
run the build commands above to refresh it. The existing payload SHA pins remain
a separate check. This freshness check compares payloads, not the HTML layout.

These commands read committed metadata and generated files; they do not open or
upload audio or contact an AI service. Local validation is the catalog gate;
a hosted empty-runner is not a catalog fail or a successful validation.

Verify Resume's first screen with an already-installed Chrome or Chromium
(set `CHROME` to the executable if it is not at the default macOS path). The
check uses Chrome DevTools Protocol the same way the local screenshot helper
does and never downloads a browser:

```bash
node tests/test_dashboard_resume_browser.js /absolute/path/to/resume-evidence
```

This additional browser check requires all Resume controls above the fold at
390×844 and 1280×800, checks keyboard order and Resume/Forget, and saves viewport
PNGs plus measured bounds. It serves the committed HTML on loopback with other
paths rejected and uses isolated temporary browser storage. Missing Chrome or a
failed launch exits non-zero; that is not viewport verification. No dependencies
are downloaded by the test. This check is not part of hosted catalog-validate.

Check clipboard failure feedback, retry, and keyboard focus in an installed
Chrome/Chromium at phone and desktop widths:

```bash
node tests/test_dashboard_clipboard_browser.js
```

This check uses synthetic text and mocked clipboard methods in an isolated
browser profile; it never reads or writes the system clipboard. The offline
clipboard unit regressions also run in the standard Python unittest gate.

Optional: `python3.12 scripts/build_xlsx.py` needs `openpyxl` and writes
`data/Jeff Story Master Song Catalog.xlsx`. It is untracked, not gitignored, and
contains historical work-plan/read-me text; it is not the current handoff.
Do not commit the workbook. `build_catalog.py`, `build_organized_vault.py`, and
`patch_catalog_v*.py` are historical one-shot scripts, not current build steps.
Owner-local audio tools and their separate dependencies are described in the
[Workbench Plan](00_control_room/Workbench%20Plan.md); they are not CI prerequisites.

## Click-test the browser-local session

Open the dashboard locally. This manual browser check complements the Node smoke
test; it does not establish that any audio has been heard or exported.

1. Click Write, Produce, or Listen. Note the song and `N of M` position; use Next
   to check a non-first song.
2. Read **Do this now** and use **Copy next step**. The clipboard must match the
   sanitized action without audio filenames or locations. Sit-down does not
   repeat that catalog next step while the session is this song. Open a song
   from a link, search, or row expand without that session, and sit-down shows
   **Do this now** for the expanded song. Unsafe or empty actions say no safe
   catalog next step and have no copy button.
   With clipboard access blocked, check the copy status for failure, then retry
   after allowing access or select the displayed text to copy manually.
3. Use **Review memo evidence** when present. It opens scoped memo search, never
   audio. Missing evidence is labeled plainly.
4. Refresh: the exact song and work kind reopen. Escape / Clear filters leaves
   the same song and safe next step in Resume; **Resume** returns to that song.
5. Click **Forget**, then refresh. Resume stays gone and the work hash is cleared.
   Browser storage holds only schema version, work kind, and catalog ID. Extra
   fields, stale schemas, unknown IDs, and mismatched kinds are rejected.
6. Search Songs by an alias or a title without apostrophes; arrow keys move a
   visible highlight among results and Enter opens the focused row (closest
   result if none is highlighted). Escape clears search. Memo Search folds the
   same punctuation (`its alright` finds It’s Alright) and uses the same
   arrow/Enter focus. Memo lyric matches are leads, not listens.
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
