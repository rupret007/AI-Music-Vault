# Vault → StoryBoard (consolidated path)

*2026-08-23 · Control-room pointer, not a new priority list.*
*Importer-honest pass: fields StoryBoard actually reads after StoryBoard #4.*

**This vault is the song brain.** StoryBoard is the band-management OS that reads it. StoryLiner is promo only. There is no StoryDesk / StoryOps band OS, and this repo does not grow a new manager app or a fourth live band.

| Piece | File | Role |
|---|---|---|
| Spine | `data/master_catalog.json` | 150 entities, scores, rights, next actions |
| Import | `data/app_api.json` | **the** StoryBoard feed — same `songs[]`, no second catalog |
| Exporter | `python3 scripts/export_app_api.py` | regenerate after catalog edits; `--check` fails on stale feed |
| Mapping | `app_api.json` → `storyboard` | inspected `catalog-import.ts`, not invented |
| Guard | `python3 scripts/validate_catalog.py` | fail closed on id/gate/lane/export-honesty drift |

## Fields StoryBoard actually imports

From `songs[]`: `id`, `title`, `project`, `is_original`, `key`, `bpm`, `bpm_int`, `vault_id`, `vault_ref`, `played_live`.

| StoryBoard writes | Vault field | Do not |
|---|---|---|
| Song.title | `title` | rewrite the title |
| Song.musicalKey | `key` (max 30) | invent a key |
| Song.bpm | `bpm_int` first, then `bpm` (int or leading tempo) | invent a tempo |
| Song.sourceKey | `vault:catalog_import_v1:{vault_id ?? id}` | merge on title |
| Song.notes | `vault_ref` (`vault:{id}`) | invent liner notes |
| Song.active | `is_original !== false` | force every row active |
| duration / vocalist | null | guess feel |

`bpm` and `bpm_int` are the same pre-parsed integer. `bpm_raw` keeps catalog text such as `"214 (cut)"`.

## Default live catalog (do not invent a band)

StoryBoard default import is **live repertoire**: project is Rad Dad or Jeff Story (or phrase-matches those names), **or** `played_live` records a Rad Dad play. When `setlist_ready` is present, default import keeps that slice only.

Parked catalogs (Stalemate, Trailer Swift, Something Dirty) stay off unless Jeff passes `includeParked` / `includeAllProjects`. Covers stay out. Travis rows are `travis_books` — StoryBoard does not auto-pitch him.

This vault labels **no** `artist_project` as the exact string `Rad Dad`. Songs *played* by Rad Dad still live under Stalemate / hybrid labels (`live_presence` ≠ project) and **do** enter default import via `played_live`. Jeff Story keyed originals in `setlist_ready` enter as well. That is the existing catalog, not a minted band. `setlist_ready_default_import` is that slice — not an invented running order.

## Three active songs (unchanged — Jeff owns this cap)

1. Flagship — ST-0001 Turn Over The Flag
2. Quick win — ST-0004 Manic
3. Experimental — ST-0009 Long Long Drive

On deck: JS-0128 It's Alright. **Protected opus:** JS-0107 Blue Skies Fade (Kimberly lane — NEEDS CONSENT, no casual rewrite).

StoryBoard may *display* the whole library after an opt-in import. It must not promote a fourth WIP. Set-list / feel / who is alive stays Jeff's.

## Setlists + ops (same file, not a second catalog)

- **Library seed:** `songs[]` (StoryBoard merge key = `vault:catalog_import_v1:{id}`).
- **Setlist seed:** `setlist_ready` — keyed originals. Default-live slice = `setlist_ready_default_import`. StoryBoard `SetlistItem.itemType` = `song`. Do **not** invent breaks, durations, or running order.
- **Ops write-back:** drop `show_played` / `bounce` JSON into `events/` citing vault ids. Lanes in the feed are WIP slots, not a setlist. Remote catalog URLs are rejected on the StoryBoard side.

## What StoryBoard should not do

- Store audio (none lives here; masters stay local + Drive)
- Invent duration or lead vocalist
- Import covers or collaborator songs as AI-upload-ok
- Treat StoryLiner, Andrea, Show Night, or a hypothetical StoryDesk/StoryOps as a second catalog
- Treat a parked or hybrid project as a new live band

Full mapping and ecosystem notes: [`APPS.md`](../APPS.md). WIP truth: [`Priority Queue.md`](Priority%20Queue.md).
