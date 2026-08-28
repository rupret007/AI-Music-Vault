# Catalog Discovery — covers book leftover
*2026-08-28 · Cloud Agent · no audio · leftover after #23 originals walk · not a second catalog · not the official set*

Walked every **93 covers** on the committed spine (`data/master_catalog.json` `covers[]` == `data/covers_reference.csv`, tip `9330052` / Vault #23). Trailer Swift originals stay **0**. Official-set originals stay **0**. Catalog rows are not the official live set. Show Night / Jeff own official sets.

This page is per-cover honesty + Logic-ready clusters for the cover book. It does not add, drop, or rename covers. It does not rewrite `master_catalog.json` or `app_api.json` song rows. It does not invent UnRecorded titles, `vm_unmatched.json`, keys, or IDs. It does not invent a Manic key. Stalemate unmatched titles stay unmatched.

#23 already listed the 93 titles and artists. That leftover was thin: title · artist only, plus one sentence that the context string is copy-paste. This pass walks Vault fields, Logic-ready gaps, version-chain, and `live_presence` vs setlist-ready vs official-set on every cover row, then clusters what is closest to a Logic drop-in vs empty. Trailer Swift vs Rad Dad vs other lanes are recorded from evidence, not from the pasted context.

## What this walk is (and is not)

| Allowed here | Forbidden here |
|---|---|
| Walk all 93 cover rows as a reference book | Rank covers against originals or invent a Trailer Swift original lane |
| Report Vault fields that are already on `covers[]` | Invent cover IDs, keys, BPM, `.logicx`, stems, MIDI, or WAV paths on the book |
| Cluster Logic-ready gaps on the book vs off-book Drive / setlist docs | Copy setlist-doc keys onto cover rows |
| Note Trailer Swift vs Rad Dad vs Stalemate vs 8-bit honestly | Treat copy-paste context as 93 official-set rows or 93 Trailer Swift originals |
| Leave unmatched Drive / setlist titles unmatched | Mint cover rows for Speak Now / Our Song / Never Grow Up / Dear John or Rad Dad extras |
| Leave Stalemate unmatched titles unmatched | Mint IDs for Tooted last Tuesday / Let’s Go To New Mexico / Chains of pain |

Official-set originals on this walk: **0**. Official-set covers on this walk: **0**. `scripts/catalog_surface.py` already fail-closes official-set claims. That must stay fail-closed.

No new fail-closed code bug was found after #23. This leftover is the cover-book write-up.

## Method

Inputs (read-only): `data/master_catalog.json` `covers[]` and `songs[]`, `data/covers_reference.csv`, `data/app_api.json` (scope / setlist-ready / default-live / official-set flags only), `data/version_chains.json`, `01_source_manifests/gdrive/inventory.jsonl`, `01_source_manifests/gdrive/doc_texts/Rad Dad Setlist.md`, `01_source_manifests/gdrive/doc_texts/Stalemate Set 4-26-24.md`, `01_source_manifests/gdrive/doc_texts/Stalemate Set 3-13-24.md`, `01_source_manifests/gdrive/doc_texts/Stalemate song list.md`, `01_source_manifests/gdrive/doc_texts/UnRecorded Songs.md`, `00_control_room/Catalog Discovery — song analysis.md`.

Primary DAW is **Logic Pro**. Ableton is not the drop-in target.

Cover-book Vault fields are only `title`, `original_artist`, `context`, `classification`. There is no `song_id`, `key`, `bpm`, `.logicx`, WAV/AIFF, stems, MIDI, `live_presence`, or version-chain pointer on any cover row.

Logic-ready clustering **on the book** (same rules as #23; do not invent a key):

| Cluster | Rule | n on this book |
|---|---|---|
| `closest_logic_dropin` | `.logicx` + WAV/AIFF/stems + parseable key on the cover row | **0** |
| `logic_project_plus_key` | `.logicx` + parseable key on the cover row | **0** |
| `logic_project_no_key` | `.logicx` on the cover row; no key | **0** |
| `audio_plus_key_no_logic` | audio + parseable key on the cover row | **0** |
| `audio_only` | audio on the cover row; no key | **0** |
| `key_only` | parseable key on the cover row | **0** |
| `empty_logic_ready` | none of the above | **93** |

Off-book evidence (Drive inventory + captured setlist docs) is a **second column**, not a Vault field. Do not write it onto `covers[]`.

| Off-book cluster | Rule | n |
|---|---|---|
| `drive_logicx_off_book` | enumerated Drive `.logicx` whose title matches a book row | 2 |
| `drive_audio_off_book` | Trailer Swift FINAL MP3 and/or parent backing-track MP3 | 13 |
| `setlist_mention_only` | title appears on captured Rad Dad / Stalemate setlist docs | 58 |
| `eightbit_title_only` | book title already ends in `(8-bit)`; no setlist/Drive match | 6 |
| `empty_even_off_book` | context string only | 14 |

Setlist-doc keys are **not** Vault keys. Docs disagree on several titles (When I Come Around D vs G; In Bloom B vs A#; Breed F#m vs Gb; Sparks Fly Bb vs Bm; Middle Name A vs blank). Do not pick a winner. Do not invent a Manic key (Manic is an original; still blank on the spine).

## Headline counts

| Measure | n | Official set? |
|---|---|---|
| Cover rows walked | 93 | **0** |
| Unique context strings | 1 | copy-paste, not 93 official-set rows |
| Cover Vault IDs | 0 | do not mint |
| Cover keys / BPM / `.logicx` / WAV / stems / MIDI on the book | 0 / 0 / 0 / 0 / 0 / 0 | do not invent |
| Version-chain keys that are covers | 0 | chains are song_id-keyed |
| `live_presence` on cover rows | 0 | play history lives on song rows (21 originals) |
| Covers in `setlist_ready` | 0 | setlist-ready is 40 keyed originals |
| Covers in Vault default-live | 0 | 20-id catalog slice |
| Official-set covers | 0 | must stay 0 |
| Official-set originals | 0 | must stay 0 |
| Trailer Swift original rows | 0 | parked cover project; not an original lane |
| Title collisions with `songs[]` | 0 | book titles do not duplicate spine song titles |

| Lane evidence (a cover may have more than one; context string is ignored) | n |
|---|---|
| `trailer_swift_drive` | 14 (the 14 Taylor Swift book titles: 13 FINAL + Ours logicx/backing) |
| `rad_dad_setlist_doc` | 30 |
| `stalemate_setlist_doc` | 46 |
| both Rad Dad + Stalemate captured sheets | 16 |
| `eightbit_title` | 6 |
| `christmas_logicx_drive` | 1 (Grandma) |
| `context_only` | 14 |

35 original artists. Same top counts as #23. Do not re-rank.

## Catalog vs official set (must stay fail-closed)

Vault default-live (20) ≠ setlist-ready (40) ≠ originals (126) ≠ covers (93) ≠ official set.

Show Night binds a local official-set dump as **Rad Dad — official set**. This feed does not write that set. Cover rows are not that set. `cover_not_active` on the feed is 23 **non-original song entities** (Paco / Sean / Dustin / adaptations / opus), not the 93-cover book.

Spine cover-or-adaptation entities already walked in #23 stay off this book: `JS-0054 Hey There` (Delilah adaptation) and `JS-0069 Room At The Top` (Tom Petty chart). Do not fold them into the 93. Do not mint cover IDs for them.

`ST-0002 The Way I Love You` is on Rad Dad’s captured setlist as an “original” credit. Classification stays **Paco outside composition** — not in the 126 originals, not in the 93-cover book, not default-live.

## Trailer Swift vs Rad Dad vs other lanes (honest)

The context string on **all 93** covers is `Rad Dad / Stalemate sets / Trailer Swift / 8-bit series / SoundCloud`. That is one pasted phrase. It is not lane membership.

| Lane | What the evidence actually says | Official set? |
|---|---|---|
| **Trailer Swift** | Jeff’s solo Taylor Swift tribute. 0 original rows. Parked catalog project in StoryBoard (`import_scope` for the name is `parked_catalog`). Finished deliverable on Drive: `Trailer Swift FINAL/MP3` = **13 enumerated album tracks** (2025-07-09). WAV sibling folder exists and was **not enumerated**. 2023 Lyrics folder = **13 numbered lyric docs** (Ours is not in that numbered list). Parent folder = **12 backing-track MP3s**. One enumerated Logic project: `Trailer Swift - Ours v1.0.logicx`. | no |
| **Rad Dad** | Current pop-punk cover band. Captured setlist sheet is almost all covers plus three already-on-spine titles (Drinking Song, Everyday, The Way I Love You). About **30** of the 93 book titles appear on that sheet. That sheet is catalog play-history / rehearsal paper, **not** the official set. | no — Show Night owns official sets |
| **Stalemate 2024 sets** | Mixed originals + covers. 4-26-24 names the artist for every song. About **39** book titles on 4-26; **24** on 3-13. Keys on those sheets stay on the sheets. | no |
| **8-bit series** | Six book titles already end in `(8-bit)`. Drive Logic-dump notes mention a covers/8-bit pile (Nirvana, NOFX, Blink, Green Day, Lagwagon, NUFAN, …) that was **not fully enumerated**. Do not invent those extra titles as cover rows. | no |
| **SoundCloud / Christmas / comedy** | Context mentions SoundCloud for every row. No per-cover SoundCloud id is on the book. Christmas-ish book titles (I Won’t Be Home For Christmas, Oi To The World, Grandma, I Celebrate The Day, Christmas Medley, Ice Ice Baby, Somewhere Over The Rainbow) are still covers, still official=0. | no |

Trailer Swift FINAL 13 vs book 14 Taylor Swift titles:

| Book title | FINAL MP3 | 2023 lyric doc | Parent backing MP3 | Drive `.logicx` |
|---|---|---|---|---|
| Sparks Fly | y (1) | y (12) | y | - |
| Ready For It | y (2) | y (9) | - | - |
| Paper Rings | y (3) | y (5) | - | - |
| You Need To Calm Down | y (4) | y (4) | - | - |
| Mean | y (5) | y (7) | y | - (earlier Mean v1.3 mp3+wav in MUSIC/2022 notes) |
| I Knew You Were Trouble | y (6) | y (8, misspelled Your) | y | - |
| Mine | y (7) | y (3) | y | - |
| Cruel Summer | y (8) | y (11) | - | - |
| The Story Of Us | y (9) | y (6) | y | - |
| Stay Stay Stay | y (10) | y (2) | y | - |
| Enchanted | y (11) | y (1) | y | - |
| All Too Well | y (12) | y (13) | - | - |
| You Belong With Me | y (13, file labeled Taylor not Trailer) | y (10) | - | - |
| Ours | **not on FINAL** | **not in numbered lyrics** | y | **y — Ours v1.0.logicx** |

Needs Jeff still has the unanswered “Songs You Made Me Ruin Vol. 1 = this 13-track album?” question. This walk does not answer it and does not invent a release row.

## Closest to a Logic drop-in vs empty

**On the book:** closest = **0**. Empty = **93**.

**Off-book, already inventoried, not written onto the book:**

### `drive_logicx_off_book` (2) — closest leftover, still not a drop-in

`.logicx` exists on Drive. Cover row still has no ID, no key, no WAV/stems field, no version chain.

| Title | Original artist | Vault ID | Key | BPM | Logicx | WAV | Stems | MIDI | Chain | Ready | Official | Played | Off-book evidence | Lane evidence | Setlist-doc key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Grandma Got Run Over By A Reindeer | Elmo & Patsy | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_logicx_off_book | christmas_logicx_drive | - |
| Ours | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_logicx_off_book | trailer_swift_drive | - |

Ours is the only Trailer Swift title with an enumerated Logic project **and** it is the Taylor Swift title **missing** from Trailer Swift FINAL. Grandma is a Christmas cover with a 2022 Logic project (`Grandma Got Runover v1.3.logicx`) and no setlist-doc hit on the captured Rad Dad / Stalemate sheets. Neither is setlist-ready. Neither is official-set. Do not invent keys.

### `drive_audio_off_book` (13) — Trailer Swift FINAL album tracks

Audio exists on Drive (FINAL MP3 ± parent backing ± lyric doc). No `.logicx` enumerated for these 13. No Vault key.

| Title | Original artist | Vault ID | Key | BPM | Logicx | WAV | Stems | MIDI | Chain | Ready | Official | Played | Off-book evidence | Lane evidence | Setlist-doc key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sparks Fly | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive+stalemate_setlist_doc | Bb/Bm (docs disagree) |
| The Story Of Us | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive+rad_dad_setlist_doc+stalemate_setlist_doc | C |
| Stay Stay Stay | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| You Belong With Me | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| Ready For It | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| You Need To Calm Down | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| Enchanted | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| Cruel Summer | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| Mine | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| Paper Rings | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| Mean | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| I Knew You Were Trouble | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |
| All Too Well | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | drive_audio_off_book | trailer_swift_drive | - |

Sparks Fly and The Story Of Us also appear on captured Stalemate / Rad Dad sheets. That is play-history paper, not official-set membership.

### `setlist_mention_only` (58) — captured sheets, empty Vault

Title appears on Rad Dad and/or Stalemate captured setlists. Cover row is still empty for Logic. Setlist-doc keys stay on the docs.

| Title | Original artist | Vault ID | Key | BPM | Logicx | WAV | Stems | MIDI | Chain | Ready | Official | Played | Off-book evidence | Lane evidence | Setlist-doc key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| First Date | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| She | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | G |
| Linoleum | NOFX | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | E |
| Basket Case | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | E |
| American Idiot | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | Ab |
| Holiday | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | F |
| Brain Stew | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | A |
| Jaded | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | A |
| When I Come Around | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | D/G (docs disagree) |
| Hitchin' A Ride | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | B |
| Longview | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| Holden Caulfield | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| Christie Road | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | G |
| Burnout | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | G |
| Nice Guys Finish Last | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| 86 | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| Novacaine | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | A |
| Pulling Teeth | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | B |
| Jesus of Suburbia | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | Misc |
| Knowledge | Operation Ivy/Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | G |
| Rebel Girl | Bikini Kill (listed under Green Day tab) | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | G |
| Dammit | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| All The Small Things | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| The Rock Show | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | A |
| Aliens Exist | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | B |
| Wendy Clear | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| Carousel | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | D |
| M&M's | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| Dick Lips | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | D |
| Dumpweed | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| What's My Age Again? | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | - |
| Chick Magnet | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| Tomorrow's Another Day | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | B |
| Middle Name | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | A (MAIN SET; TAB A/B blank) |
| Responsibility | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| In Bloom | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | B/A# (docs disagree) |
| Breed | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | F#m/Gb (same pitch, docs disagree) |
| On A Plain | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | D |
| Territorial Pissings | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | A |
| Santeria | Sublime | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | E |
| Ruby Soho | Rancid | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | G |
| KKK Took My Baby Away | Ramones | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | G |
| Blitzkrieg Bop | Ramones | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | A |
| Stand By Me | Ben E. King via Pennywise | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | A |
| Blind | Face to Face | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | F |
| Creep | Radiohead | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | G (MAIN SET; TAB A/B blank) |
| My Own Worst Enemy | Lit | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | E |
| The Middle | Jimmy Eat World | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | D |
| 1985 | Bowling For Soup | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | B |
| Come Back To Texas | Bowling For Soup | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | B |
| They Call Me Steve | Teenage Bottlerocket | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | A |
| Somewhere On Fullerton | Allister | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | D |
| All My Fault | Riverfenix | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | stalemate_setlist_doc | D |
| Miles Away | Goldfinger | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | B |
| The Anthem | Good Charlotte | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | - |
| In Too Deep | Sum 41 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | - |
| Fat Lip | Sum 41 | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | - |
| Saw Her Standing There | The Beatles | - | - | - | - | - | - | - | 0 | - | 0 | - | setlist_mention_only | rad_dad_setlist_doc | E |

### `eightbit_title_only` (6)

Book already marks these as 8-bit. Do not borrow a key from the non-8-bit sibling (`On A Plain` ≠ `On A Plain (8-bit)`).

| Title | Original artist | Vault ID | Key | BPM | Logicx | WAV | Stems | MIDI | Chain | Ready | Official | Played | Off-book evidence | Lane evidence | Setlist-doc key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Wasting Time (8-bit) | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | eightbit_title_only | eightbit_title | - |
| Pieces (8-bit) | Sum 41 | - | - | - | - | - | - | - | 0 | - | 0 | - | eightbit_title_only | eightbit_title | - |
| No Cigar (8-bit) | Millencolin | - | - | - | - | - | - | - | 0 | - | 0 | - | eightbit_title_only | eightbit_title | - |
| Gives You Hell (8-bit) | All-American Rejects | - | - | - | - | - | - | - | 0 | - | 0 | - | eightbit_title_only | eightbit_title | - |
| On A Plain (8-bit) | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | eightbit_title_only | eightbit_title | - |
| Olympia WA (8-bit) | Rancid | - | - | - | - | - | - | - | 0 | - | 0 | - | eightbit_title_only | eightbit_title | - |

### `empty_even_off_book` (14)

Context string only. No captured-setlist hit, no Trailer Swift FINAL/parent hit, no enumerated `.logicx`.

| Title | Original artist | Vault ID | Key | BPM | Logicx | WAV | Stems | MIDI | Chain | Ready | Official | Played | Off-book evidence | Lane evidence | Setlist-doc key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Not Now | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Asthenia | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| I Won't Be Home For Christmas | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Sheena Is A Punk Rocker | Ramones | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Easy | Faith No More/Commodores | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Knockin' On Heaven's Door | Bob Dylan | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Where The Sidewalk Ends | ? | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Armatage Shanks | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Oi To The World | The Vandals | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| I Celebrate The Day | Relient K | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Christmas Medley | various | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Ice Ice Baby | Vanilla Ice | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| Somewhere Over The Rainbow | Arlen/Harburg | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |
| The Decline | NOFX | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_even_off_book | context_only | - |

`Where The Sidewalk Ends` keeps original artist `?`. Do not invent an artist.

## Full cover walk (all 93)

Vault columns are blank on every row because they are blank on the book. Official is **fail-closed 0**. Ready / Played / Chain are 0. Book cluster is `empty_logic_ready` for all 93.

| Title | Original artist | Vault ID | Key | BPM | Logicx | WAV | Stems | MIDI | Chain | Ready | Official | Played | Book cluster | Off-book cluster | Lane evidence | Setlist-doc key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| First Date | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| She | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | G |
| Linoleum | NOFX | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | E |
| Basket Case | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | E |
| American Idiot | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | Ab |
| Holiday | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | F |
| Brain Stew | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | A |
| Jaded | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | A |
| When I Come Around | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | D/G (docs disagree) |
| Hitchin' A Ride | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | B |
| Longview | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| Holden Caulfield | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| Christie Road | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | G |
| Burnout | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | G |
| Nice Guys Finish Last | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| 86 | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| Novacaine | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | A |
| Pulling Teeth | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | B |
| Jesus of Suburbia | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | Misc |
| Knowledge | Operation Ivy/Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | G |
| Rebel Girl | Bikini Kill (listed under Green Day tab) | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | G |
| Dammit | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| All The Small Things | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| The Rock Show | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | A |
| Aliens Exist | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | B |
| Wendy Clear | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| Carousel | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | D |
| M&M's | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| Dick Lips | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | D |
| Dumpweed | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| What's My Age Again? | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | - |
| Not Now | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Asthenia | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| I Won't Be Home For Christmas | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Wasting Time (8-bit) | Blink-182 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | eightbit_title_only | eightbit_title | - |
| Chick Magnet | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | C |
| Tomorrow's Another Day | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | B |
| Middle Name | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | A (MAIN SET; TAB A/B blank) |
| Responsibility | MxPx | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| In Bloom | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | B/A# (docs disagree) |
| Breed | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | F#m/Gb (same pitch, docs disagree) |
| On A Plain | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | D |
| Territorial Pissings | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | A |
| Santeria | Sublime | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | E |
| Ruby Soho | Rancid | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | G |
| KKK Took My Baby Away | Ramones | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | G |
| Blitzkrieg Bop | Ramones | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | A |
| Sheena Is A Punk Rocker | Ramones | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Stand By Me | Ben E. King via Pennywise | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | A |
| Blind | Face to Face | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | F |
| Creep | Radiohead | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | G (MAIN SET; TAB A/B blank) |
| My Own Worst Enemy | Lit | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | E |
| The Middle | Jimmy Eat World | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | D |
| 1985 | Bowling For Soup | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc+stalemate_setlist_doc | B |
| Come Back To Texas | Bowling For Soup | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | B |
| They Call Me Steve | Teenage Bottlerocket | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | A |
| Somewhere On Fullerton | Allister | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | D |
| All My Fault | Riverfenix | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | stalemate_setlist_doc | D |
| Miles Away | Goldfinger | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | B |
| The Anthem | Good Charlotte | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | - |
| In Too Deep | Sum 41 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | - |
| Fat Lip | Sum 41 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | - |
| Pieces (8-bit) | Sum 41 | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | eightbit_title_only | eightbit_title | - |
| Easy | Faith No More/Commodores | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Knockin' On Heaven's Door | Bob Dylan | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Where The Sidewalk Ends | ? | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Armatage Shanks | Green Day | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| No Cigar (8-bit) | Millencolin | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | eightbit_title_only | eightbit_title | - |
| Gives You Hell (8-bit) | All-American Rejects | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | eightbit_title_only | eightbit_title | - |
| On A Plain (8-bit) | Nirvana | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | eightbit_title_only | eightbit_title | - |
| Olympia WA (8-bit) | Rancid | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | eightbit_title_only | eightbit_title | - |
| Oi To The World | The Vandals | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Grandma Got Run Over By A Reindeer | Elmo & Patsy | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_logicx_off_book | christmas_logicx_drive | - |
| I Celebrate The Day | Relient K | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Christmas Medley | various | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Ice Ice Baby | Vanilla Ice | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Somewhere Over The Rainbow | Arlen/Harburg | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |
| Saw Her Standing There | The Beatles | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | setlist_mention_only | rad_dad_setlist_doc | E |
| Sparks Fly | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive+stalemate_setlist_doc | Bb/Bm (docs disagree) |
| The Story Of Us | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive+rad_dad_setlist_doc+stalemate_setlist_doc | C |
| Stay Stay Stay | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| You Belong With Me | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Ready For It | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| You Need To Calm Down | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Enchanted | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Cruel Summer | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Mine | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Paper Rings | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Mean | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| I Knew You Were Trouble | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| All Too Well | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_audio_off_book | trailer_swift_drive | - |
| Ours | Taylor Swift | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | drive_logicx_off_book | trailer_swift_drive | - |
| The Decline | NOFX | - | - | - | - | - | - | - | 0 | - | 0 | - | empty_logic_ready | empty_even_off_book | context_only | - |

## Unmatched titles (stay unmatched)

Do not mint IDs. Do not add cover rows.

| Source | Titles | Honesty |
|---|---|---|
| Stalemate song list | Let’s Go To New Mexico · Tooted last Tuesday · Chains of pain (castle) | Same as #23. Possible alias / no entity / Dustin’s UNK-0013. Stay unmatched. |
| Trailer Swift parent backing tracks **not** in the 93-book | Speak Now · Our Song · Never Grow Up · Dear John | Drive audio exists. Not a catalog row. Stay unmatched. |
| Trailer Swift FINAL vs book | Ours is in the book and **not** on the 13-track FINAL | Do not drop Ours. Do not invent a 14th FINAL track. |
| Rad Dad MAIN SET / wishlist extras already on the captured sheet | Song 2 · Ocean Ave · My Friends Over You · Weightless · Check Yes Juliet · Sk8er Boi · Dirty Little Secret · Stacy's Mom · Sugar We're Goin Down · Misery Business · I Write Sins Not Tragedies · I'm Not Okay · Dear Maria Count Me In · Cute Without the 'E' · good 4 u · my ex's best friend · Since U Been Gone · Welcome to the Black Parade · Stay (Taylor Swift) · On the Road Again · Mr Brightside · Weezer blank | Already on Jeff’s sheet. Not in the 93-book. Stay unmatched. Do not mint. |

## Leave the blob alone

- **Do not rewrite `master_catalog.json` or `app_api.json` song rows.** Cover book stays 93 title/artist/context/classification rows.
- **Do not invent a Manic key.** `ST-0004` is still `audio_only` / blank key on the spine.
- **`UnRecorded Songs.md` is still a 4-line stub.** Do not invent the 71-title list.
- **`vm_unmatched.json` is still missing.** Do not invent the unmatched-memo list.
- **Trailer Swift FINAL/WAV children were not enumerated.** Do not invent WAV paths.
- **Spine stage on JS-0128 still says `IN CURRENT LIVE SET`.** Surface already sanitizes. Do not rewrite the spine.
- Derived `master_catalog.csv` already matches the 150-row spine (#22). Do not redo that CSV work.
- #23 originals Logic-ready walk stays the originals leftover. This page does not re-cluster the 126.

## Conclusion

Hypothesis held: leftover value after #23 is **cover-book Logic-ready honesty**, not a new app and not a fail-closed code bug.

**On the book, closest to Logic drop-in: 0. Empty: 93.**
**Off-book, already inventoried: 2 Drive `.logicx` (Ours, Grandma) · 13 Trailer Swift FINAL audio rows · 58 setlist mentions · 6 8-bit titles · 14 empty even off-book.**
**Trailer Swift originals: 0. Official-set originals: 0. Official-set covers: 0. Covers stay 93.**

Context-string “Rad Dad / Stalemate / Trailer Swift / 8-bit / SoundCloud” is not lane membership. Trailer Swift is a parked cover project with a 13-track FINAL album and 0 original rows. Rad Dad’s captured sheet is not the official set.

**Next honest leftover:** Logic-ready **field fill on Jeff’s Mac** for the two already-inventoried cover `.logicx` files (Ours, Grandma) — without inventing keys or minting cover IDs — plus enumerating Trailer Swift FINAL/WAV if those files are real, and recovering the real UnRecorded / unmatched-memo lists from Drive. Do not mint unmatched Trailer Swift / Rad Dad / Stalemate titles. Do not deploy. Do not merge this draft without review.
