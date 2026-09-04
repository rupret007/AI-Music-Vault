# Priority Queue — v1.5 (2026-08-20, the Transcript Pass)
*Integrity pass 2026-08-23: catalog v1.6 / 150 entities. Three active songs unchanged. Long Long Drive AI-upload gate corrected to YES (Jeff confirmed 2026-08-18). Band OS consumer = StoryBoard via `data/app_api.json` — not StoryDesk/StoryOps. No new priorities.*
*Exporter-honest pass 2026-08-23: StoryBoard default live = Rad Dad (no vault rows labeled that way — do not invent them). Still these three songs. Still no new priorities.*
*StoryBoard #5 honesty 2026-08-23: default import is the published `setlist_ready_default_import` 20-id slice (`travis_books`, field map `bpm_int` / `vault_ref`). Still these three songs. Still no new priorities.*
*StoryBoard #6 honesty 2026-08-23: published slice includes parked-named Everyday / hybrid rows as current-artist repertoire; draft name is Vault default-live. Still these three songs. Still no new priorities.*
*setlist_ready vs default-live count honesty 2026-08-23: `counts.setlist_ready` (40) stays distinct from the 20-id Vault default-live slice and fails closed if conflated. Still these three songs. Still no new priorities.*
*published catalog-count honesty 2026-08-23: `counts.originals` (126) / `counts.scored` (59) / `counts.ai_upload_ok` (128) fail closed if omitted or collapsed into a setlist count. Still these three songs. Still no new priorities.*
*usable catalog SoT 2026-08-26: StoryBoard import is `data/app_api.json` after StoryBoard #9 — not the spine. Show Night does not expand Vault. Nothing auto-posts. Still these three songs. Still no new priorities.*
*usable catalog local-JSON 2026-08-26: StoryBoard #12 accepts that file only as local JSON (Band operations → Music & setlists). Remote catalog URLs are rejected. Still these three songs. Still no new priorities.*
*Session Log once 2026-08-26: the #12 local-JSON heading is listed once. Still these three songs. Still no new priorities.*
*Session Log resume from latest 2026-08-26: continue from the latest Session Log H2, not Session 1. Still these three songs. Still no new priorities.*
*Local validate, not hosted CI 2026-08-26: hosted catalog-validate may be a 0-step empty-runner — not a catalog fail. Still these three songs. Still no new priorities.*
*Jeff-facing docs roles/counts only 2026-08-26: README.md / APPS.md keep roles and counts — live-lane titles removed, ids removed, no collaborator-as-catalog-map dumps. Still these three songs. Still no new priorities.*
*Local validate success roles/counts only 2026-08-27: catalog-gate stdout stays roles and counts — published ids removed from the success line. Still these three songs. Still no new priorities.*
*StoryBoard rejects the spine 2026-08-27: live importer after #16 fails closed on the spine — not a fallback planner. Still these three songs. Still no new priorities.*
*Show Night official set owner-only 2026-08-27: official-set writes stay owner-only; public suggestions cannot mutate that set; this feed is not a public Show Night writer. Still these three songs. Still no new priorities.*
*Official-set dump bind 2026-08-27: StoryBoard #19 binds a local official-set dump as Rad Dad — official set; guest/parked slugs stay opt-in; Show Night is the live set surface. Still these three songs. Still no new priorities.*
*Catalog rows are not the official set 2026-08-27: Vault default-live stays a catalog slice; Show Night owns official sets; dashboard reuses data/app_api.json and does not reprint IN CURRENT LIVE SET. Still these three songs. Still no new priorities.*
*Satellite CSV honesty 2026-08-28: derived master_catalog.csv must match the 150-row spine; covers/version-chain/momentum ids fail closed. Still these three songs. Still no new priorities.*
*Song analysis leftover 2026-08-28: 126 originals + 93 covers clustered by Logic-ready evidence; catalog still not the official set. Still these three songs. Still no new priorities.*
*Covers book leftover 2026-08-28: 93 covers stay a reference book (empty on-book Logic-ready); Trailer Swift originals stay 0; official-set originals stay 0. Still these three songs. Still no new priorities.*
*Catalog memo evidence find-and-act 2026-09-03: songs with searchable matched memos can be scanned, filtered, and opened newest-first; intake names copy; Logic keys/WAVs stay owner-only. Still these three songs. Still no new priorities.*
*Catalog song work card 2026-09-03: existing next actions classify into write/produce/listen so the private dashboard can filter, open a lane, and copy a sanitized work card. Still these three songs. Still no new priorities.*
*Catalog write/produce/listen sit-down 2026-09-03: the same song brain now keeps a resumable work session, sits down on sanitized next action plus memo evidence, and does not reprint Logic/WAV paths. Still these three songs. Still no new priorities.*
*Catalog one-song session start 2026-09-03: Write / Produce / Listen are explicit primary actions, each session opens its highest-momentum matching song immediately, shows bounded queue position, and leaves secondary filters collapsed. Catalog rows, scores, priorities, and audio are unchanged. Still these three songs. Still no new priorities.*
*Catalog one-song session click-test 2026-09-04: refresh resumes the exact validated song instead of the first queue match; Forget soft-fails; README matches the real tester clicks. Still these three songs. Still no new priorities.*
*Catalog resume next-step leftover 2026-09-04: after Escape, Resume shows the same sanitized next step for the exact stored song; Copy next step fails closed; sit-down does not reprint leftover listen verbs. Still these three songs. Still no new priorities.*
**Evidence level:** LYRIC CORPUS COMPLETE + **TRANSCRIPT CORPUS COMPLETE** — all 916 voice memos transcribed locally (Whisper base.en on Jeff's Mac; 1 corrupt file). 372 memos now matched to 88 songs (+46 this pass). 9 previously unknown songs recovered and cataloged (JS-0130…0138). Still NO aesthetic listening — transcription ≠ listening; treat all performance/melody judgments as pending.

## THE HEADLINE
The album picture is unchanged (6 tracks, one overdub-and-master push from done). What changed: **the vault now has a second act.** The transcript pass recovered 9 real unknown songs — including one written 10 months ago — and revealed that **It's Alright (JS-0128) is a finished-shape, rights-clean song your band already plays live that exists nowhere on paper.** It's the strongest candidate to take Manic's WIP slot when the lead guitar is tracked.

## ACTIVE (max 3 — unchanged)
| Slot | Song | Status |
|---|---|---|
| **Flagship** | ST-0001 Turn Over The Flag | 2 overdubs left. Transcript pass added 2 more solo demos (Feb + Aug 2024). |
| **Quick win** | ST-0004 Manic | Waiting on Jeff's lead-guitar overdub (choruses + solos). EXP-002 ska-horn sketch queued behind Chrome. |
| **Experimental** | ST-0009 Long Long Drive | Suno EXP-001 ready; blocked on Chrome extension. |
**On deck for the next open slot: It's Alright (JS-0128)** — see the Song Workup. Two 60-second Jeff-answers make its lyric final.

## 1. BEST SONGS OVERALL (unchanged top; It's Alright enters provisionally)
1. Be With You — 86 · 2. TBFH — 86 · 3. Manic — 85 · 4. Long Long Drive — 81 · 5. Misery — 79 · 6. Drinking Song — 79 · 7. Why Do I... — 77 · 8. It's Only Been 18 — 76 · 9. Take The Step — 75 · 10. Synonyms For Stubborn — 75 · 11. Turn Over The Flag — 74 · **11b. It's Alright — 74 (provisional: transcript-only)** · 12. Andrea — 73 · 13. What To Do — 73 · 14. I Fall Down — 72 · 15. Old You — 70 · 16. Candi Lane — 70

## 2. BEST TO FINISH NEXT — the album six (unchanged)
Manic (1 overdub) → Turn Over The Flag (2) → The Way I Love You (3) → TBFH (3) → Better Than Now (2 + Sean lyric confirm — fragments now captured from the 2024-07-25 memo) → Take The Step (4). Then the album-wide level/true-peak pass (Matchering is now installed and ready).

## 3. THE MIND RECORD — now has a complete arc (NEW)
The unmade album was missing its ending. Not anymore:
**Manic → Why Do I... → Long Long Drive → What To Do → Misery → Take The Step → It's Alright.**
Mania → crisis → the drive → the bottom → what it costs her → the step → *the sun comes up anyway.* Seven Jeff-written songs, all with sources on file. Parking this here — it's a next-year record, not a distraction from the album — but it's real now, and It's Alright is why.

## 4. RECOVERED SONGS (NEW — the transcript pass, JS-0130…0138)
Ranked listen queue lives in **Hidden Gems v2 — Lyric Verified**. Headliners: **I Fall Pretty Down / City's Gone** (written Oct 2025 — newest unknown in the vault) · **Been Loving You** (4 takes over 6 months) · **Don't Put Your Life Away** (2021 Mind-thread, protective side) · **Chasing Rainbows** (Oct 2019 — the vault's oldest memo, full lyric). Plus: Better Than Now chorus fragments captured for Sean; "Blue skies beginning" memo (9 min, Jul 2024) filed to the opus.

## 5. QUICK WINS (updated)
Manic overdub · Turn Over The Flag overdubs · It's Alright lyric finalization (60s of Jeff's ear) · It's Only Been 18 (v1.5 mix exists) · the album mastering pass (Matchering installed — half a day, lifts every track).

## 6. HIGH-CEILING PROJECTS (unchanged)
Be With You (86, next-record centerpiece) · Long Long Drive · Why Do I... · Andrea rewrite · Blue Skies Fade (Demucs now installed — stems become possible the moment the Final.mp3 reaches the intake folder) · Going To Cali · Cigarettes In A.

## Provenance & credit flags (carryover)
Justify (Emerson credit) · August Heated Nights (Bellamy) · AI-assisted-reading flags on August Heated Nights / The Leaves Are Weak / I Need You V2 pending Jeff confirmation · What To Do bridge sketches (2026-08-20) are AI-draft raw material, logged; nothing enters a song without Jeff's rewrite/approval.

## Roadmap (consistency over ambition)
Manic → Turn Over → Way I Love You → TBFH → Better Than Now → Take The Step → mastering pass → **album done** → It's Alright + Be With You open the next-record conversation (and the Mind tracklist is sitting right there).
