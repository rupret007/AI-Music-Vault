# Vault → StoryBoard (consolidated path)

*2026-08-23 · Control-room pointer, not a new priority list.*

**This vault is the song brain.** StoryBoard is the band-management OS that reads it. There is no StoryDesk / StoryOps band OS, and this repo does not grow a new manager app.

| Piece | File | Role |
|---|---|---|
| Spine | `data/master_catalog.json` | 150 entities, scores, rights, next actions |
| Import | `data/app_api.json` | **the** StoryBoard feed — same `songs[]`, no second catalog |
| Exporter | `python3 scripts/export_app_api.py` | regenerate after catalog edits |
| Mapping | `app_api.json` → `storyboard` | StoryBoard `Song` field map (inspected, not invented) |
| Guard | `python3 scripts/validate_catalog.py` | fail closed on id/gate/lane drift |

## Three active songs (unchanged — Jeff owns this cap)

1. Flagship — ST-0001 Turn Over The Flag
2. Quick win — ST-0004 Manic
3. Experimental — ST-0009 Long Long Drive

On deck: JS-0128 It's Alright. **Protected opus:** JS-0107 Blue Skies Fade (Kimberly lane — NEEDS CONSENT, no casual rewrite).

StoryBoard may *display* the whole library. It must not promote a fourth WIP. Set-list / feel / who is alive stays Jeff's.

## What StoryBoard should not do

- Store audio (none lives here; masters stay local + Drive)
- Invent duration or lead vocalist
- Import covers or collaborator songs as AI-upload-ok
- Treat StoryLiner, Andrea, Show Night, or a hypothetical StoryDesk/StoryOps as a second catalog

Full mapping and ecosystem notes: [`APPS.md`](../APPS.md). WIP truth: [`Priority Queue.md`](Priority%20Queue.md).
