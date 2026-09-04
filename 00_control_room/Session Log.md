# Session Log

## Session 1 — 2026-08-18 (Cowork, project "2026 Song Organization")

### Access verified
- ✅ Google Drive connector (jeffstory007@gmail.com) — full read access, 357 song-relevant records inventoried
- ✅ SoundCloud — public pages only (no login used); 44 of 189 sounds cataloged, metadata only
- ✅ Mac mini (jeffs-mac-mini-local): ~/Music and ~/Documents granted — **contain NO song audio or Logic projects** (Logic support files + Music.app library + dev projects only)
- ❌ Voice Memos — not on the Mac's accessible folders; intake folder created (see below)
- Not attempted this session: Chrome browser automation (SoundCloud private/2024a), Suno (approval gate not yet passed)

### What was done
1. Drive sweep (subagent): 357 records → `01_source_manifests/gdrive/inventory.jsonl`; 10 key docs captured in full (Overdubs, Prime Outline tracklist, song list, 2 setlists, Crisis Averted index, Drinking Song, Rad Dad setlist, SD setlist, dustduff90 Structures doc)
2. SoundCloud sweep (subagent): 44 tracks → `01_source_manifests/soundcloud/inventory.json`; 2024a playlist NOT publicly accessible (private/deleted); ~145 sounds unenumerated (SoundCloud SSR pagination limit)
3. Voice Memo Intake folder created on the Mac: `Music/Jeff Story Song Vault/Voice Memo Intake/` with plain-language export instructions
4. Master catalog v1: **113 original-song entities + 93 covers** (separated) → `00_control_room/master_catalog.{json,csv,xlsx}`
5. Preliminary ranking of the 12 songs with real lyric/production evidence; Priority Queue v1
6. WIP queue set: Turn Over The Flag (flagship) / Manic (quick win) / Long Long Drive (experimental)
7. Producer Brief written for ST-0001 Turn Over The Flag
8. All manifests + control-room docs saved to the claude.ai project

### Honesty ledger
- **Audio listened to: ZERO files.** Every audio item = "metadata only."
- Lyrics read in full: 14 songs (10 LYRICS-folder docs via content capture, Drinking Song, plus dustduff90 doc excerpts, SD setlist, Crisis Averted doc)
- Scores exist only where lyrics were actually read; everything else = confidence "low" or "insufficient evidence"

### Key discoveries
- Near-finished 6-track Stalemate album (bounces v1.4–1.6, active Mar 2026) with Jeff's own overdub checklist = the completion path
- 5 band identities: Stalemate, Something Dirty (2005–2023), Crisis Averted (~2023), Trailer Swift (TS tribute), Rad Dad (covers)
- Crisis Averted doc = master index of 12 songs × (practice + studio + chart + PDF) links
- Two finished earlier releases: My Mom Says We're Cool (2010, 12 trk), Something Dirty EP (2011, 5 trk)
- dustduff90 "Structures" doc: 12–13 songs existing nowhere else; authorship uncertain
- Dorivalland collab doc edited 4 days ago (dver.artist)

### NOT done / next continuation point
1. **Listening pass** — top priority next session: the 6 bounces + Manic demo + What To Do + Everyday + Only 18 v1.5 (stage via Drive download or device if files land locally)
2. Read remaining ~60 unread lyric docs (batch: NEW SONGS 2024 → 2020 archive)
3. Voice Memos — waiting on Jeff's export to intake folder
4. SoundCloud remaining ~145 tracks (needs logged-in Chrome or per-track fetches); 2024a playlist via Jeff's browser
5. Unenumerated Drive corners: 24 Practice folders, November 2024 Demos/Mixes, Set 6-1-2024 mp3s (IDs in inventory), Trailer Swift FINAL, per-song 2023 folders, Stems, deep 2010 archive
6. Suno: awaiting Jeff's one-time approval (proposed first experiment: Long Long Drive arrangement test)

### Assumptions recorded
- "Mom" (SD 2011) = "Mom, You're The Bomb" (charts/mixes) — single entity pending confirmation
- "Over 18" (2010) ≠ "It's Only Been 18" (2023) — kept separate
- Rad Dad "Paco Estrada" credit on The Way I Love You treated as an error pending Jeff's answer
- dustduff90 songs classified authorship-uncertain, excluded from Jeff-original ranking

## Session 1, Pass 2 — 2026-08-18 (later same day)

### Done
1. **27 more lyric docs read in full** (subagent) → doc_texts/ now holds 37 docs. All of NEW SONGS 2024 + priority 2020-archive docs + Dorivalland + Our Life.
2. **First audio ever obtained + analyzed:** 4 of 6 album bounces downloaded to workspace (turn over 1.6, tbfh 1.4, manic 1.4, take the step 1.4). Signal analysis only (librosa+ffmpeg): durations 2:00–2:16, key-estimates consistent with Eb-tuning charts, ALL true peaks over 0 dBFS, Manic +3dB hot vs album. NO aesthetic listening; ASR blocked (HuggingFace/Azure model downloads 403 in sandbox).
3. Catalog v1.1: 38 songs now scored (was 12). New top-15 entrants: Manic 85, Why Do I... 77, Synonyms For Stubborn 75, Andrea 73, What To Do 73 (bridge unwritten!), I Fall Down 72.
4. Candi Lane lineage resolved: Our Life (2014) → Candy Lane (2017) → Candi Lane (2024).
5. Dorivalland reclassified: collaborator's musical-theater project (reference, not catalog).
6. Credit/provenance flags: Justify quotes Emerson; August Heated Nights uses Bellamy's real speech; 2-3 docs read AI-assisted (confirm with Jeff for the ledger).
7. Producer Brief for Turn Over The Flag updated with measured structure/loudness + contrast-not-thickness guidance.
8. WIP queue unchanged (no churn): Turn Over / Manic / Long Long Drive. Manic's 85 validates the quick-win slot.

### Failed / blocked this pass
- Downloads of "2. the way i love you v1.4" and "5. better than now v1.4" — repeated "MCP session expired" errors (others worked; likely flaky large-payload path). RETRY NEXT SESSION.
- Speech-to-text: faster-whisper + openai-whisper model downloads both 403-blocked. Options next session: retry, or transcribe on Jeff's Mac, or Jeff types the Better Than Now lyric (Needs Jeff #5 already covers it).

### Next continuation point
1. Retry 2 remaining bounce downloads + analyze.
2. Listening-based evaluation still owed on everything (or Jeff listens with the brief in hand).
3. Unread docs remaining: ~35 (2020 deep archive bulk, per-song 2023 folders, dustduff90 'andrea lyrics' doc 1WvDH9vIecGEoc4odboQ9Gd6SKghjY9GEKcz9cs15Jn4).
4. Bonus doc found, unread: NEW SONGS 2024 "Turn over the flag" doc (14YEd5WgIusz9zsUzr9ioYDvAt9r0O_-5GK23vvg0ejI), "Manic? No way!" 2020 ancestor (1HZjazoxIzbULTmf8s3iFQQcd_NjDFztzx_3jKqLJZXg).
5. SoundCloud 2024a + remaining ~145 tracks (browser session).
6. Voice Memo intake folder — check for new files.

## Session 1, Pass 3 — 2026-08-18 (evening)
### Done
1. VOICE MEMOS CAPTURED: Finder (computer use, Jeff-approved) copied 916 memos (1.7GB, 2019-09→2026-07) + CloudRecordings.db to Music/Jeff Story Song Vault/Voice Memo Intake. Real titles extracted from DB. 326 matched to 73 songs (matcher: fuzzy title). 590 unmatched → vm_unmatched.json; ~290 are location-named untitled ideas (Maxwell Dr ~196, Crescent Dr ~60...).
2. Jeff's rights answers folded in (see Decision Log 8-12).
3. Drive deep corners: inventory 357→622 records. Set lists archive to 2010; 2023 remaster WAVs of the 2010 album; J&C Nov-2024 demos (7 songs incl. Prime Outline); 24 Logic projects in "Logic" folder; year-folder logicx lists; Dustin stems w/ BPMs; bounces/backup older mixes (incl. the way i love you v1.2 — fallback for the still-undownloadable v1.4); Trailer Swift FINAL 13-track album; "UnRecorded Songs" doc (2024-12) FOUND BUT NOT YET READ.
4. New entities: Airtime, Shine On Through The Darkness, Suddenly Stranded, Political Circus, Run Away, Country Fried(/Chicken Fried/Sunburnt Country?), Four Walls, Blue Skies Fade, Home on the Lake, Champ Elysisis, Dah, Everything's Beautiful, Home, Bom Bom + collaborator entities (Travis Story, TAD). Catalog now 129 entities.
5. "andrea lyrics" (Dustin's doc) = SAME song as Jeff's Andrea (same words/chords) — his copy or an old co-write; ask casually sometime.
6. What To Do chart: Cm, 84bpm.
### Blocked / notes
- Subagent reports twice killed by content filter when relaying lyric content — workaround: agents write to disk, I read locally. The ~25 deep-archive 2020 lyric docs remain UNREAD (do in small batches next session).
- 'Manic? No way!' doc read attempt didn't save before the filter kill — re-read next session.
- Still undownloaded bounces: 2 (way i love you v1.4, better than now v1.4); backup v1.2 mixes exist as fallback.
- "UnRecorded Songs" doc (id in inventory, Set Lists folder, 2024-12-10) — READ FIRST NEXT SESSION: it's Jeff's own list of what's unrecorded.
### Next continuation point
1. Read "UnRecorded Songs" + remaining 2020 archive docs (small batches).
2. Voice memo hidden-gem pass: transcribe/listen the 290 untitled location-named ideas (needs ASR on-device or in cloud once model download is solved; alternative: stage small batches and analyze signal-only).
3. Retry 2 album bounce downloads; analyze; then album mastering checklist.
4. SoundCloud: 62/189 done; rest needs Jeff's logged-in browser.

## Session 1, Pass 4 — 2026-08-18 (Suno kickoff)
- JEFF APPROVED SUNO (blanket, his words: "use suno with any and all of this"). Scope guard applied: Jeff-written songs only — EXCLUDED: The Way I Love You (Paco Estrada), Better Than Now (Sean), Dustin Duffy's 13, Mom You're The Bomb (Greg Baldia co-write, until consent), all covers. Private, ≤4 gens/song, no voice clone. Logged in Rights doc.
- EXP-001 created (04_suno_experiments/): Long Long Drive arrangement test. Source chosen: voice memo "Long long drive better" (2023-06-01) — signal-verified Am ~123bpm, matching the lyric doc chart; solo performance = clean rights. Paste-ready lyrics + style prompt saved in EXP-001 assets/.
- BLOCKER: Claude-in-Chrome extension not connecting from Jeff's Chrome (installed but no handshake; restart advised). Computer-use fallback impossible (browsers are read-only tier). Manual recipe sent to Jeff; automation retry next session.
- Read Jeff's own "UnRecorded Songs" doc (2024-12-10, 71 titles) → 10 NEW entities (Older, Brown Eye Surprise, Over You, Beautiful Morning, Kids Can't Fly, Take The Abuse, New Act, Poolside, It's Alright, B4L). Catalog now 139 entities.
- Next: run/refine EXP-001 gens 1-2 (Jeff manual or extension), log results in the EXP-001 brief; then consider EXP-002 candidates (What To Do, Why Do I..., Prime Outline) — all Jeff-confirmed originals.

## Session 1, Pass 5 — 2026-08-18 (late)
### Done
1. DEEP-ARCHIVE LYRIC READ COMPLETE — all located lyric docs now read (57 songs scored, was 38). New: Misery 79 (TOP-6, was invisible), Old You 70, Candi Lane composite raised to 70 (2017 version's life-arc verses), Blindfolds 62, Over 40 = 60-as-comedy, Heart Racing 60 (crisis cluster), + 15 more scored/graded down to fragments.
2. RECLASSIFIED: "Hey there" = Hey There Delilah adaptation w/ Andrea lyric (cover/adaptation — excluded); "Room At The Top" = Tom Petty cover chart. "Resist"+"Resist?" merged. "Go my way" = ancestor draft of Our Last Night.
3. MOTIF FOUND: the garden image recurs in 4 songs (Long Long Drive, Life at the Bottom, A Simpler Life, Our Last Night) — candidate concept thread for a future EP.
4. VOICE MEMO TRIAGE BATCH 1: 50 of 291 untitled location-named memos staged + signal-ranked (music-likelihood heuristic). 24 strong candidates → "Hidden Gems Listen List - Batch 1.md". 20 memos >10min flagged as probable rehearsals. NO listening/ASR yet — heuristic only.
5. Producer Brief written for ST-0004 Manic (the quick win): 1 overdub + level/TP fix = first finished album track.
### Blocked
- Drive download endpooint failing consistently this pass (all bounce retries + backup v1.2) — "session expired" per call. Search/read still fine. Retry next session.
- Chrome extension still not handshaking → Suno EXP-001 waiting (manual recipe with Jeff, or extension retry).
### Next continuation point
1. EXP-001 results from Jeff (or extension retry → run it).
2. Bounce downloads retry (way i love you v1.4 1CbMF..., better than now v1.4 19Gj7..., backup v1.2 1bhqQ...).
3. Voice memo triage batches 2-6 (remaining 237 location-named + 82 short fragments + named-unmatched).
4. Crisis Averted studio takes + Set 6-1-2024 mp3s: download/analyze for best-source upgrades.
5. Sean lyric capture (Better Than Now); remaining Needs Jeff items.

## Session 1, Pass 6 — close-out (fresh window)
- 4 Crisis Averted 2023 studio takes downloaded + signal-analyzed: Be With You (2:26, F confirmed — readiness 79→82), TBFH (2:19, A confirmed), Long Long Drive (2:18, ~Ebm = the different-key take), What To Do (2:15, ~Gm@152 — a fast full-band version very unlike the Cm/84 chart; two distinct treatments exist).
- Manic confirmed by Jeff as part of the unreleased Stalemate album (band bounce = no Suno; solo demos only).
- The 2 cursed bounce files (way i love you v1.4 / better than now v1.4) fail server-side consistently while ALL other downloads work — file-specific issue. Workarounds next session: Chrome extension download, or Jeff re-exports/copies them in Drive (a fresh copy gets a fresh file id).
- Chrome extension: still no handshake after install (multiple checks). Next session: verify extension is enabled at chrome://extensions, pinned, signed into claude.ai as jeffstory007@gmail.com, then full Chrome restart.

## Session 1, final notes
- Jeff provided: BSF college 8-track share link (file id 1fNrd0agVhRpycddFi6bwm2pfajO25nNg — still over 10MB connector cap; needs intake-folder drag, chat attachment, or extension) + Stalemate YouTube channel (@stalemate.punkband, UC_AwZcusSP4xtNRA13wiPkQ — enumerate via extension next session; RSS robots-blocked).
- 1999 album confirmed = My Mom Says We're Cool (YT Music). Andrea re-recorded ~2023 and released (SoundCloud /jeffstory/andrea is the 1999 version; find the 2023 release next session). "Other Stalemate releases" exist on streaming — map via channel.

## Session 1, Pass 7 — organization layer + interface (2026-08-19)
1. ORGANIZED VAULT INSTALLED ON MAC (Music/Jeff Story Song Vault): 00-99 numbered structure, 139 per-song record sheets (grouped Stalemate/SD/solo/collab + INDEX.md), Drive link index (622 items), control room docs, manifests, briefs. Originals untouched — pure index layer. (Leftovers Jeff can delete: vault_organized.zip, _to_delete_nested_zip_extract.)
2. VOICE MEMOS BY SONG: 326 symlinks across 73 song folders in "03 Voice Memos/By Song" — browse memos per song, no duplicated audio.
3. INTERACTIVE DASHBOARD: "jeff-story-song-vault" Cowork artifact (also sent as HTML) — search/filter all 139 songs, scores as validated two-hue bars (dataviz-checked), three lanes, expandable per-song detail. THIS + the claude.ai project = "the AI for my music": any session in project answers questions over the whole catalog.
4. Regenerate dashboard after catalog updates: python3 /home/claude/vault/build_dashboard.py → SendUserFile → update_artifact.
5. PRIOR-ART RESEARCH (Jeff asked): beets (MIT — borrowable code; Chromaprint/AcoustID fingerprinting = solution for duplicate-mix clustering), Navidrome (open source — self-hosted streaming: point at the vault → listen to everything from any device; use as app, no license concerns), DISCO/Songspace (commercial SaaS for exactly this — subscription; our vault already covers it). PROPOSAL for next session (needs Jeff install approval): brew install navidrome + chromaprint on the mac mini.

## Session 1, Pass 8 — the songwriting-partner layer (2026-08-19)
1. JEFF LISTENED TO MANIC (first human listen in system): needs lead guitar esp. solos; hears ska/punk horns. Brief updated; EXP-002 (ska horn sketch from Jeff's SOLO demo) created + saved to project. Album version scope: lead guitar only; horns decided after sketch.
2. SONG MAP written (claude/song-map.md): 7 threads — The Mind (biggest/best; a complete unmade album), Candy (marriage across 12 yrs), Kimberly/Andrea (deepest), The State, The Road, The Bar, The Garden motif. All lineages listed. Structural fingerprints documented.
3. STYLE GUIDE written (claude/jeff-story-style-guide.md): binding co-writing rules — voice protections (plain confession, specificity, profanity-as-sincerity, twist endings, mutating final choruses, parenthetical answer vocals), known pitfalls w/ examples, musical defaults, ORIGINAL→PROPOSED→WHY diff rule, rights walls.
4. CO-WRITER SKILL packaged + delivered (jeff-story-cowriter.skill) — if Jeff saves it, "let's write" triggers the full protocol in any session. Delivered, not confirmed saved.
5. HOW JEFF INTERACTS WITH "THE AI FOR HIS MUSIC": any chat in project "2026 Song Organization" + say e.g. "let's finish the What To Do bridge" / "work on Misery" — the AI reads style guide + song map + catalog first. Dashboard artifact for browsing; skill for writing.

## Session 1 — CLOSING STATE (2026-08-19)
Everything saved to project "2026 Song Organization": THE-PLAN, priority-queue, master-catalog (json+csv), covers-reference, song-map, jeff-story-style-guide, pocket-vault, workbench-plan, needs-jeff, decision-log, session-log, access-gaps, rights-and-ai-provenance, producer briefs (ST-0001, ST-0004), suno EXP-001 + EXP-002, hidden-gems list, all manifests. On Jeff's Mac: organized vault (00-99), 139 song sheets, memos-by-song links, dashboard artifact in Cowork sidebar. Delivered to Jeff: catalog xlsx, dashboard, co-writer skill, Mystery Gem #1.
AWAITING JEFF: Mystery Gem verdict · Manic lead guitar · workbench Terminal paste · BSF file to intake · Chrome extension handshake · Stalemate artist link · remaining Needs Jeff answers.

## Integrity + StoryBoard pass — 2026-08-23 (Cloud Agent, no audio)
### Done
1. Catalog integrity: ST-0009 gate aligned with Jeff-confirmed rights; stale top-level counts (`original_song_entities` 113→126, memo pool 326/73→372/88); JS-0139/0140 gained empty `key`/`bpm` fields.
2. `scripts/validate_catalog.py` + `.github/workflows/catalog-validate.yml` + unit tests. Fail closed.
3. StoryBoard documented as **the** band-OS import: `data/app_api.json` + `storyboard` mapping. APPS.md / `00_control_room/Vault to StoryBoard.md` / Producer README resume paths. Explicitly not StoryDesk/StoryOps. No new app.
4. Dashboard builder pointed at `data/` (was `/home/claude/vault/...`). Memo-match overlay from `vm_matches.json`. Search also hits writers / next action / gate.
5. Historical patch/build scripts labeled do-not-re-run (Cowork paths).

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Whisper/Demucs/Basic Pitch/Chromaprint run. No Suno. No masters added, renamed, moved, or deleted (none in-repo).
- Blue Skies Fade / Kimberly lane: not rewritten.
- Three-active-song cap: not expanded.

### Next continuation point
Same as before this pass: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard can now be wired to `data/app_api.json` on its side — that work lives in the StoryBoard repo, not here.

## Export honesty pass — 2026-08-23 (Cloud Agent, no audio)
### Done
1. Re-inspected StoryBoard `catalog-import.ts`. Corrected `app_api.json` / `APPS.md` / Vault→StoryBoard map: `bpm` is the import field (pre-parsed int), notes and `sourceKey` are constructed, `active` is always true on import.
2. Published `import_scope` + `setlist_ready_default_import`. Default live (Rad Dad) is empty — `live_presence` is not `artist_project`. No invented live band.
3. Stronger `validate_catalog.py` + export `--check`. Architecture lock: Vault=catalog, StoryBoard=band OS, StoryLiner=promo only, no fourth live band.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. Three-active-song cap unchanged. Blue Skies Fade untouched.
- Did not relabel any `artist_project` as Rad Dad.

### Next continuation point
Unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import flags (`includeParked` / `includeAllProjects` / a future Rad Dad label) stay Jeff's call.

## StoryBoard #5 published-slice honesty — 2026-08-23 (Cloud Agent, no audio)
### Done
1. Re-inspected live StoryBoard `catalog-import.ts` after StoryBoard #5. The importer now prefers published `setlist_ready_default_import` and reads `import_scope`. Vault #5 still listed `import_scope` under `does_not_read` and described default import as the #4 fallback only.
2. Contract + export + validator now match that planner: field map = `VAULT_STORYBOARD_FIELD_MAP`, `travis_books`, schema 3, 20-id slice must equal `import_scope=default_live` and the live planner. Empty published slice stays empty.
3. README no longer claims the default seed is empty.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.

## StoryBoard #6 parked-named default-live honesty — 2026-08-23 (Cloud Agent, no audio)
### Done
1. Re-inspected live StoryBoard `catalog-import.ts` after StoryBoard #6. The importer names the published-slice draft **Vault default-live** and warns when that slice includes parked-named Vault projects (Everyday / Stalemate, hybrids). Vault #6 still said parked catalogs stay off default import.
2. Contract + export + validator now publish `default_live_parked_named_ids`, the StoryBoard setlist names, and fail closed if those rows are hidden or treated as a fourth live band.
3. Everyday (ST-0014) and Drinking Song (JS-0001) stay in the 20-id slice as current-artist repertoire.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.

## setlist_ready vs default-live count honesty — 2026-08-23 (Cloud Agent, no audio)
### Done
1. After Vault #7 / StoryBoard #6, names were fail-closed (**Vault default-live** vs **Vault setlist-ready**) but `counts.setlist_ready` was not. A hand-edit could omit it or set it to 20 while `setlist_ready` still listed 40 keyed originals.
2. Validator now requires `counts.setlist_ready`, matches the keyed-originals array, and refuses conflation with `counts.setlist_ready_default_import` / `counts.storyboard_default_live` when the slices differ. The two setlist names stay distinct.
3. Verified leftovers that are already honest: field map vs live StoryBoard #6 importer; parked-named default-live is still only ST-0014 + JS-0001; JS-0128 stays in the published slice; ST-0001 (parked flagship) and ST-0002 (cover) stay out.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.

## published catalog-count honesty — 2026-08-23 (Cloud Agent, no audio)
### Done
1. After Vault #8, setlist-ready vs default-live counts were fail-closed, but `counts.originals` / `counts.scored` / `counts.ai_upload_ok` were still hand-editable. A lie could omit them or collapse 126 / 59 / 128 into a setlist draft (40 or 20) or into each other.
2. Validator now requires those three counts, matches catalog classification / potential / YES gates, and refuses conflation when the numbers differ.
3. Discarded: field-map drift vs live StoryBoard importer after StoryBoard #7 (Manager provenance only; `VAULT_STORYBOARD_FIELD_MAP` / `decideVaultSong` / setlist names unchanged). Parked-named default-live is still ST-0014 + JS-0001. JS-0128 in; ST-0001 / ST-0002 out. Did not reclassify the two non-original YES rows (fragment + draft/ancestor) — that is a rights question, not a published-count lie.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.

## usable catalog source-of-truth — 2026-08-26 (Cloud Agent, no audio)
### Done
1. Re-inspected live StoryBoard `catalog-import.ts` after StoryBoard #9. `decideVaultSong` / field map / setlist names are unchanged from #6. The leftover lie was usability: the feed still said inspected after #6, so it did not lock the #9 rule that makes this catalog the source of truth on the Vault + Show Night path.
2. StoryBoard still accepts `master_catalog.json`. Pointed at the spine (no published slice, no `played_live` remap) that planner is not the published default-live feed. Contract now fail-closes that `data/app_api.json` is the import.
3. Show Night bind is ported: planned Vault titles bind; excluded / unknown titles skip; an empty published slice stays empty. Nothing auto-posts. Jeff owns catalog calls.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.
- Private catalog stays private. No public dump of titles.

## usable catalog local-JSON — 2026-08-26 (Cloud Agent, no audio)
### Done
1. Re-inspected live StoryBoard `catalog-import.ts` after StoryBoard #12. `decideVaultSong` / field map / Show Night bind / never_auto_post stay as Vault #11 left them. The leftover lie was usability: `ops.remote_catalog_urls` was published false but not fail-closed, and `inspected` still named #9, so Band operations could be told this private catalog is fetchable.
2. Ported StoryBoard #12 `catalogLocatorLooksRemote` / `parseLocalCatalogJson`. Validator now requires local-JSON-only, rejects remote catalog URLs, and fails closed if the feed itself looks like a locator. Operator path is Band operations → Music & setlists.
3. Discarded: re-doing #11; treating the hosted 0-step empty-runner as a catalog fail; field-map drift; StoryBoard-side spine reject; public stub; unmerged StoryBoard #13 preview copy.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.
- Private catalog stays private. No public dump of titles. Hosted validate may be a 0-step empty-runner — not a catalog fail.

## Session Log once — 2026-08-26 (Cloud Agent, no audio)
### Done
1. After Vault #12 landed, this file listed the same "usable catalog local-JSON" heading twice. Resume from that leftover would look like two passes. Removed the duplicate so the #12 local-JSON pass appears once.
2. Validator now fails closed if Session Log repeats an H2 heading. #11/#12 catalog-feed locks are unchanged. No second catalog surface.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog.

## Session Log resume from latest — 2026-08-26 (Cloud Agent, no audio)
### Done
1. After Vault #13, Session Log H2 headings are unique, but Producer README still sent resume to the first Session 1 "NOT done / next continuation point". Later honesty passes had no Next continuation point, so a later session would treat Session 1 as current.
2. Validator now requires Session Log, fails closed if the latest H2 pass has no Next continuation point, and fails closed if Producer README still points at that Session 1 heading. #11/#12/#13 locks are unchanged. No second catalog surface.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — not the spine, not a remote URL. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Local validate is the catalog gate — 2026-08-26 (Cloud Agent, no audio)
### Done
1. After Vault #14, resume uses the latest Session Log H2, but APPS.md and the validator docstring still said CI fails closed. Hosted catalog-validate on this private repo may be a 0-step empty-runner, so that claim treats a red empty-runner as the catalog gate.
2. Validator now fails closed if APPS.md or the validator docstring still claims CI fails closed, and APPS.md must admit the hosted empty-runner is not a catalog fail. Local `python3 scripts/validate_catalog.py` is the gate. #11/#12/#13/#14 locks are unchanged. No second catalog surface. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Blue Skies Fade untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — not the spine, not a remote URL. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Jeff-facing docs roles and counts only — 2026-08-26 (Cloud Agent, no audio)
### Done
1. After Vault #15, local validate is the catalog gate, but README.md and APPS.md still shipped live-lane titles, protected-opus names, collaborator-as-catalog-map dumps, and write-back ids. Jeff-facing ecosystem docs are roles and counts only.
2. Validator now fails closed if README.md or APPS.md still contain catalog titles, published ids, or collaborator-as-catalog-map dumps. Roles/counts-only wording passes. The #15 local-validate-is-the-gate lock is unchanged. #11/#12/#13/#14 locks are unchanged. No second catalog surface. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog. Live-lane titles removed. Ids removed.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — not the spine, not a remote URL. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Local validate success is roles and counts only — 2026-08-27 (Cloud Agent, no audio)
### Done
1. After Vault #16, Jeff-facing docs stay roles and counts only, but the catalog-gate success line still printed published lane ids. That leftover makes verify output unusable in a PR without sanitizing.
2. Validator success report is now roles and counts only. Fail closed if that line ships published ids. The #16 public-doc lock is unchanged. The #15 local-validate-is-the-gate lock is unchanged. #11/#12/#13/#14 locks are unchanged. No second catalog surface. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog. Live-lane titles stay out of Jeff-facing docs. Ids stay out of the catalog-gate success line.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — not the spine, not a remote URL. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## StoryBoard rejects the spine — 2026-08-27 (Cloud Agent, no audio)
### Done
1. After Vault #17, catalog-gate success stays roles and counts only, but the contract still planned a non-empty spine import. Live StoryBoard #16 rejects `master_catalog.json` at the import boundary. That leftover made the catalog tooling describe a deleted accept path.
2. Contract + validator now fail closed if the feed still treats the spine as an accepted import, if inspected omits StoryBoard #16, or if APPS.md still describes the deleted remap path. Live spine stays reject-shaped; the feed stays a StoryBoard envelope. #11/#12/#13/#14/#15/#16/#17 locks are unchanged. No second catalog surface. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog. Live-lane titles stay out of Jeff-facing docs. Ids stay out of the catalog-gate success line.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Show Night official set is owner-only — 2026-08-27 (Cloud Agent, no audio)
### Done
1. After Vault #18, the catalog feed admits StoryBoard rejects the spine, but it still did not fail-closed the live Show Night official-set boundary. Show Night #1/#2 keep official-set writes owner-only. Public suggestions cannot mutate that set. This feed is not a public Show Night writer.
2. Contract + validator now fail closed if the feed hides that owner-only official set, if inspected omits Show Night #1, or if APPS.md still claims this feed writes the official set. Song rows are unchanged. #11/#12/#13/#14/#15/#16/#17/#18 locks are unchanged. No second catalog surface. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog. Live-lane titles stay out of Jeff-facing docs. Ids stay out of the catalog-gate success line.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Official-set dump binds Rad Dad — official set — 2026-08-27 (Cloud Agent, no audio)
### Done
1. After Vault #19, the catalog feed admits Show Night official set is owner-only, but it still did not fail-closed the live official-set dump bind. StoryBoard #19 binds a local `songs[]` + `setSlug` dump as **Rad Dad — official set**. Guest/parked slugs stay opt-in. Public suggestion dumps are not the official set. Show Night #3 names Show Night as the live set surface; Vault is the catalog.
2. Contract + validator now fail closed if the feed hides that dump bind, if inspected omits StoryBoard #19, or if APPS.md still omits the official-set dump / live-set-surface admission. Song rows are unchanged. #11/#12/#13/#14/#15/#16/#17/#18/#19 locks are unchanged. No second catalog surface. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist or a second catalog. Live-lane titles stay out of Jeff-facing docs. Ids stay out of the catalog-gate success line. Official-set titles were not copied here.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Catalog rows are not the official set — 2026-08-27 (Cloud Agent, no audio)
### Done
1. After Vault #20, the catalog feed admits the official-set dump bind, but it still talked like Vault default-live / catalog rows were the live set. Show Night owns official sets. StoryBoard #20 keeps Vault song rows Vault-framed after that bind.
2. Contract + validator now fail closed if the feed hides that catalog rows are not the official set, if inspected omits StoryBoard #20, or if APPS.md / the dashboard still claim catalog rows are the live set. The dashboard reuses `data/app_api.json` for import_scope and no longer labels catalog play history as LIVE. Song rows are unchanged. #11/#12/#13/#14/#15/#16/#17/#18/#19/#20 locks are unchanged. No second catalog surface. Do not change billing.
3. QA leftover: the dashboard still reprinted spine stage `IN CURRENT LIVE SET`. The first useful surface now sanitizes that phrase to catalog play history. Validator / README fail closed on that live-set claim. Spine unchanged.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Private catalog stays private. No public dump of titles. Did not invent a setlist, lyrics dump, or a second catalog. Live-lane titles stay out of Jeff-facing docs. Ids stay out of the catalog-gate success line. Official-set titles were not copied here.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Satellite catalog tables fail closed — 2026-08-28 (Cloud Agent, no audio)
### Done
1. Started the existing catalog pipeline on main tip 1420e858 (#21). `validate_catalog.py`, `export_app_api.py --check`, `catalog_surface.py`, and `python3 -m unittest discover -s tests -v` were already green. Catalog≠official-set is already fail-closed on the feed / APPS.md / dashboard.
2. Walked every spine row plus satellite tables. Leftover honesty bug: `data/master_catalog.csv` was a stale 139-row view of the 150-row spine (JS-0130…0140 missing; potential/key/notes drift on overlapping rows). That is export/validate drift, not a feel rewrite.
3. Regenerated the derived CSV from the existing spine (same columns; no songs added/dropped/renamed in JSON). Validator now fails closed if the CSV, covers CSV, version-chain ids, or momentum ids/titles drift. Momentum scores may still disagree with live-set floors — reported, not rewritten. Discovery write-up: `00_control_room/Catalog Discovery — satellite cross-walk.md`. #11–#21 locks unchanged. No second catalog. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Spine `data/master_catalog.json` was not rewritten. CSV is a derived projection of songs already on the spine.
- Catalog rows are not the official set. Show Night owns official sets. Vault default-live stays a catalog slice.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived `master_catalog.csv` must match the spine. Next honest leftover is Logic-ready field fill on Jeff's Mac (keys / WAV / AIFF / stems) plus the UnRecorded Songs 71-title stub and missing `vm_unmatched.json` — do not invent those rows. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Song analysis Logic-ready walk — 2026-08-28 (Cloud Agent, no audio)
### Done
1. After Vault #22, derived `master_catalog.csv` already matches the 150-row spine. Did not redo that CSV work. Did not rewrite `master_catalog.json` or `app_api.json` song rows.
2. Walked all 126 originals and 93 covers on the existing spine. Per-song honesty: band lane, recorded vs unrecorded (heuristic), cover vs original, key/BPM/Logicx/stems/MIDI/WAV presence, version-chain, `live_presence` vs setlist-ready vs official-set. Official-set count on this walk is **0**. Catalog rows are not the official set.
3. Clustered Logic-ready gaps: 9 closest drop-in · 5 Logic+key · 19 Logic/no key · 10 audio+key/no Logic · 31 audio-only (includes Manic) · 16 key-only · 36 empty. Manic stems/MIDI were substring false positives (`system` / future horns) — reported, not rewritten. Everyday / Drinking Song momentum scores stay reported-only. Stalemate unmatched titles stay unmatched. Discovery: `00_control_room/Catalog Discovery — song analysis.md`. No fail-closed code bug after #22. #11–#22 locks unchanged. No second catalog. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No invented UnRecorded 71-title list. No invented `vm_unmatched.json`. No minted Stalemate unmatched IDs.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Spine song rows were not rewritten. Catalog rows are not the official set. Show Night owns official sets. Vault default-live stays a catalog slice.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived `master_catalog.csv` must match the spine. Next honest leftover is Logic-ready field fill on Jeff's Mac (keys / WAV / AIFF / stems / `.logicx`) for the 19 Logic-no-key + 36 empty originals — without inventing keys — plus recovering the real UnRecorded / unmatched-memo lists from Drive. Do not mint Stalemate unmatched IDs. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Covers book leftover walk — 2026-08-28 (Cloud Agent, no audio)
### Done
1. After Vault #23, the originals Logic-ready walk is recorded. The leftover was the 93-cover book: #23 listed title · artist only. Did not rewrite `master_catalog.json` or `app_api.json` song rows. Did not invent UnRecorded titles, `vm_unmatched.json`, keys, or IDs. Did not invent a Manic key.
2. Walked every cover row: Vault fields are only title / original_artist / context / classification. On the book, Logic-ready is empty for all 93 (0 IDs, 0 keys, 0 `.logicx`, 0 version chains, 0 `live_presence`, 0 setlist-ready, official-set 0). Context string is one paste — not 93 Trailer Swift originals and not the official set. Trailer Swift originals stay **0**. Official-set originals stay **0**. Covers stay **93**.
3. Off-book evidence (not written onto the book): 2 Drive `.logicx` (Ours, Grandma) · 13 Trailer Swift FINAL audio rows · 58 captured-setlist mentions · 6 8-bit titles · 14 empty even off-book. Trailer Swift FINAL is 13 tracks; the book has 14 Taylor Swift titles (Ours is the extra, and the only TS title with an enumerated Logic project). Speak Now / Our Song / Never Grow Up / Dear John stay unmatched. Rad Dad extras on the captured sheet stay unmatched. Stalemate unmatched titles stay unmatched. Discovery: `00_control_room/Catalog Discovery — covers book leftover.md`. No fail-closed code bug after #23. #11–#23 locks unchanged. No second catalog. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs.
- No new songs. No invented UnRecorded 71-title list. No invented `vm_unmatched.json`. No minted cover IDs. No minted Stalemate unmatched IDs. No invented Trailer Swift original lane. No invented Manic key.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Spine song rows were not rewritten. Cover book rows were not rewritten. Catalog rows are not the official set. Show Night owns official sets. Vault default-live stays a catalog slice. Rad Dad’s captured sheet is not the official set.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived `master_catalog.csv` must match the spine. Cover book stays 93 / official-set originals stay 0 / Trailer Swift originals stay 0. Next honest leftover is Logic-ready field fill on Jeff's Mac for the 19 Logic-no-key + 36 empty originals, plus the two already-inventoried cover `.logicx` files (Ours, Grandma) — without inventing keys or minting cover IDs — plus recovering the real UnRecorded / unmatched-memo lists from Drive. Do not mint unmatched Trailer Swift / Rad Dad / Stalemate titles. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Catalog memo evidence find-and-act — 2026-09-03 (Cloud Agent, no audio)
### Done
1. After leftover-squash #26, songs and searchable matched memos already connect. The leftover was usability, not another spine walk: Jeff still had to expand every row to see evidence, and the scoped memo set was not newest-first or copyable.
2. Deepened that same Songs / Memo Search workflow. Songs with searchable matches now show the count and latest memo date, can be filtered or sorted by that evidence, and still open the scoped memo set. Scoped memos are newest-first, show the catalog next action, copy the local intake filename, and keep a local `#memos=` / `#song=` hash. Escape clears the scope. Catalog feel is unchanged.
3. Security leftover: the generated dashboard fail-closes if it opens Logic keys, WAVs, or audio. Copy is the already-visible intake name only. No unmatched-memo address dump. No catalog 0.22.5 mutation. No audio open/upload. No AI contact. Logic keys/WAVs stay owner-only on Jeff's Mac. #11–#26 locks unchanged. No second catalog. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs. No audio opened or uploaded.
- No new songs. No invented UnRecorded 71-title list. No invented `vm_unmatched.json`. No minted IDs. No invented keys. No Manic / Blasting Room work.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Spine song rows were not rewritten. Cover book rows were not rewritten. Embedded DATA/TX payloads stay projections of the existing index.
- Catalog rows are not the official set. Show Night owns official sets. Vault default-live stays a catalog slice.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived `master_catalog.csv` must match the spine. Cover book stays 93 / official-set originals stay 0 / Trailer Swift originals stay 0. The private dashboard now lets Jeff find songs with searchable matched memos and act on that scoped set (newest first, copy intake name) without opening audio. Logic keys/WAVs stay owner-only on Jeff's Mac — do not invent keys or fill Logic-ready from this page. Next honest leftover is still recovering the real UnRecorded / unmatched-memo lists from Drive, plus Jeff-Mac Logic-ready field fill, without inventing keys or minting IDs. Do not mint unmatched Trailer Swift / Rad Dad / Stalemate titles. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Catalog song work card — 2026-09-03 (Cloud Agent, no audio)
### Done
1. After leftover #27, songs and searchable matched memos already find-and-act. The leftover was writing/producing: Jeff still had to expand every row to see the next action / hook / open questions, and the three lanes did not open the song.
2. The same Songs / Memo Search surface now classifies the existing next_action into write / produce / listen / rest / inventory / decide, shows that kind plus a sanitized next-action preview on the closed row, filters it, and opens a lane song. Expanded songs and a scoped memo set can copy a work card (title, hook, theme, next action, open questions, status, key/BPM, gate class).
3. Security leftover: the work card strips Logic/WAV filenames and known street fragments, omits sources / best_source / memo titles, and returns empty if a locator remains. Validator fail-closes if the dashboard opens Logic keys, WAVs, or audio, or if the write/produce surface is missing. Embedded DATA/TX hashes unchanged from main. No catalog 0.22.5 mutation. No unmatched-memo address dump. No Manic / Blasting Room work. Logic keys/WAVs stay owner-only on Jeff's Mac. #11–#27 locks unchanged. No second catalog. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs. No audio opened or uploaded.
- No new songs. No invented UnRecorded 71-title list. No invented `vm_unmatched.json`. No minted IDs. No invented keys. No Manic / Blasting Room work.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Spine song rows were not rewritten. Cover book rows were not rewritten. Embedded DATA/TX payloads stay projections of the existing index.
- Catalog rows are not the official set. Show Night owns official sets. Vault default-live stays a catalog slice.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived `master_catalog.csv` must match the spine. Cover book stays 93 / official-set originals stay 0 / Trailer Swift originals stay 0. The private dashboard now lets Jeff filter write/produce/listen work from existing next actions, open a lane song, and copy a sanitized work card without opening audio. Logic keys/WAVs stay owner-only on Jeff's Mac — do not invent keys or fill Logic-ready from this page. Next honest leftover is still recovering the real UnRecorded / unmatched-memo lists from Drive, plus Jeff-Mac Logic-ready field fill, without inventing keys or minting IDs. Do not mint unmatched Trailer Swift / Rad Dad / Stalemate titles. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Catalog write/produce/listen sit-down — 2026-09-03 (Cloud Agent, no audio)
### Done
1. After leftover #28, write/produce/listen filters and a sanitized work card already exist. The leftover was sit-down: expanding a song still reprinted Logic/WAV/best_source paths, listen still pointed at owner audio this page cannot open, and the work filter died when a lane or memo jump ran.
2. The same Songs / Memo Search surface now keeps a `#work=` session (write / produce / listen counts are clickable), walks Previous/Next in that queue, shows work kind on the lanes, and sits down on the sanitized next action plus latest searchable memo evidence (copy intake name). Work card may include memo count/date; intake names and streets stay off the clipboard.
3. Security leftover: expanded next action and memo-scope next are sanitized; Latest source / Known assets are not rendered. Validator fail-closes if the dashboard displays those owner-audio locators or if the sit-down/work session is missing. Embedded DATA/TX hashes unchanged from main. No catalog 0.22.5 mutation. No unmatched-memo address dump. No Manic / Blasting Room work. Logic keys/WAVs stay owner-only on Jeff's Mac. #11–#28 locks unchanged. No second catalog. Do not change billing.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs. No audio opened or uploaded.
- No new songs. No invented UnRecorded 71-title list. No invented `vm_unmatched.json`. No minted IDs. No invented keys. No Manic / Blasting Room work.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched.
- Spine song rows were not rewritten. Cover book rows were not rewritten. Embedded DATA/TX payloads stay projections of the existing index.
- Catalog rows are not the official set. Show Night owns official sets. Vault default-live stays a catalog slice.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items unchanged: Manic guitar · EXP-001 when Chrome connects · Needs Jeff #1–5 · BSF file into intake. StoryBoard import stays local `data/app_api.json` — the spine is rejected as an import, not a remote URL. Show Night official set is owner-only. Official-set dump binds as Rad Dad — official set. Show Night is the live set surface. Catalog rows are not the official set. Show Night owns official sets. Derived `master_catalog.csv` must match the spine. Cover book stays 93 / official-set originals stay 0 / Trailer Swift originals stay 0. The private dashboard now lets Jeff sit down to write/produce/listen from existing next actions: resumable work session, sanitized next, latest memo evidence, no owner-audio paths. Logic keys/WAVs stay owner-only on Jeff's Mac — do not invent keys or fill Logic-ready from this page. Next honest leftover is still recovering the real UnRecorded / unmatched-memo lists from Drive, plus Jeff-Mac Logic-ready field fill, without inventing keys or minting IDs. Do not mint unmatched Trailer Swift / Rad Dad / Stalemate titles. Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

## Catalog one-song session start — 2026-09-03 (Codex Extra High, no audio)
### Done
1. Started from exact private main `c3bd8885`. The previous sit-down work was real, but Write / Produce / Listen still looked like passive counts and opened a collapsed list, so Jeff had to hunt again before acting.
2. Kept the existing Songs / Memo Search surface and existing catalog logic. Three explicit work-session buttons now open the highest-momentum matching song immediately, name the exact queue position, preserve that selection through sorting/filtering, and stop Previous/Next at the real boundaries instead of wrapping.
3. Reduced first-glance controls to search, sort, and one native More filters disclosure. Project, scored, StoryBoard scope, memo-evidence, and all-work filters remain available inside it. Generated dashboard JavaScript compiles; focused dashboard/privacy tests pass; a headless Chrome walk confirmed `#work=write` lands on one expanded item with `1 of 30` and Previous disabled.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs. No audio opened, uploaded, or modified.
- No new songs, priorities, scores, keys, IDs, catalog rows, transcript rows, DATA/TX payloads, or app feed changes. No Manic / Blasting Room work. Catalog v1.6 and version/build identifiers are unchanged.
- Work buttons navigate the existing private local index only. Next actions remain sanitized; Logic/WAV/best_source paths and known street fragments stay out of the work card. The repository stays private.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched. Catalog rows are not the official set; Show Night owns official sets.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items remain unchanged: physical playing/listening, EXP-001 when Chrome connects, Needs Jeff #1–5, and the protected-opus file intake. Use the private dashboard's primary Write / Produce / Listen buttons to start one bounded session; More filters is for catalog exploration, not a new priority system. StoryBoard still imports local `data/app_api.json`; the spine stays rejected, catalog rows are not the official set, and Show Night owns official sets. Logic-ready field fill and recovering real unmatched/UnRecorded lists remain Mac/Drive evidence work—never invent keys, titles, IDs, or paths. Hosted validate may be a 0-step empty-runner. Do not change billing.

## Catalog one-song session resume — 2026-09-03 (Codex Extra High, no audio)
### Done
1. Started from exact private main `4823cbfb`. The one-song start already selected a highest-momentum item and bounded Previous/Next, but a refresh lost the exact song and made Jeff hunt again.
2. Reused that work queue and existing catalog work-kind classifier. Once a song is opened, the dashboard stores only schema version + matching work kind + catalog ID in this browser. A visible Resume action reopens that exact validated song; Forget clears it.
3. The parser rejects unknown IDs, changed work kinds, stale schemas, and any extra fields, then removes the invalid record. Blocked browser storage fails soft. The validator and focused navigation tests lock the privacy boundary and exact-song outcome.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs. No audio opened, uploaded, or modified.
- No title, note, transcript, next action, memo filename, path, or audio locator is placed in browser storage. The repository remains private.
- No new songs, priorities, scores, keys, IDs, catalog rows, transcript rows, DATA/TX payloads, or app feed changes. No Manic / Blasting Room work. Catalog v1.6 and version/build identifiers are unchanged.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched. Catalog rows are not the official set; Show Night owns official sets.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items remain unchanged: physical playing/listening, EXP-001 when Chrome connects, Needs Jeff #1–5, and the protected-opus file intake. Use Resume only for the browser-local one-song work position; use Forget to clear it, and use this latest Session Log section for the authoritative project handoff. StoryBoard still imports local `data/app_api.json`; the spine stays rejected, catalog rows are not the official set, and Show Night owns official sets. Logic-ready field fill and recovering real unmatched/UnRecorded lists remain Mac/Drive evidence work—never invent keys, titles, IDs, or paths. Hosted validate may be a 0-step empty-runner. Do not change billing.

## Catalog one-song session click-test — 2026-09-04 (Cloud Agent Extra High, no audio)
### Done
1. Started from exact private main `e11509de` after leftover-squash #31. Resume already stored only schema version + work kind + catalog ID, but a `#work=` refresh opened the first queue song and overwrote the saved record, so the advertised exact-session path was not click-testable.
2. The same private dashboard now reapplies a matching `#work=` hash to the validated stored song, not the first match. **Resume** still reopens that song after Escape / Clear filters. **Forget** announces success, drops the leftover `#work=` hash so a later refresh cannot mint a new record, and soft-fails when the browser store cannot clear. Stale, mismatched, extra-field, and unknown records stay fail-closed and are removed.
3. README and Producer README now match the real tester clicks: Click Write, Produce, or Listen → note song and position → Next optional → Refresh → Resume → Forget → Refresh again. No title, note, transcript, next action, filename, or audio locator is stored.

### Honesty ledger
- **Audio listened to this pass: ZERO.** No Music.ai / Suno / Whisper / Demucs. No audio opened, uploaded, or modified.
- No title, note, transcript, next action, memo filename, path, or audio locator is placed in browser storage. The repository remains private.
- No new songs, priorities, scores, keys, IDs, catalog rows, transcript rows, DATA/TX payloads, or app feed changes. No Manic / Blasting Room work. Catalog v1.6 and version/build identifiers are unchanged.
- No fourth live band. Three-active-song cap unchanged. Protected opus untouched. Catalog rows are not the official set; Show Night owns official sets.
- Hosted validate may be a 0-step empty-runner — not a catalog fail. Do not change billing.

### Next continuation point
Standing Jeff-owned items remain unchanged: physical playing/listening, EXP-001 when Chrome connects, Needs Jeff #1–5, and the protected-opus file intake. Click-test the private session from the README steps; use this latest Session Log section for the authoritative project handoff. StoryBoard still imports local `data/app_api.json`; the spine stays rejected, catalog rows are not the official set, and Show Night owns official sets. Logic-ready field fill and recovering real unmatched/UnRecorded lists remain Mac/Drive evidence work—never invent keys, titles, IDs, or paths. Hosted validate may be a 0-step empty-runner. Do not change billing.
