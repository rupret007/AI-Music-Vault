# Catalog Discovery — song analysis
*2026-08-28 · Cloud Agent · no audio · song-level leftover after #22 · not a second catalog · not the official set*

Walked every **126 originals** and every **93 covers** on the committed spine (`data/master_catalog.json` v1.6, tip `0cc4a43` / Vault #22). Catalog rows are not the official live set. Show Night / Jeff own official sets.

This page is per-song honesty + Logic-ready clusters. It does not add, drop, or rename songs. It does not rewrite `master_catalog.json` or `app_api.json` song rows. It does not invent the UnRecorded 71-title list or `vm_unmatched.json`. Stalemate unmatched titles stay unmatched.

## What this walk is (and is not)

| Allowed here | Forbidden here |
|---|---|
| Cluster the 126 originals by Logic-ready evidence already on the spine | Invent keys, BPM, `.logicx`, stems, MIDI, or WAV paths |
| Report recorded vs unrecorded **as already flagged** | Mint new IDs for unmatched Stalemate titles |
| Flag `live_presence` vs `setlist_ready` vs official-set | Treat default-live or `IN CURRENT LIVE SET` as the official set |
| Flag Everyday / Drinking Song momentum **score** drift as reported-only | Silently rewrite `momentum.json` scores |
| Walk all 93 covers as a reference book | Rank covers against originals or invent a Trailer Swift original lane |
| Leave `UnRecorded Songs.md` as a 4-line stub | Invent the 71-title list or `vm_unmatched.json` |

Official-set count on this walk: **0 originals**. `scripts/catalog_surface.py` already fail-closes `official_set: false` on every published song. That must stay fail-closed.

No new fail-closed code bug was found after #22. This leftover is the song-level write-up.

## Method

Inputs (read-only): `data/master_catalog.json` (including spine `covers[]`), `data/app_api.json` (scope / setlist-ready / default-live only), `data/version_chains.json`, `data/momentum.json` (reported-only), `data/covers_reference.csv`, `00_control_room/Vault to StoryBoard.md`, Stalemate / Something Dirty / Jeff Story / Rad Dad band docs, `01_source_manifests/gdrive/doc_texts/Stalemate song list.md`, `01_source_manifests/gdrive/doc_texts/UnRecorded Songs.md`.

Primary DAW is **Logic Pro**. Ableton is not the drop-in target.

Logic-ready clustering (do not invent a key):

| Cluster | Rule |
|---|---|
| `closest_logic_dropin` | `.logicx` + WAV/AIFF/stems + parseable key — closest to a Logic drop-in |
| `logic_project_plus_key` | `.logicx` + parseable key; no WAV/stems mention |
| `logic_project_no_key` | `.logicx` present; **no key** (blocked for StoryBoard setlist-ready) |
| `audio_plus_key_no_logic` | audio/chain evidence + parseable key; no `.logicx` on the spine |
| `audio_only` | audio evidence; no parseable key (do not invent one) |
| `key_only` | parseable key; no Logic project and no WAV/AIFF/stems |
| `empty_logic_ready` | none of the above — lyric / unknown / stub |

Substring trap (corrected on this walk): notes that say “first aesthetic evaluation in the **system**” or “possible future **MIDI horns**” are **not** stems or MIDI files. `ST-0004 Manic` is `audio_only`. The only original whose notes name real stems is `ST-0001` (`turn over mix 1.4 … ~40 stems`). Version chains contain **zero** `.mid` / `.midi` files.

Recorded buckets are **heuristics from existing fields**, not a new score: `recorded_high` = `rec_pct ≥ 80`; `unrecorded_flagged` = notes/stage already say unrecorded / UnRecorded stub; `has_audio_evidence` = mix / bounce / wav / studio / released / SoundCloud / mp3 already on the row; else `unknown_rec` / `partial_rec`. Everyday is a released 1999 album song with **null** `rec_pct`, so it sits in `has_audio_evidence` — do not invent a `rec_pct`.

Band lanes are **catalog history**, not official-set membership.

## Headline counts

| Measure | n | Official set? |
|---|---|---|
| Spine entities | 150 | no |
| Originals walked | 126 | **0** |
| Non-original entities (already on spine) | 24 | no |
| Covers walked | 93 | no |
| `setlist_ready` originals (keyed) | 40 | no |
| Vault default-live slice | 20 | **no — catalog slice** |
| Originals with `live_presence` | 19 | no — play history |
| Official-set originals | 0 | must stay 0 |

| Logic cluster | n |
|---|---|
| `closest_logic_dropin` | 9 |
| `logic_project_plus_key` | 5 |
| `logic_project_no_key` | 19 |
| `audio_plus_key_no_logic` | 10 |
| `audio_only` | 31 |
| `key_only` | 16 |
| `empty_logic_ready` | 36 |

| Recorded bucket (heuristic) | n |
|---|---|
| `recorded_high` | 15 |
| `has_audio_evidence` | 46 |
| `unknown_rec` | 54 |
| `unrecorded_flagged` | 11 |

| Catalog lane tag (originals; a song may have more than one) | n | Official set? |
|---|---|---|
| `jeff_story` | 83 | no |
| `stalemate_parked` | 32 | no |
| `something_dirty_history` | 13 | no |
| `rad_dad_play_history` | 2 originals only — ST-0014 Everyday, JS-0001 Drinking Song | **no — play history, not the official set** |
| Trailer Swift originals | 0 | Trailer Swift lives in the 93-cover book |

## Catalog vs official set (must stay fail-closed)

Vault default-live (20) ≠ setlist-ready (40) ≠ originals (126) ≠ official set.

Show Night binds a local official-set dump as **Rad Dad — official set**. This feed does not write that set. Dashboard reuses `data/app_api.json` and does not reprint `IN CURRENT LIVE SET`.

Spine stage still says `IN CURRENT LIVE SET` on **JS-0128** only. Dashboard/surface already sanitizes. **Do not rewrite the spine.** That row is catalog play history, not the official set.

Published Vault default-live slice (catalog, official=0 on every row):

| ID | Title | Lane | Key | Ready | Official | Played |
|---|---|---|---|---|---|---|
| ST-0014 | Everyday | rad_dad_play+stalemate | C | y | 0 | 2026-05 |
| JS-0001 | Drinking Song | rad_dad_play+stalemate+something_dirty | Am | y | 0 | 2026-05 |
| JS-0128 | It's Alright | jeff_story | C# | y | 0 | 2025-10 |
| ST-0032 | Another Bland Love Song | jeff_story | G | y | 0 | - |
| JS-0131 | I Fall Pretty Down / City's Gone (working title) | jeff_story | C | y | 0 | - |
| JS-0004 | Thanksgiving | jeff_story | C | y | 0 | - |
| ST-0022 | Life At The Bottom | jeff_story | G | y | 0 | - |
| JS-0002 | Going To New Mexico | jeff_story | C | y | 0 | - |
| JS-0003 | Less Miserable | jeff_story | C | y | 0 | - |
| ST-0029 | Head in the Sand | jeff_story | B | y | 0 | - |
| JS-0132 | Don't Put Your Life Away (working title) | jeff_story | C | y | 0 | - |
| JS-0133 | A Place Where You Might (working title) | jeff_story | G#m | y | 0 | - |
| JS-0130 | Been Loving You (working title) | jeff_story | A# | y | 0 | - |
| ST-0021 | I'm Sorry I'm Crazy | jeff_story | B | y | 0 | - |
| JS-0134 | Anyone Can See / Here Is The Church (working title) | jeff_story | G | y | 0 | - |
| ST-0031 | Newfound Love | jeff_story | Am | y | 0 | - |
| JS-0137 | Happy (working title) | jeff_story | Dm | y | 0 | - |
| JS-0135 | Chasing Rainbows | jeff_story | A# | y | 0 | - |
| JS-0136 | The Way That You Love Me | jeff_story | D# | y | 0 | - |
| JS-0138 | Find My Island (working title) | jeff_story | C#m | y | 0 | - |

Played (`live_presence`) but **not** setlist-ready — usually missing a parseable key:

| ID | Title | Key | Cluster | Official | Played |
|---|---|---|---|---|---|
| SD-0001 | I Hate This Part | - | empty_logic_ready | 0 | 2023-05 |
| SD-0009 | Dr Pepper | - | empty_logic_ready | 0 | 2023-05 |

`ST-0002 The Way I Love You` is on Rad Dad’s captured setlist as an “original” credit but classification is **Paco outside composition** — not in the 126 originals, not default-live. Do not invent Rad Dad catalog rows.

## Album six honesty

The six-track album picture is unchanged. Two of the six are not Jeff originals.

| ID | Title | In 126? | Logic cluster | Rec | Key | Logicx | Official | Note |
|---|---|---|---|---|---|---|---|---|
| ST-0001 | Turn Over The Flag | yes | closest_logic_dropin | recorded_high | E (live, Eb tuning) | y | 0 | original |
| ST-0002 | The Way I Love You | no | — | — | — | - | 0 | outside — Paco; not in the 126 |
| ST-0003 | TBFH | yes | audio_plus_key_no_logic | recorded_high | A | - | 0 | original |
| ST-0004 | Manic | yes | audio_only | recorded_high | - | - | 0 | original |
| ST-0005 | Better Than Now | no | — | — | — | - | 0 | Sean band original; not in the 126 |
| ST-0006 | Take The Step | yes | closest_logic_dropin | recorded_high | A/A# (varies by chart) | y | 0 | original |

**Manic correction:** readiness 87, one overdub, version chain is **two mp3s**, no `.logicx`, blank key/BPM. Signal-est C#m was weak (`r=0.48`) — do not invent a key. Notes mentioning “system” / future MIDI horns are not stems or MIDI files. Cluster `audio_only` is correct. Logic-drop-in is empty.

## Logic-ready clusters (all 126 originals)

Columns: Logicx / WAV/AIFF / Stems / MIDI / Chain = evidence already on the spine or version chain. Ready = StoryBoard `setlist_ready`. Default-live = published 20-id catalog slice. Official is **fail-closed 0** on every row. Played = `live_latest` (catalog play history).

### `closest_logic_dropin` (9)

`.logicx` + WAV/AIFF/stems + parseable key — closest to a Logic drop-in.

These are the only originals that already show `.logicx` + audio/stems + a parseable key.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0004 | Thanksgiving | jeff_story | has_audio_evidence | C | - | y | y | - | - | 2 | y | y | 0 | - |
| SD-0006 | Going To Cali | something_dirty | has_audio_evidence | B | - | y | y | - | - | 6 | y | - | 0 | 2023-05 |
| SD-0007 | Cigarettes In A | something_dirty | unknown_rec | A | - | y | y | - | - | 3 | y | - | 0 | 2023-05 |
| ST-0001 | Turn Over The Flag | stalemate | recorded_high | E (live, Eb tuning) | - | y | y | y | - | 7 | y | - | 0 | 2024-04 |
| ST-0006 | Take The Step | stalemate | recorded_high | A/A# (varies by chart) | 145 | y | y | - | - | 6 | y | - | 0 | 2024-04 |
| ST-0008 | It's Only Been 18 | stalemate | has_audio_evidence | C doc / G live | 212 | y | y | - | - | 5 | y | - | 0 | 2024-04 |
| ST-0018 | In The End | stalemate | has_audio_evidence | D | - | y | y | - | - | 3 | y | - | 0 | - |
| ST-0022 | Life At The Bottom | jeff_story | has_audio_evidence | G | - | y | y | - | - | 1 | y | y | 0 | - |
| ST-0032 | Another Bland Love Song | jeff_story | has_audio_evidence | G | - | y | y | - | - | 4 | y | y | 0 | - |

### `logic_project_plus_key` (5)

`.logicx` + parseable key; no WAV/stems mention.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0003 | Less Miserable | jeff_story | has_audio_evidence | C | - | y | - | - | - | 3 | y | y | 0 | - |
| ST-0007 | Be With You | stalemate | has_audio_evidence | A live / F on song list | - | y | - | - | - | 2 | y | - | 0 | 2024-04 |
| ST-0015 | Annoying Me | stalemate | has_audio_evidence | C | - | y | - | - | - | 1 | y | - | 0 | - |
| ST-0021 | I'm Sorry I'm Crazy | jeff_story | has_audio_evidence | B | - | y | - | - | - | 1 | y | y | 0 | - |
| ST-0031 | Newfound Love | jeff_story | unknown_rec | Am | - | y | - | - | - | 1 | y | y | 0 | - |

### `logic_project_no_key` (19)

`.logicx` present; **no key** (blocked for StoryBoard setlist-ready).

Do not invent keys. These fail StoryBoard `setlist_ready` until a parseable key is filled on Jeff’s Mac. `ST-0110 Andrea` is recorded-high and still not setlist-ready. Stay off the Andrea_NanoBot app; this is a catalog key gap only.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0005 | The Leaves Are Weak | jeff_story | has_audio_evidence | - | - | y | y | - | - | 3 | - | - | 0 | - |
| JS-0006 | A Better Way | jeff_story | has_audio_evidence | - | - | y | y | - | - | 3 | - | - | 0 | - |
| JS-0009 | Oui C'est Fou | jeff_story | has_audio_evidence | - | - | y | y | - | - | 3 | - | - | 0 | - |
| JS-0012 | Don't Look Bach | jeff_story | has_audio_evidence | - | - | y | y | - | - | 3 | - | - | 0 | - |
| JS-0017 | Starlight | jeff_story | has_audio_evidence | - | - | y | - | - | - | 3 | - | - | 0 | - |
| JS-0022 | You Complete Me | jeff_story | has_audio_evidence | - | - | y | y | - | - | 2 | - | - | 0 | - |
| JS-0047 | A Simpler Life | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0061 | Old You | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0101 | Shine On Through The Darkness | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0102 | Suddenly Stranded | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0103 | Political Circus | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0104 | Run Away | jeff_story | has_audio_evidence | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0105 | Country Fried | jeff_story | unknown_rec | - | - | y | - | - | - | 3 | - | - | 0 | - |
| JS-0106 | Four Walls | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| JS-0109 | Champ Elysisis | jeff_story | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| ST-0023 | Highs and Lows | stalemate | has_audio_evidence | - | - | y | y | - | - | 3 | - | - | 0 | - |
| ST-0027 | Morgan The Wizard | stalemate | unknown_rec | - | - | y | - | - | - | 1 | - | - | 0 | - |
| ST-0028 | The Prime Outline | stalemate | has_audio_evidence | - | - | y | y | - | - | 1 | - | - | 0 | - |
| ST-0110 | Andrea | stalemate | recorded_high | - | - | y | y | - | - | 2 | - | - | 0 | - |

### `audio_plus_key_no_logic` (10)

audio/chain evidence + parseable key; no `.logicx` on the spine.

Keyed and has audio/chain evidence. Closest **non-Logic** drop-ins. They need a `.logicx` on Jeff’s Mac, not an Ableton rewrite. Rad Dad play history on this walk is **only** Everyday and Drinking Song — catalog play history, not the official set.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0001 | Drinking Song | rad_dad_play+stalemate+something_dirty | has_audio_evidence | Am | - | - | - | - | - | 2 | y | y | 0 | 2026-05 |
| JS-0002 | Going To New Mexico | jeff_story | has_audio_evidence | C | - | - | y | - | - | 2 | y | y | 0 | - |
| SD-0004 | Velvet Roses | something_dirty | unknown_rec | G | - | - | - | - | - | 1 | y | - | 0 | 2023-05 |
| ST-0003 | TBFH | stalemate | recorded_high | A | - | - | - | - | - | 3 | y | - | 0 | 2024-04 |
| ST-0009 | Long Long Drive | stalemate | has_audio_evidence | Am | 123 | - | - | - | - | 2 | y | - | 0 | 2024-04 |
| ST-0010 | Wham Bam | stalemate | recorded_high | E | 150 | - | y | - | - | 3 | y | - | 0 | 2024-04 |
| ST-0012 | Don't Call Me A Hero | stalemate | unknown_rec | F# (live) | - | - | - | - | - | 1 | y | - | 0 | - |
| ST-0013 | Graveyard Swiftly | stalemate | unknown_rec | E | - | - | - | - | - | 1 | y | - | 0 | 2024-04 |
| ST-0014 | Everyday | rad_dad_play+stalemate | has_audio_evidence | C | - | - | - | - | - | 1 | y | y | 0 | 2026-05 |
| ST-0019 | Candi Lane | stalemate+something_dirty | has_audio_evidence | A | - | - | - | - | - | 1 | y | - | 0 | 2023-05 |

### `audio_only` (31)

audio evidence; no parseable key (do not invent one).

Includes album quick-win `ST-0004 Manic` and the 1999 *My Mom Says We're Cool* originals `ST-0101`…`ST-0108`.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0007 | 31 Timberview | jeff_story | has_audio_evidence | - | - | - | y | - | - | - | - | - | 0 | - |
| JS-0008 | Better Together | jeff_story | has_audio_evidence | - | - | - | y | - | - | 1 | - | - | 0 | - |
| JS-0011 | August Heated Nights | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0013 | I Fall Down | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0014 | Justify | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0015 | Minor Lessons | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0016 | Prevent The Fall | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0018 | Synonyms For Stubborn | jeff_story | has_audio_evidence | - | - | - | y | - | - | 1 | - | - | 0 | - |
| JS-0019 | Taking Flight | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0020 | The Catalyst | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0021 | Why Do I... | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| JS-0023 | Unjustified | jeff_story | has_audio_evidence | - | - | - | y | - | - | 1 | - | - | 0 | - |
| JS-0108 | Home on the Lake | jeff_story | has_audio_evidence | - | - | - | y | - | - | - | - | - | 0 | - |
| JS-0110 | Dah | jeff_story | has_audio_evidence | - | - | - | y | - | - | - | - | - | 0 | - |
| JS-0122 | Over You | jeff_story | unrecorded_flagged | - | - | - | - | - | - | 1 | - | - | 0 | - |
| SD-0002 | I'm OK | something_dirty | unknown_rec | - | - | - | - | - | - | 1 | - | - | 0 | - |
| SD-0003 | Love In A Pill | something_dirty | unknown_rec | - | - | - | - | - | - | 1 | - | - | 0 | - |
| SD-0005 | Day In The Life | something_dirty | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0004 | Manic | stalemate | recorded_high | - | - | - | - | - | - | 2 | - | - | 0 | - |
| ST-0011 | Planet Of The Flakes | stalemate | recorded_high | - | - | - | y | - | - | 2 | - | - | 0 | - |
| ST-0024 | I Need You | stalemate | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0025 | Dystopian Choice | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0026 | Brave New World | jeff_story | has_audio_evidence | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0101 | Jettison | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0102 | This Can't Be | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0103 | My Mom Says We're Cool | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0104 | I'm A Loser | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0105 | A New Girlfriend | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0106 | Untrue | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0107 | The Sky Is Blue | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |
| ST-0108 | Over 18 | stalemate | recorded_high | - | - | - | - | - | - | 1 | - | - | 0 | - |

### `key_only` (16)

parseable key; no Logic project and no WAV/AIFF/stems.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0128 | It's Alright | jeff_story | unrecorded_flagged | C# | 129 | - | - | - | - | - | y | y | 0 | 2025-10 |
| JS-0130 | Been Loving You (working title) | jeff_story | unknown_rec | A# | 103 | - | - | - | - | - | y | y | 0 | - |
| JS-0131 | I Fall Pretty Down / City's Gone (working title) | jeff_story | unknown_rec | C | 103 | - | - | - | - | - | y | y | 0 | - |
| JS-0132 | Don't Put Your Life Away (working title) | jeff_story | unknown_rec | C | 215 | - | - | - | - | - | y | y | 0 | - |
| JS-0133 | A Place Where You Might (working title) | jeff_story | unknown_rec | G#m | 161 | - | - | - | - | - | y | y | 0 | - |
| JS-0134 | Anyone Can See / Here Is The Church (working title) | jeff_story | unknown_rec | G | 136 | - | - | - | - | - | y | y | 0 | - |
| JS-0135 | Chasing Rainbows | jeff_story | unknown_rec | A# | 112 | - | - | - | - | - | y | y | 0 | - |
| JS-0136 | The Way That You Love Me | jeff_story | unknown_rec | D# | 108 | - | - | - | - | - | y | y | 0 | - |
| JS-0137 | Happy (working title) | jeff_story | unknown_rec | Dm | 185 | - | - | - | - | - | y | y | 0 | - |
| JS-0138 | Find My Island (working title) | jeff_story | unknown_rec | C#m | 92 | - | - | - | - | - | y | y | 0 | - |
| SD-0008 | Bad Idea | something_dirty | unknown_rec | Em | - | - | - | - | - | - | y | - | 0 | 2023-05 |
| SD-0010 | Disconnect | something_dirty | unknown_rec | C | - | - | - | - | - | - | y | - | 0 | 2023-05 |
| ST-0016 | Times Have Changed | stalemate | has_audio_evidence | B (list) / G+A charts | - | - | - | - | - | - | y | - | 0 | - |
| ST-0017 | What To Do | stalemate | has_audio_evidence | Em | - | - | - | - | - | - | y | - | 0 | - |
| ST-0029 | Head in the Sand | jeff_story | unknown_rec | B | - | - | - | - | - | - | y | y | 0 | - |
| ST-0030 | Rabbit Hole | stalemate | unknown_rec | Bb | - | - | - | - | - | - | y | - | 0 | - |

### `empty_logic_ready` (36)

none of the above — lyric / unknown / stub.

Includes UnRecorded-stub titles (Older, Brown Eye Surprise, Beautiful Morning, Kids Can't Fly, Take The Abuse, New Act, Poolside, B4L), JS-0139/0140, Misery, and played-but-unkeyed Something Dirty rows.

| ID | Title | Lane | Rec | Key | BPM | Logicx | WAV/AIFF | Stems | MIDI | Chain | Ready | Default-live | Official | Played |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JS-0010 | 90% / 99 Percent | jeff_story | has_audio_evidence | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0048 | Blindfolds | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0049 | Bottom Of My Heart | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0050 | Drums of War | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0051 | Get Outta The City | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0053 | Heart Racing | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0055 | Independence Day | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0056 | Insane | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0057 | Life In America 2018 | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0058 | Mayhem | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0059 | Misery | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0060 | My Muse Abuse | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0062 | Our Last Night (Moonlight Pride) | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0063 | Over 40 | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0064 | Resist | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0065 | Talk To Me | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0066 | The World's Gonna End | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0067 | Unity | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0068 | Unknown Song | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0070 | Andrea (lyric rev 2023) | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0100 | Airtime | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0111 | Everything's Beautiful | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0112 | Home | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0120 | Older | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0121 | Brown Eye Surprise | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0123 | Beautiful Morning | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0124 | Kids Can't Fly | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0125 | Take The Abuse | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0126 | New Act | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0127 | Poolside | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0129 | B4L | jeff_story | unrecorded_flagged | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0139 | A New Hope (working title) | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| JS-0140 | Anthem Part 2 (working title) | jeff_story | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |
| SD-0001 | I Hate This Part | something_dirty | has_audio_evidence | - | - | - | - | - | - | - | - | - | 0 | 2023-05 |
| SD-0009 | Dr Pepper | something_dirty | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | 2023-05 |
| SD-0011 | Our Life | something_dirty | unknown_rec | - | - | - | - | - | - | - | - | - | 0 | - |

## Recorded-high originals (15)

`rec_pct ≥ 80` only. Released songs with a null `rec_pct` are not in this bucket.

| ID | Title | Lane | rec_pct | Cluster | Official |
|---|---|---|---|---|---|
| ST-0001 | Turn Over The Flag | stalemate | 90 | closest_logic_dropin | 0 |
| ST-0003 | TBFH | stalemate | 85 | audio_plus_key_no_logic | 0 |
| ST-0004 | Manic | stalemate | 85 | audio_only | 0 |
| ST-0006 | Take The Step | stalemate | 80 | closest_logic_dropin | 0 |
| ST-0010 | Wham Bam | stalemate | 100 | audio_plus_key_no_logic | 0 |
| ST-0011 | Planet Of The Flakes | stalemate | 100 | audio_only | 0 |
| ST-0101 | Jettison | stalemate | 100 | audio_only | 0 |
| ST-0102 | This Can't Be | stalemate | 100 | audio_only | 0 |
| ST-0103 | My Mom Says We're Cool | stalemate | 100 | audio_only | 0 |
| ST-0104 | I'm A Loser | stalemate | 100 | audio_only | 0 |
| ST-0105 | A New Girlfriend | stalemate | 100 | audio_only | 0 |
| ST-0106 | Untrue | stalemate | 100 | audio_only | 0 |
| ST-0107 | The Sky Is Blue | stalemate | 100 | audio_only | 0 |
| ST-0108 | Over 18 | stalemate | 100 | audio_only | 0 |
| ST-0110 | Andrea | stalemate | 100 | logic_project_no_key | 0 |

## Unrecorded-flagged originals (11)

Already flagged on the spine. Do not invent a 71-title UnRecorded list from this bucket.

| ID | Title | Cluster | Stage | Official |
|---|---|---|---|---|
| JS-0059 | Misery | empty_logic_ready | lyric only (deep archive) | 0 |
| JS-0120 | Older | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0121 | Brown Eye Surprise | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0122 | Over You | audio_only | listed only (UnRecorded Songs doc) | 0 |
| JS-0123 | Beautiful Morning | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0124 | Kids Can't Fly | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0125 | Take The Abuse | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0126 | New Act | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0127 | Poolside | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |
| JS-0128 | It's Alright | key_only | written + IN CURRENT LIVE SET (Oct 2025 practice) — unrecorded, no lyric doc | 0 |
| JS-0129 | B4L | empty_logic_ready | listed only (UnRecorded Songs doc) | 0 |

## Covers (93) — reference book, not a set

Walked every cover. `covers[]` == `covers_reference.csv` (already fail-closed equal by #22). Never rank covers against originals. Not the official set.

Context string on **all 93** covers mentions Rad Dad + Stalemate + Trailer Swift. That is copy-paste context, not 93 official-set rows and not 93 Trailer Swift originals.

35 artists. Top counts:

| Artist | n |
|---|---|
| Green Day | 18 |
| Blink-182 | 15 |
| Taylor Swift | 14 |
| Nirvana | 5 |
| MxPx | 4 |
| Ramones | 3 |
| Sum 41 | 3 |
| NOFX | 2 |
| Rancid | 2 |
| Bowling For Soup | 2 |
| Operation Ivy/Green Day | 1 |
| Bikini Kill (listed under Green Day tab) | 1 |
| Sublime | 1 |
| Ben E. King via Pennywise | 1 |
| Face to Face | 1 |
| Radiohead | 1 |
| Lit | 1 |
| Jimmy Eat World | 1 |
| Teenage Bottlerocket | 1 |
| Allister | 1 |
| Riverfenix | 1 |
| Goldfinger | 1 |
| Good Charlotte | 1 |
| Faith No More/Commodores | 1 |
| Bob Dylan | 1 |
| ? | 1 |
| Millencolin | 1 |
| All-American Rejects | 1 |
| The Vandals | 1 |
| Elmo & Patsy | 1 |
| Relient K | 1 |
| various | 1 |
| Vanilla Ice | 1 |
| Arlen/Harburg | 1 |
| The Beatles | 1 |

Full cover walk (title · artist only — not a setlist):

| Title | Original artist |
|---|---|
| First Date | Blink-182 |
| She | Green Day |
| Linoleum | NOFX |
| Basket Case | Green Day |
| American Idiot | Green Day |
| Holiday | Green Day |
| Brain Stew | Green Day |
| Jaded | Green Day |
| When I Come Around | Green Day |
| Hitchin' A Ride | Green Day |
| Longview | Green Day |
| Holden Caulfield | Green Day |
| Christie Road | Green Day |
| Burnout | Green Day |
| Nice Guys Finish Last | Green Day |
| 86 | Green Day |
| Novacaine | Green Day |
| Pulling Teeth | Green Day |
| Jesus of Suburbia | Green Day |
| Knowledge | Operation Ivy/Green Day |
| Rebel Girl | Bikini Kill (listed under Green Day tab) |
| Dammit | Blink-182 |
| All The Small Things | Blink-182 |
| The Rock Show | Blink-182 |
| Aliens Exist | Blink-182 |
| Wendy Clear | Blink-182 |
| Carousel | Blink-182 |
| M&M's | Blink-182 |
| Dick Lips | Blink-182 |
| Dumpweed | Blink-182 |
| What's My Age Again? | Blink-182 |
| Not Now | Blink-182 |
| Asthenia | Blink-182 |
| I Won't Be Home For Christmas | Blink-182 |
| Wasting Time (8-bit) | Blink-182 |
| Chick Magnet | MxPx |
| Tomorrow's Another Day | MxPx |
| Middle Name | MxPx |
| Responsibility | MxPx |
| In Bloom | Nirvana |
| Breed | Nirvana |
| On A Plain | Nirvana |
| Territorial Pissings | Nirvana |
| Santeria | Sublime |
| Ruby Soho | Rancid |
| KKK Took My Baby Away | Ramones |
| Blitzkrieg Bop | Ramones |
| Sheena Is A Punk Rocker | Ramones |
| Stand By Me | Ben E. King via Pennywise |
| Blind | Face to Face |
| Creep | Radiohead |
| My Own Worst Enemy | Lit |
| The Middle | Jimmy Eat World |
| 1985 | Bowling For Soup |
| Come Back To Texas | Bowling For Soup |
| They Call Me Steve | Teenage Bottlerocket |
| Somewhere On Fullerton | Allister |
| All My Fault | Riverfenix |
| Miles Away | Goldfinger |
| The Anthem | Good Charlotte |
| In Too Deep | Sum 41 |
| Fat Lip | Sum 41 |
| Pieces (8-bit) | Sum 41 |
| Easy | Faith No More/Commodores |
| Knockin' On Heaven's Door | Bob Dylan |
| Where The Sidewalk Ends | ? |
| Armatage Shanks | Green Day |
| No Cigar (8-bit) | Millencolin |
| Gives You Hell (8-bit) | All-American Rejects |
| On A Plain (8-bit) | Nirvana |
| Olympia WA (8-bit) | Rancid |
| Oi To The World | The Vandals |
| Grandma Got Run Over By A Reindeer | Elmo & Patsy |
| I Celebrate The Day | Relient K |
| Christmas Medley | various |
| Ice Ice Baby | Vanilla Ice |
| Somewhere Over The Rainbow | Arlen/Harburg |
| Saw Her Standing There | The Beatles |
| Sparks Fly | Taylor Swift |
| The Story Of Us | Taylor Swift |
| Stay Stay Stay | Taylor Swift |
| You Belong With Me | Taylor Swift |
| Ready For It | Taylor Swift |
| You Need To Calm Down | Taylor Swift |
| Enchanted | Taylor Swift |
| Cruel Summer | Taylor Swift |
| Mine | Taylor Swift |
| Paper Rings | Taylor Swift |
| Mean | Taylor Swift |
| I Knew You Were Trouble | Taylor Swift |
| All Too Well | Taylor Swift |
| Ours | Taylor Swift |
| The Decline | NOFX |

## Non-original entities already on the spine (24)

Do not mint new IDs. Do not fold these into the 126 originals.

| ID | Title | Bucket | Project |
|---|---|---|---|
| ST-0002 | The Way I Love You | outside_or_band_other | Stalemate |
| ST-0005 | Better Than Now | outside_or_band_other | Stalemate |
| ST-0020 | Mom, You're The Bomb | co-write | Stalemate / Something Dirty |
| JS-0052 | Go My Way | draft_or_fragment | Jeff Story |
| JS-0054 | Hey There | cover_or_adaptation | Jeff Story |
| JS-0069 | Room At The Top | cover_or_adaptation | Jeff Story |
| UNK-0001 | Deadweight | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0002 | She's Not All There | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0003 | Rock Brigade | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0004 | Captain Freedom's Workout | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0005 | Catharsis | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0006 | Fool | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0007 | Guns, Glory and Goners | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0008 | mp3.com | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0009 | Rockin' R | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0010 | Scapegoat | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0011 | Searching | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0012 | The End | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0013 | Castle (Chains of Pain) | uncertain_or_collab | Dustin Duffy (Stalemate Split) |
| UNK-0100 | Dorivalland Song | uncertain_or_collab | collab: dver.artist |
| JS-0107 | Blue Skies Fade | co-write | Jeff Story |
| JS-0113 | Bom Bom | draft_or_fragment | Jeff Story |
| UNK-0200 | Your New Boyfriend | uncertain_or_collab | Travis Story |
| UNK-0201 | TAD project (Wrapped in Linen / Rise of the Unicorn) | uncertain_or_collab | Dustin Duffy (TAD) |

## Stalemate unmatched titles (stay unmatched)

From `01_source_manifests/gdrive/doc_texts/Stalemate song list.md`. Do not invent IDs.

| List title | Honesty |
|---|---|
| Let’s Go To New Mexico | Possible alias of catalogued **Going To New Mexico (JS-0002)**. Do not merge. Do not mint a second ID. |
| Tooted last Tuesday | No entity. Stay unmatched. |
| Chains of pain (castle) | **UNK-0013 Castle (Chains of Pain)** exists as **Dustin’s** song. Do **not** re-id it as a Jeff/Stalemate original. |

## Momentum score drift (reported-only)

No unknown ids / title drift (already fail-closed by #22). Scores may still disagree with Decision 38 live-set floors. Do **not** silently rewrite `momentum.json`.

| ID | Title | momentum.json | Spine | Action |
|---|---|---|---|---|
| ST-0014 | Everyday | 30 | 75 | reported-only |
| JS-0001 | Drinking Song | 13 | 75 | reported-only |

Originals with no `momentum.json` row (7). Do not invent scores:

| ID | Title | Spine momentum |
|---|---|---|
| JS-0008 | Better Together | - |
| JS-0010 | 90% / 99 Percent | - |
| JS-0106 | Four Walls | - |
| JS-0108 | Home on the Lake | - |
| JS-0109 | Champ Elysisis | - |
| JS-0139 | A New Hope (working title) | - |
| JS-0140 | Anthem Part 2 (working title) | - |

## Leave the blob alone

- **`UnRecorded Songs.md` is a 4-line stub.** Spine note says Jeff’s 71-title backlog was captured. Ten previously-unknown titles from that pass are already on the spine (Older, Brown Eye Surprise, Over You, Beautiful Morning, Kids Can't Fly, Take The Abuse, New Act, Poolside, It's Alright, B4L). The remaining title list is not in-repo. Do not invent 71 songs.
- **`vm_unmatched.json` is missing.** `voice_memo_pool.note` still points at `01_source_manifests/voicememo/vm_unmatched.json`. Do not invent the unmatched list.
- **Spine stage on JS-0128 still says `IN CURRENT LIVE SET`.** Surface already sanitizes. Do not rewrite the spine.
- Derived `master_catalog.csv` already matches the 150-row spine (#22). Do not redo that CSV work.

## Conclusion

Hypothesis held: leftover value after #22 is **song-level Logic-ready honesty**, not a new app and not a fail-closed code bug.

**Closest to Logic drop-in:** 9 originals.
**Key is the gate:** 19 have a Logic project and no parseable key.
**Empty for Logic:** 36 originals have no Logic/WAV/key evidence on the spine.

**Next honest leftover:** Logic-ready **field fill on Jeff’s Mac** (keys / WAV / AIFF / stems / `.logicx`) for the 19 `logic_project_no_key` + 36 `empty_logic_ready` rows — without inventing keys — plus recovering the real UnRecorded / unmatched-memo lists from Drive. Do not mint Stalemate unmatched IDs. Do not deploy. Do not merge this draft without review.
