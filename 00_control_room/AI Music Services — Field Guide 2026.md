# AI MUSIC SERVICES — FIELD GUIDE (researched 2026-08-20)
*What's out there, what changed, and what fits YOUR pipeline. House rules unchanged: your songs only, private, decision-aids not releases, originals preserved, no voice cloning without separate explicit OK, everything logged.*

## The lay of the land (August 2026)
The legal ground shifted hard in the last year. Warner settled with Suno (Nov 2025) and UMG settled with Udio (Oct 2025); Sony is still suing both, with rulings expected this summer. Practical fallout for users: **Suno's free tier lost downloads** (stream/share only), paid tiers have download caps, and streaming platforms now actively tag and demonetize AI-generated uploads (Deezer tags ~44% of new uploads as AI; Spotify has a human-artist verification badge; Apple filters at the distributor level).

**Why your pipeline is already on the right side of all of this:** we only use AI sketches as *decision aids* — nothing AI-generated ever gets released as a Jeff Story song. The industry's own emerging best practice ("AI for sketching and demos, human production for finished work") is literally the pipeline we defined before knowing any of this. Your finished songs stay 100% human, releasable anywhere, badge-safe.

## Service by service — verdicts for Jeff

### 🟢 SUNO (v5.5) — still the one, and much stronger than when we planned EXP-001
What's new since our briefs were written: **Stem Split** (a generation can be split into up to 12 time-aligned WAV stems — we can pull JUST the horn section out of a Manic ska sketch and audition it against your real recording) · **Song Editor** (section-level regeneration — rework just a bridge or chorus arrangement, exactly what arrangement tests want) · **Suno Studio** (browser DAW, Premier tier) · **custom audio upload, 15 sec–4 min** (your 2-minute demos fit perfectly) · v5.5 vocals far more natural.
**The catch:** free tier = no downloads anymore (you can still LISTEN on-platform, which is all a decision-aid strictly needs), and heavy editing burns credits fast. **Pro is ~$8/mo (2,500 credits)** with downloads and commercial license.
**Ownership fine print:** Suno's ToS says users generally don't OWN generated music, and there's no indemnification. Irrelevant to us — we never release Suno output — but it's one more reason the decision-aid rule stays.
**Verdict:** primary experiment platform. EXP-001 (Long Long Drive) and EXP-002 (Manic horns) both run here.
**Decision for you (30 seconds, no rush):** stay free (listen on-platform, screenshots + notes as the record) or run Pro month-to-month ($8) during experiment months so we can download/keep sketch stems. Your call — the rules work either way.

### 🔴 UDIO — skip
Post-settlement Udio is a **walled garden**: creations can't be downloaded or posted elsewhere at all, and the pivot is toward licensed major-label artist styles for fans. Putting your demos into a box you can't export from serves you not at all.

### 🟡 STABLE AUDIO 3 — interesting, and it can run LOCALLY
Open-weight models (free) generate instrumentals/textures up to ~6 minutes, trained on licensed data. Because the weights are open, it can potentially run on the mac mini — **private by construction, Workbench-philosophy compliant** (nothing leaves the machine). Not a song generator like Suno — think instrumental beds and textures. Added to the Workbench watchlist as a future experiment (worth testing whether the M-series mini handles it); NOT installed, per the propose-first rule.

### 🟡 MOISES (~$4/mo) — only if you want it on your phone
Stem separation, chord detection, speed-shift for practice. **Demucs on your mini already does the core job free and private** — Moises adds phone convenience and live chord display for practice. Optional quality-of-life, not pipeline.

### 🔴 LANDR — skip for now
AI mastering + distribution. **Matchering (installed) covers the mastering pass locally and free.** Revisit only if/when you want a distribution partner for the finished album — different decision, different day.

### ⛔ Voice cloning / Personas — wall stays up
Suno now has custom-voice uploads and Personas (a sonic fingerprint of a voice). House rule unchanged: **no voice cloning without your separate, explicit, per-case permission** — and if that day comes, the only permissible subject is your own voice, on a paid tier, private. Nothing queued, nothing planned.

## The updated experiment playbook (what v5.5 changes)
1. **EXP-001 Long Long Drive** (queued): unchanged in substance; v5.5 vocals mean the sketch will sound closer to real — remember it's still a decision aid.
2. **EXP-002 Manic ska horns** (queued): NOW BETTER — generate the ska arrangement, **Stem Split it, pull just the horn stems**, and A/B them mentally against the real band recording. The decision ("do horns amplify the mania?") gets cleaner evidence.
3. **Section-level tests** (new capability): the Song Editor can regenerate just a bridge — future experiments can ask "what does a half-time bridge feel like on X" without regenerating whole songs. Cheaper, more focused.
4. Still blocked on: the Chrome extension handshake (for me to drive it), or you clicking through the recipe yourself — both experiment briefs in `04 Suno Experiments` have exact paste-ready lyrics + style prompts.

## Standing rules (restated, unchanged)
Your songs only (the catalog's `ai_upload_ok` field is the gate — 125 YES / 21 NO / 2 NEEDS-CONSENT) · solo recordings only, never band performances · private · max 4 generations per experiment · no voice cloning · results logged in the experiment doc + Rights & AI Provenance ledger · AI output never ships as a Jeff Story release.
