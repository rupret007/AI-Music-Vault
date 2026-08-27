# THE APP ECOSYSTEM — Jeff's music software, and how it connects to the vault

*Vault is the song brain. StoryBoard is the band-management OS that consumes it.
Updated 2026-08-27 — consolidated path: **Vault → local `data/app_api.json` → StoryBoard Band operations**. StoryBoard rejects the spine as an import. Remote catalog URLs are rejected. Jeff-facing wording here is roles and counts only.*

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
| **One import file** | StoryBoard reads local `data/app_api.json` (same `songs[]` array). StoryBoard rejects the spine as an import. Remote catalog URLs are rejected. Mapping lives on the import file under `storyboard`. |
| **No new app** | This repo does not grow a StoryBoard clone. Export + document; StoryBoard already has Song + Setlist. |
| **Three active songs** | Flagship · Quick win · Experimental. On deck. Protected opus. Roles only — not a public catalog map. |
| **No audio here** | Masters stay local + Drive. The feed carries import fields (keys, scores, gates) — never files. |

### StoryBoard Song mapping (importer-honest, 2026-08-26)

Inspected `rupret007/StoryBoard` `packages/shared/src/catalog-import.ts` after StoryBoard #16.
The importer reads **`data/app_api.json`**, not `master_catalog.json`, and only as
**local JSON** (Band operations → Music & setlists). Remote catalog URLs are
rejected. From `songs[]` it reads `id`, `title`, `project`, `is_original`, `key`,
`bpm`, `bpm_int`, `vault_id`, `vault_ref`, `played_live`, `import_scope`, plus the
published `setlist_ready_default_import` id list (and `setlist_ready` on opt-in).
It names the published-slice draft **Vault default-live**. Parked-named rows in
that slice stay current-artist repertoire — not a fourth live band.
When a Vault payload is present, Show Night only binds planned Vault titles
and does not mint excluded rows or fill an empty published slice.
Prisma still has duration / vocalist / genre / URLs — those stay null.
**Nothing auto-posts. Jeff owns feel, set-list, and catalog calls.**
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

**Default live is the published `setlist_ready_default_import` slice** (`import_scope=default_live`). StoryBoard #12 prefers that list when present and names the draft **Vault default-live**; an empty published slice stays empty. The file is accepted only as local JSON — remote catalog URLs are rejected. Parked-named rows in that slice stay current-artist repertoire — not a fourth live band. StoryBoard rejects the spine as an import — `master_catalog.json` is not a fallback feed. Fallback when the published array is absent: Rad Dad + Jeff Story + recorded Rad Dad plays, gated by `setlist_ready` (draft **Vault setlist-ready**). Parked catalogs that are not in the published slice stay parked unless opted in. Hybrid labels that phrase-match `rad dad` are live repertoire, not a fourth live band. `live_presence` is published as `played_live`. Travis rows are `travis_books`. Do not invent Rad Dad catalog rows.

Seed keyed originals from `setlist_ready`. Default import keeps `setlist_ready_default_import` (not an invented setlist). Merge on StoryBoard `sourceKey`, not on title. Field map is StoryBoard's `VAULT_STORYBOARD_FIELD_MAP` (`bpm_int`, notes ← `vault_ref`, `active = is_original !== false`).

**Setlists:** StoryBoard `Setlist` items are `song | break | note`. Vault only supplies songs. Default import writes **Vault default-live**; opt-in parked/all writes **Vault setlist-ready**. Those two drafts stay distinct, and the published catalog tallies stay catalog-true — fail closed if omitted or conflated. Do not invent breaks, a running order, or who sings what — Jeff owns that. `lanes` are the three WIP slots, not a setlist. Show Night is a running-order import on this feed, not a second catalog.

**Ops:** StoryBoard show/booking events write back to `events/` (`show_played` with vault ids). That is the ops loop. No second catalog.

Regenerate after catalog edits: `python3 scripts/export_app_api.py`. Local `python3 scripts/validate_catalog.py` fails closed if this file drifts from the catalog or the three-lane cap. Hosted `catalog-validate` on this private repo may be a 0-step empty-runner — that red is not a catalog fail. Do not claim hosted green. Do not change billing.

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
{"event": "show_played", "date": "…", "band": "…",
 "venue": "…", "songs": ["<vault-id>", "..."]}
```

Prefer vault ids. Titles work as a fallback. Same shape for WebJam bounces (`{"event":"bounce", "song":"<vault-id>", "version":"…", "path":"…", "sha256":"…"}`). Do not paste published ids into this document.

---

## How to actually add the repos here

1. **Reference only (current).** This document. Zero coupling. **Stay here** — Jeff said no new app in the vault.
2. **Git submodules** later, if StoryBoard's import needs a pinned contract in one clone.
3. **Do not merge StoryBoard into this repo.** It is its own product.

---

## Open questions for Jeff
- ~~Which of the Story-family repos touch music?~~ **RESOLVED:** StoryBoard = band OS, StoryLiner = promo, Story-Flight-Plan = not music. StoryDesk / StoryOps are not the band OS.
- ~~StoryBoard song-library schema?~~ **RESOLVED 2026-08-23** (inspected `prisma` `Song`): title / musicalKey / bpm / durationSeconds / leadVocalist / active. Mapping is in `data/app_api.json` → `storyboard`. Duration and lead vocalist stay null until Jeff supplies them.
- Is the assistant named after a catalog row, or a separate thing?
- Does `rad-dad-show-night` already store setlists in a structured file we can read directly?
- StoryBoard library today: empty or hand-populated? (Import is a seed vs a merge on `vault:catalog_import_v1:{id}`.)
- Should any vault `artist_project` be labeled **Rad Dad**, or does Jeff always import with `includeAllProjects` / `includeParked`? Default live is the published 20-row `setlist_ready_default_import` slice (including parked-named / hybrid rows as current-artist repertoire) — we will not invent Rad Dad rows or a fourth live band.
