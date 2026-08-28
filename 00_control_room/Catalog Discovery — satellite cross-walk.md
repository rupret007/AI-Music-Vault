# Catalog Discovery — satellite cross-walk
*2026-08-28 · Cloud Agent · no audio · not a second catalog · not the official set*

Walked every row on the committed spine (`data/master_catalog.json` v1.6, tip 1420e858 / Vault #21) and cross-walked the satellite tables. Pipeline first: `validate_catalog.py`, `export_app_api.py --check`, `catalog_surface.py`, `python3 -m unittest discover -s tests -v` were already green. Catalog rows are not the official live set. Show Night / Jeff own official sets.

This page is counts + gaps. It does not add, drop, or rename songs.

## Pipeline

| Gate | Result |
|---|---|
| `python3 scripts/validate_catalog.py` | green before and after this pass (roles and counts only) |
| `python3 scripts/export_app_api.py --check` | green — feed matches exporter |
| `python3 scripts/catalog_surface.py` | library only; import exits 0 |
| `python3 -m unittest discover -s tests -v` | green (173 → expanded this pass) |
| `python3 scripts/export_catalog_csv.py --check` | **was red** (stale CSV); green after derived rebuild |
| hosted `catalog-validate` | may be a 0-step empty-runner — not a catalog fail |

`scripts/build_catalog.py` is a historical Cowork one-shot — do not re-run. `build_xlsx.py` needs openpyxl and is derived, not the spine.

## Honest counts (spine)

| Measure | Count | Notes |
|---|---|---|
| Entities | 150 | claimed `original_song_entities` 126 matches `classification==original` |
| Originals | 126 | Jeff-written ranking pool |
| Non-original entities | 24 | 13 Dustin Duffy · 2 collaborator · 1 Paco outside composition · 1 Sean band original · 2 co-write (incl. protected opus) · 1 ancestor draft · 1 Delilah adaptation · 1 Tom Petty cover chart · 1 Dorivalland reference · 1 original fragment |
| Covers table | 93 | `covers[]` == `covers_reference.csv` titles; never ranked against originals |
| Scored potential | 59 | readiness filled on only 12 (album-adjacent) |
| Spine momentum field | 120 / 126 originals | 7 originals have no momentum field |
| `momentum.json` | 119 | subset; no unknown ids |
| Parseable key | 43 / 150 | 40 originals |
| Parseable BPM | 26 / 150 | 14 originals |
| `live_presence` | 21 | catalog play history — **not** the official set |
| AI-upload gates | 128 YES · 20 NO · 2 NEEDS CONSENT | |
| StoryBoard feed | 150 songs | export comparable-equal to spine |
| `setlist_ready` | 40 | keyed originals |
| Vault default-live | 20 | catalog slice, **not** the official set |
| Parked-named in that slice | 2 | Everyday (ST-0014) · Drinking Song (JS-0001) — current artist, not a fourth band |
| Version chains | 76 songs · 141 files | 88 audio · 47 Logic projects (`logic-project` + `logic_project` spelling split) · 6 studio-takes |
| Voice memos | 916 DB / 916 transcribed / 915 jsonl | 372 matched to 88 songs · 1 jsonl gap = corrupt `20250426…A30FC564` |
| GDrive inventory | 622 rows | 52 captured doc texts |
| Events inbox | 0 files | live-set truth still inferred |

### Recorded vs unrecorded (heuristic on existing fields — not a new score)

| Bucket | Count | How it was counted |
|---|---|---|
| High recording (`rec_pct` ≥ 80) | 17 | mostly album / released |
| Has audio evidence (mix / bounce / wav / SoundCloud in sources) | 52 | not the same as “finished” |
| Flagged unrecorded / lyric-only / `rec_pct` 0 | 36 | includes It’s Alright |
| Unknown `rec_pct` | 45 | do not invent a recorded flag |

### Band tags (catalog projects — not a live set)

| Tag | Spine `artist_project` | `live_presence.band` |
|---|---|---|
| Jeff Story | 88 | — |
| Stalemate | 32 + 2 hybrid | 12 |
| Something Dirty | 11 + 3 hybrid | 8 |
| Rad Dad | 1 hybrid phrase only | 3 (catalog play history) |
| Dustin / UNK | 14 | — |
| Travis Story | 1 | booker, not a live band |
| Trailer Swift | 0 song rows | parked cover project; 93 covers file the TS/pop-punk book |

Rad Dad’s captured setlist sheet is almost all covers. The three originals named there (Drinking Song, Everyday, The Way I Love You) already exist on the spine. That sheet is **not** the official set.

## Cross-walk gaps (leave the blob alone unless noted)

### Fixed this pass (derived table only)
- **`master_catalog.csv` was 139 rows vs 150 spine rows.** Missing JS-0130…0140 (already on the JSON spine from the transcript pass). Potential drift on SD-0007 / JS-0128; key drift on JS-0128; notes drift on 26 overlapping rows. Regenerated from the spine. Same columns. Not a second catalog.

### Reported — do not silently rewrite
- **`momentum.json` vs spine floors.** Everyday (ST-0014) 30 vs spine 75; Drinking Song (JS-0001) 13 vs spine 75. Decision 38 applied a live-set momentum floor. 14 last-activity mismatches. 7 originals have no `momentum.json` row (Better Together, 90% / 99 Percent, Four Walls, Home on the Lake, Champ Elysisis, A New Hope, Anthem Part 2). Fail-closed on unknown ids / title drift only.
- **`vm_unmatched.json` is missing.** `voice_memo_pool.note` still points at it. Do not invent the unmatched list.
- **UnRecorded Songs.md is a 4-line stub.** Spine note says Jeff’s 71-title backlog was captured. The title list is not in-repo. Do not invent 71 songs.
- **Stalemate song list unmatched titles** (do not mint entities): “Let’s Go To New Mexico” (possible alias of catalogued Going To New Mexico), “Tooted last Tuesday”, “Chains of pain (castle)”.
- **Spine stage on JS-0128 still says `IN CURRENT LIVE SET`.** Dashboard / first useful surface already sanitizes. Do not rewrite the spine. That row is catalog play history, not the official set.
- **`transcripts.jsonl` uses `.txt` names; `vm_transcribed.json` uses `.m4a`.** Stem-join matches 915/916. Not a second transcript catalog.
- **events/README.md examples still use titles / one published id.** Internal inbox doc; not Jeff-facing README/APPS.

## Logic-ready gaps (Logic Pro, not Ableton)

Primary DAW is Logic Pro. Discovery looked for WAV / AIFF / MIDI / stems / `.logicx` mentions on the spine + version chains.

| Logic-ready signal (originals, 126) | Count |
|---|---|
| Has any key | 40 |
| Has any BPM | 14 |
| Mentions a Logic project | 33 |
| Mentions WAV | 26 |
| Mentions stems | 1 (Turn Over The Flag) |
| Mentions MIDI | 1 (Manic) |
| No Logic-ready mention at all | 83 |

Do not invent keys, BPMs, or stem paths. Those fields get filled from Jeff’s Mac / Drive, not from this pass.

## Catalog vs official set (already fail-closed)

- Vault default-live (20) ≠ setlist-ready (40) ≠ originals (126) ≠ official set.
- Show Night binds a local official-set dump as **Rad Dad — official set**. This feed does not write that set.
- Dashboard reuses `data/app_api.json` and does not reprint `IN CURRENT LIVE SET`.
- No fourth live band. Travis books. Nothing auto-posts.

## Conclusion

Hypothesis held: leftover value was cross-walk + honesty, not a new app.

**This pass:** fail-closed the derived CSV (and satellite id/title honesty) so the 150-row spine cannot be hidden behind a 139-row table.

**Next honest leftover:** Logic-ready field fill on Jeff’s Mac (keys / WAV / AIFF / stems) and recovering the real UnRecorded Songs / unmatched-memo lists from Drive — without inventing rows. Do not deploy. Do not merge this draft without review.
