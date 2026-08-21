# THE APP ECOSYSTEM — Jeff's music software, and how it connects to the vault

*Since 2025 Jeff has been building software alongside the songs. Several of these apps want exactly the data this vault holds — and several produce data the vault should be absorbing. This maps what exists and how they wire together.*

## The repos (github.com/rupret007, as of 2026-08-20)

### 🎵 Core music
| Repo | What it is | Vault relevance |
|---|---|---|
| **webjam** | Desktop conductor for low-latency remote collaboration — Jamulus sessions, Reference Studio (local recording/arrangement/mixing, non-destructive, WAV/FLAC bounce with checksums), meeting handoff, iPhone companion. v0.26.0, four-platform CI, MIT. | **HIGH — bidirectional.** Every Reference Studio bounce is a new song version with a checksum. That's version-chain data of better quality than anything in Drive. |
| **rad-dad-show-night** | Rad Dad + Friends show-night run sheet, set lists, shared song-suggestion board. TypeScript. | **HIGH — bidirectional.** The vault's `live_presence` layer is currently hand-parsed from setlist docs; this app *is* the live-set source of truth going forward. |
| **RadDadSite** | Rad Dad band website. CSS. | **MEDIUM — outbound.** Could render setlists/originals from vault data instead of hand-maintained lists. |

### 🤖 The assistants ("my manager")
| Repo | What it is | Vault relevance |
|---|---|---|
| **Andrea-Assistant** | Assistant app (HTML). | **HIGHEST — inbound.** An assistant that knows Jeff's music needs a knowledge base. This vault *is* that knowledge base. |
| **Andrea_NanoBot** | Assistant/bot (TypeScript, Jul 2026). | Same — likely the newer iteration. |
| **story-cursor-guardrails** | Guardrails for AI-assisted development (Python). | **CONCEPTUAL.** The vault has its own guardrails (rights gates, ORIGINAL→PROPOSED→WHY, 3-song cap). Same instinct, different domain — worth cross-pollinating. |
| **Cursor-OpenClaw-Integration** | Cursor / OpenClaw integration (Python). | Tooling context. |

### 📋 Story-family / other
`StoryBoard` · `StoryLiner` · `Story-Flight-Plan` · `story-corner-shelf` · `StoryLand-Driving-School` · `Turdanoid` (Arkanoid game) · `FireLoader` (C#) · `constructiondaily` · `WPSD-Dashboard`
*(Non-music or unconfirmed — Jeff: flag any of these that touch music and they move up.)*

---

## The integration architecture

The vault should be the **single source of truth for song knowledge**, and the apps should read from it and write events back to it.

```
                    ┌──────────────────────────┐
   setlists  ──────▶│                          │──────▶  Andrea assistant
   (show-night)     │   AI MUSIC VAULT         │         ("what should I work on?"
                    │   data/master_catalog    │          "what key is Manic in?")
   bounces   ──────▶│   150 entities           │
   (WebJam)         │   scores · rights · keys │──────▶  RadDadSite
                    │   momentum · live · next │         (setlists, song pages)
   memos     ──────▶│                          │
   (Whisper)        └──────────────────────────┘──────▶  Rad Dad Show Night
                                                          (originals w/ keys + charts)
```

### Step 1 — the vault exposes a stable feed *(built: `scripts/export_app_api.py`)*
Produces `data/app_api.json` — a slim, stable-schema feed any app can consume without parsing the full catalog:

```jsonc
{
  "generated": "2026-08-20",
  "songs": [{
    "id": "ST-0004", "title": "Manic", "project": "Stalemate",
    "key": "…", "bpm": …, "potential": 85, "readiness": …, "momentum": 84,
    "live": "2024-04", "stage": "…", "next_action": "…",
    "ai_upload_ok": true, "is_original": true, "writers": ["Jeff Story"]
  }],
  "lanes": { "flagship": "ST-0001", "quick_win": "ST-0004", … },
  "setlist_ready": [ /* originals with a known key, playable live */ ]
}
```
Run: `python3 scripts/export_app_api.py`. Regenerate whenever the catalog changes.

### Step 2 — apps write events back
The highest-value flow is **live-set truth**. Right now momentum is inferred from file dates; if Show Night emits a played-setlist event per gig, the vault's `live_presence` becomes *actual performance history* — and momentum stops being an estimate. Proposed drop-file the app can write (or Jeff can paste):

```json
{"event": "show_played", "date": "2026-09-14", "band": "Rad Dad",
 "venue": "…", "songs": ["Drinking Song", "Everyday", "The Way I Love You"]}
```
Dropped into `events/` and folded in at the next session. Same shape works for WebJam bounces (`{"event":"bounce", "song":"Manic", "version":"v1.5", "path":"…", "sha256":"…"}`).

### Step 3 — the assistant gets the brain
`Andrea-Assistant` / `Andrea_NanoBot` should read `data/app_api.json` plus the four docs that hold judgment: `Priority Queue`, `What's Alive`, `Song Map`, and `Jeff Story Style Guide`. That combination is what lets an assistant answer *"what should I work on tonight?"* with a real answer instead of a guess — and the Style Guide is what keeps it from writing generic AI lyrics if it ever helps with words.

---

## How to actually add the repos here

Three options, cheapest first — Jeff picks:

1. **Reference only (current).** This document. Zero coupling, always accurate about *what exists*, no code duplication. Good default.
2. **Git submodules.** `git submodule add https://github.com/rupret007/webjam apps/webjam` — pins each app at a commit, clones with the vault, keeps histories separate. Best if you want one clone to bring everything.
3. **Merge a repo in wholesale.** Only worth it for something that stops being its own product and becomes part of the vault.

Recommendation: stay at (1) until an app actually consumes `app_api.json`, then move that app to (2) so the contract is versioned in one place.

---

## Open questions for Jeff
- Which of the Story-family repos touch music? (StoryBoard? StoryLiner?)
- Is **Andrea** the assistant named after the song "Andrea," or a separate thing? (Affects nothing technical — but the vault should record it either way.)
- Does `rad-dad-show-night` already store setlists in a structured file we can read directly, rather than inventing the event format above?
- Should the vault's dashboard and the app ecosystem eventually converge into one interface, or stay separate tools?
