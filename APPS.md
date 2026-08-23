# THE APP ECOSYSTEM — Jeff's music software, and how it connects to the vault

*Vault is the song brain. StoryBoard is the band-management OS that consumes it.
Updated 2026-08-23 — consolidated path: **Vault → `data/app_api.json` → StoryBoard**.*

## The consolidated path (read this first)

```
  Jeff's songs / rights / scores / next actions
                    │
                    ▼
         AI MUSIC VAULT  (this repo)
         data/master_catalog.json     ← spine, 150 entities
                    │
                    │  python3 scripts/export_app_api.py
                    ▼
         data/app_api.json            ← THE StoryBoard import
                    │
                    ▼
         StoryBoard song library + setlists
         (band OS: booking, shows, CRM — not a second catalog)
```

| Rule | Meaning |
|---|---|
| **One song brain** | `data/master_catalog.json` is the only catalog. Do not invent a second format. |
| **One band OS** | **StoryBoard** (`rupret007/StoryBoard`) is the manager. **Not StoryDesk. Not StoryOps.** Those names are not the band OS. |
| **One import file** | StoryBoard reads `data/app_api.json` (same `songs[]` array). Mapping lives on that file under `storyboard`. |
| **No new app** | This repo does not grow a StoryBoard clone. Export + document; StoryBoard already has Song + Setlist. |
| **Three active songs** | Flagship ST-0001 · Quick win ST-0004 · Experimental ST-0009. On deck JS-0128. Opus JS-0107 (Blue Skies Fade, protected). |
| **No audio here** | Masters stay local + Drive. The feed carries titles, keys, scores, gates — never files. |

### StoryBoard Song mapping (importer-honest, 2026-08-23)

Inspected `rupret007/StoryBoard` `packages/shared/src/catalog-import.ts` after StoryBoard #5.
The importer reads `songs[].id`, `title`, `project`, `is_original`, `key`, `bpm`,
`bpm_int`, `vault_id`, `vault_ref`, `played_live`, `import_scope`, plus the published
`setlist_ready_default_import` id list (and `setlist_ready` on opt-in).
Prisma still has duration / vocalist / genre / URLs — those stay null.
**StoryLiner is promo only** and does not consume this feed.

| StoryBoard writes | From this feed | Honesty |
|---|---|---|
| `title` | `songs[].title` | do not rewrite Jeff's title |
| `musicalKey` | `songs[].key` (trim; max 30; empty → null) | do not invent a key |
| `bpm` | `songs[].bpm_int` first, then `bpm` | `parseBpm` prefers a clean integer. Export pre-parses into both `bpm` and `bpm_int`. `bpm_raw` keeps `"214 (cut)"`. |
| `sourceKey` | `vault:catalog_import_v1:{vault_id ?? id}` | merge on sourceKey, not title |
| `notes` | `vault_ref` (`vault:{id}`) | do not invent liner notes |
| `active` | `is_original !== false` | covers stay inactive |
| `durationSeconds` / `leadVocalist` / `genre` / URLs | **null** | Jeff owns feel |

**Default live is the published `setlist_ready_default_import` 20-id slice** (`import_scope=default_live`). StoryBoard #5 prefers that list when present; an empty published slice stays empty. Fallback when the array is absent: Rad Dad + Jeff Story + recorded Rad Dad plays, gated by `setlist_ready`. Parked: Stalemate, Trailer Swift, Something Dirty. Hybrid labels that phrase-match `rad dad` are live repertoire, not a fourth live band. `live_presence` is published as `played_live`. Travis rows are `travis_books`. Do not invent Rad Dad catalog rows.

Seed keyed originals from `setlist_ready`. Default import keeps `setlist_ready_default_import` (not an invented setlist). Merge on StoryBoard `sourceKey`, not on title. Field map is StoryBoard's `VAULT_STORYBOARD_FIELD_MAP` (`bpm_int`, notes ← `vault_ref`, `active = is_original !== false`).

**Setlists:** StoryBoard `Setlist` items are `song | break | note`. Vault only supplies songs. Do not invent breaks, a running order, or who sings what — Jeff owns that. `lanes` are the three WIP slots, not a setlist.

**Ops:** StoryBoard show/booking events write back to `events/` (`show_played` with vault ids). That is the ops loop. No second catalog.

Regenerate after catalog edits: `python3 scripts/export_app_api.py`. CI fails closed if this file drifts from the catalog or the three-lane cap.

---

## The repos (github.com/rupret007, as of 2026-08-23)

### 🎵 Core music
| Repo | What it is | Vault relevance |
|---|---|---|
| **webjam** | Desktop conductor for low-latency remote collaboration — Jamulus sessions, Reference Studio (local recording/arrangement/mixing, non-destructive, WAV/FLAC bounce with checksums), meeting handoff, iPhone companion. v0.26.0, four-platform CI, MIT. | **HIGH — bidirectional.** Every Reference Studio bounce is a new song version with a checksum. That's version-chain data of better quality than anything in Drive. |
| **rad-dad-show-night** | Rad Dad + Friends show-night run sheet, set lists, shared song-suggestion board. TypeScript. | **HIGH — write-back.** Live-set events belong in `events/` and should cite vault ids. StoryBoard is still the band OS; this app is the night-of sheet. |
| **RadDadSite** | Rad Dad band website. CSS. | **MEDIUM — outbound.** Could render setlists/originals from vault data instead of hand-maintained lists. |

### 🤖 The assistants
| Repo | What it is | Vault relevance |
|---|---|---|
| **Andrea-Assistant** | Assistant app (HTML). | **Inbound knowledge.** Read `data/app_api.json` plus Priority Queue / What's Alive / Song Map / Style Guide. Does not replace StoryBoard. |
| **Andrea_NanoBot** | Assistant/bot (TypeScript, Jul 2026). | Same. |
| **story-cursor-guardrails** | Guardrails for AI-assisted development (Python). | **CONCEPTUAL.** Vault guardrails: rights gates, ORIGINAL→PROPOSED→WHY, 3-song cap. |
| **Cursor-OpenClaw-Integration** | Cursor / OpenClaw integration (Python). | Tooling context. |

### 🏢 Band-business layer
| Repo | What it is | Vault relevance |
|---|---|---|
| **StoryBoard** | **The band OS — "the manager."** Venue CRM, booking, 90-day planning, setlists, invoicing. Next.js 16 / NestJS 11 / Prisma 7 / Postgres 16. | **THE consumer.** Song library + setlists import `data/app_api.json`. Show/booking events write back to `events/`. |
| **StoryLiner** | **Promo only.** Social content, voice-profile guardrails, review-before-publish. | Facts (dates, credits, story) come from the catalog. Not a song library. Not a band OS. |

**Not the band OS:** StoryDesk, StoryOps, or any new manager app. If those names show up elsewhere, they do not get a second catalog and they do not replace StoryBoard.

### 📋 Non-music (confirmed by Jeff / inspection)
`Story-Flight-Plan` (flight-training plan for Jeff + his son — not music) · `story-corner-shelf` · `StoryLand-Driving-School` · `Turdanoid` (Arkanoid game) · `FireLoader` (C#) · `constructiondaily` · `WPSD-Dashboard` · `story-cursor-guardrails` / `Cursor-OpenClaw-Integration` (dev tooling)

---

## Write-back (apps → vault)

The highest-value return path is **live-set truth**. Momentum is still inferred from file dates; a played-setlist event per gig makes `live_presence` a fact. Drop JSON into `events/` (see that folder's README):

```json
{"event": "show_played", "date": "2026-09-14", "band": "Rad Dad",
 "venue": "…", "songs": ["ST-0002", "ST-0014", "JS-0001"]}
```

Prefer vault ids. Titles work as a fallback. Same shape for WebJam bounces (`{"event":"bounce", "song":"ST-0004", "version":"v1.5", "path":"…", "sha256":"…"}`).

---

## How to actually add the repos here

1. **Reference only (current).** This document. Zero coupling. **Stay here** — Jeff said no new app in the vault.
2. **Git submodules** later, if StoryBoard's import needs a pinned contract in one clone.
3. **Do not merge StoryBoard into this repo.** It is its own product.

---

## Open questions for Jeff
- ~~Which of the Story-family repos touch music?~~ **RESOLVED:** StoryBoard = band OS, StoryLiner = promo, Story-Flight-Plan = not music. StoryDesk / StoryOps are not the band OS.
- ~~StoryBoard song-library schema?~~ **RESOLVED 2026-08-23** (inspected `prisma` `Song`): title / musicalKey / bpm / durationSeconds / leadVocalist / active. Mapping is in `data/app_api.json` → `storyboard`. Duration and lead vocalist stay null until Jeff supplies them.
- Is **Andrea** the assistant named after the song "Andrea," or a separate thing?
- Does `rad-dad-show-night` already store setlists in a structured file we can read directly?
- StoryBoard library today: empty or hand-populated? (Import is a seed vs a merge on `vault:catalog_import_v1:{id}`.)
- Should any vault `artist_project` be labeled **Rad Dad**, or does Jeff always import with `includeAllProjects` / `includeParked`? Default live is the published 20-id `setlist_ready_default_import` slice — we will not invent Rad Dad rows.
