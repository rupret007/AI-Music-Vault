#!/usr/bin/env python3
"""Dashboard transcript totals must stay distinct from its useful search index."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from catalog_surface import (  # noqa: E402
    EMBEDDED_DATA_SHA256,
    EMBEDDED_TX_SHA256,
    LOGIC_READY_CLUSTERS,
    WCAG_AA_NORMAL_TEXT,
    build_memo_search_index,
    catalog_cover_count,
    catalog_recovered_count,
    contrast_ratio,
    dashboard_displays_owner_audio_index,
    dashboard_exposes_logic_ready,
    dashboard_exposes_song_work,
    dashboard_finds_remembered_song_names,
    dashboard_first_paint_ready,
    dashboard_listen_is_not_playback,
    dashboard_opens_owner_audio,
    dashboard_resume_leads_first_paint,
    dashboard_work_next_stays_in_view,
    dashboard_computed_home_layout,
    dashboard_phone_and_a11y_ready,
    dashboard_phone_layout_covers,
    dashboard_rdy_contrast_ready,
    dashboard_write_contrast_ready,
    dashboard_resumes_song_work_privately,
    dashboard_theme_tokens,
    embedded_dashboard_payloads,
    latest_memo_for_song,
    logic_ready_maps,
    logic_ready_next_leaks_private_locators,
    memo_evidence_by_song,
    memo_lyric_norm_by_song,
    next_step_is_incomplete,
    normalize_search_text,
    parse_vault_hash,
    safe_song_next_step,
    song_aliases,
    song_logic_ready_cluster,
    song_logic_ready_evidence_label,
    song_logic_ready_evidence_tags,
    song_logic_ready_next,
    song_search_hit,
    song_work_card,
    song_work_kind,
    sort_memo_evidence_rows,
    strip_private_locators,
    work_card_leaks_private_locators,
)


class DashboardMemoHonestyTests(unittest.TestCase):
    def test_memo_index_sanitizes_intake_name_to_basename(self):
        prepared, counts = build_memo_search_index(
            [
                {
                    "uid": "a",
                    "file": "file:///Users/jeff/Voice Memos/Raw Take 1.m4a?download=1",
                    "title": "A",
                    "date": "2026-09-01",
                    "dur": 12,
                    "text": "this transcript text is definitely long enough",
                },
                {
                    "uid": "b",
                    "file": r"C:\\Users\\jeff\\Voice Memos\\Second Take.m4a",
                    "title": "B",
                    "date": "2026-09-02",
                    "dur": 20,
                    "text": "another transcript that is long enough to keep",
                },
            ],
            {"JS-0001": ["a"], "JS-0002": ["b"]},
        )
        self.assertEqual(counts["searchable"], 2)
        self.assertEqual(prepared[0]["f"], "Raw Take 1.m4a")
        self.assertEqual(prepared[1]["f"], "Second Take.m4a")

    def test_memo_index_hides_owner_audio_suffixes_in_intake_name(self):
        prepared, counts = build_memo_search_index(
            [
                {
                    "uid": "leak",
                    "file": "file:///Users/jeff/Voice Memos/private mix.wav",
                    "title": "Hidden",
                    "date": "2026-09-03",
                    "dur": 21,
                    "text": "searchable transcript text stays long enough for indexing",
                }
            ],
            {"JS-0001": ["leak"]},
        )
        self.assertEqual(counts["searchable"], 1)
        self.assertEqual(prepared[0]["f"], "")

    def test_short_matched_transcript_stays_in_source_truth_not_search_index(self):
        transcripts = [
            {
                "uid": "short",
                "file": "short.m4a",
                "title": "Short",
                "date": "2026-08-31",
                "dur": 1,
                "text": "hey",
            },
            {
                "uid": "long",
                "file": "long.m4a",
                "title": "Long",
                "date": "2026-08-31",
                "dur": 30,
                "text": "a useful transcript with enough words to search",
            },
            {
                "uid": "unmatched",
                "file": "unmatched.m4a",
                "title": "Unmatched",
                "date": "2026-08-31",
                "dur": 30,
                "text": "another useful transcript with enough words to search",
            },
        ]
        prepared, counts = build_memo_search_index(
            transcripts,
            {"JS-0001": ["short"], "JS-0002": ["long"]},
        )

        self.assertEqual(
            counts,
            {
                "transcribed": 3,
                "matched": 2,
                "searchable": 2,
                "searchable_matched": 1,
            },
        )
        self.assertEqual([row["s"] for row in prepared], ["JS-0002", ""])
        self.assertNotIn("song_id", transcripts[0])

    def test_committed_dashboard_uses_source_and_searchable_counts(self):
        with open(os.path.join(ROOT, "data", "vm_transcribed.json"), encoding="utf-8") as handle:
            transcripts = json.load(handle)
        with open(
            os.path.join(ROOT, "01_source_manifests", "voicememo", "vm_matches.json"),
            encoding="utf-8",
        ) as handle:
            matches = json.load(handle)
        _prepared, counts = build_memo_search_index(transcripts, matches)
        self.assertEqual(
            counts,
            {
                "transcribed": 916,
                "matched": 372,
                "searchable": 807,
                "searchable_matched": 355,
            },
        )

        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        for name, key in (
            ("TX_TOTAL", "transcribed"),
            ("TX_MATCHED_TOTAL", "matched"),
            ("TX_SEARCHABLE_TOTAL", "searchable"),
            ("TX_SEARCHABLE_MATCHED", "searchable_matched"),
        ):
            self.assertIn(f"const {name} = {counts[key]};", dashboard)
        self.assertIn("search 807 usable-text transcripts", dashboard)
        self.assertIn("916 transcribed and 372 matched", dashboard)
        self.assertIn("355 matched rows have enough text", dashboard)
        self.assertNotIn("all 916 memos searchable", dashboard)
        self.assertNotIn("search all 916 memo transcripts", dashboard)

    def test_memo_evidence_uses_searchable_matches_only(self):
        rows = [
            {"s": "JS-0001", "d": "2024-01-02", "f": "b.m4a"},
            {"s": "JS-0001", "d": "2022-03-01", "f": "a.m4a"},
            {"s": "", "d": "2025-01-01", "f": "unmatched.m4a"},
            {"s": "JS-0002", "d": "", "f": "empty.m4a"},
        ]
        evidence = memo_evidence_by_song(rows)
        self.assertEqual(
            evidence,
            {
                "JS-0001": {"n": 2, "first": "2022-03-01", "last": "2024-01-02"},
                "JS-0002": {"n": 1, "first": "", "last": ""},
            },
        )

    def test_memo_evidence_sorts_newest_first_and_sinks_empty_dates(self):
        ordered = sort_memo_evidence_rows(
            [
                {"d": "2020-01-01", "f": "old.m4a"},
                {"d": "2024-12-01", "f": "new.m4a"},
                {"d": "", "f": "z-empty.m4a"},
                {"d": "2024-12-01", "f": "newer-name.m4a"},
            ]
        )
        self.assertEqual(
            [row["f"] for row in ordered],
            ["newer-name.m4a", "new.m4a", "old.m4a", "z-empty.m4a"],
        )

    def test_vault_hash_only_accepts_known_catalog_ids(self):
        names = {"JS-0001": "First Song"}
        self.assertEqual(
            parse_vault_hash("#memos=JS-0001", names),
            {"kind": "memos", "id": "JS-0001"},
        )
        self.assertEqual(
            parse_vault_hash("song=JS-0001", names),
            {"kind": "song", "id": "JS-0001"},
        )
        self.assertIsNone(parse_vault_hash("#memos=JS-0002", names))
        self.assertIsNone(parse_vault_hash("#open=JS-0001", names))
        self.assertIsNone(parse_vault_hash("#memos=JS-0001<script>", names))
        self.assertEqual(
            parse_vault_hash("#work=write", names),
            {"kind": "work", "id": "write"},
        )
        self.assertEqual(
            parse_vault_hash("#work=listen", names),
            {"kind": "work", "id": "listen"},
        )
        self.assertIsNone(parse_vault_hash("#work=unknown", names))
        self.assertIsNone(parse_vault_hash("#work=JS-0001", names))

    def test_dashboard_must_not_open_owner_audio(self):
        self.assertTrue(dashboard_opens_owner_audio('<a href="mix.wav">open</a>'))
        self.assertTrue(dashboard_opens_owner_audio('<a href="take.mid">open</a>'))
        self.assertTrue(dashboard_opens_owner_audio("<audio src='x.m4a'></audio>"))
        self.assertTrue(dashboard_opens_owner_audio('<a href="file:///tmp/x.wav">x</a>'))
        self.assertTrue(dashboard_opens_owner_audio('<button onclick="play()">x</button>'))
        self.assertFalse(
            dashboard_opens_owner_audio(
                "const DATA = [];\nconst TX = [];\n<button>Copy intake name</button>"
            )
        )
        self.assertFalse(
            dashboard_opens_owner_audio(
                "const DATA = [];\n"
                'const TX = [{"f": "clip.wav", "x": "said file:// once"}];\n'
                "<div>index only</div>\n"
            )
        )

    def test_committed_dashboard_deepens_find_and_act_without_opening_audio(self):
        with open(
            os.path.join(ROOT, "data", "vm_transcribed.json"), encoding="utf-8"
        ) as handle:
            transcripts = json.load(handle)
        with open(
            os.path.join(
                ROOT, "01_source_manifests", "voicememo", "vm_matches.json"
            ),
            encoding="utf-8",
        ) as handle:
            matches = json.load(handle)
        prepared, counts = build_memo_search_index(transcripts, matches)
        evidence = memo_evidence_by_song(prepared)
        self.assertEqual(counts["searchable_matched"], 355)
        self.assertEqual(sum(item["n"] for item in evidence.values()), 355)
        self.assertGreater(len(evidence), 0)

        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertIn('id="evidence"', dashboard)
        self.assertIn("Has searchable memos", dashboard)
        self.assertIn("Sort: Latest memo evidence", dashboard)
        self.assertIn("data-copy-file", dashboard)
        self.assertIn("Copy intake name", dashboard)
        self.assertIn("newest first", dashboard)
        self.assertIn("this page does not open audio", dashboard)
        self.assertIn("function parseVaultHash(", dashboard)
        self.assertIn("function sortMemoHits(", dashboard)
        self.assertIn("function handleVaultKey(", dashboard)
        self.assertFalse(dashboard_opens_owner_audio(dashboard))
        self.assertTrue(dashboard_exposes_song_work(dashboard))
        self.assertTrue(dashboard_resumes_song_work_privately(dashboard))
        self.assertTrue(dashboard_finds_remembered_song_names(dashboard))
        self.assertTrue(dashboard_exposes_logic_ready(dashboard))
        self.assertTrue(dashboard_phone_and_a11y_ready(dashboard))
        self.assertTrue(dashboard_first_paint_ready(dashboard))
        self.assertTrue(dashboard_resume_leads_first_paint(dashboard))
        self.assertTrue(dashboard_work_next_stays_in_view(dashboard))
        self.assertTrue(dashboard_listen_is_not_playback(dashboard))
        self.assertFalse(dashboard_displays_owner_audio_index(dashboard))
        self.assertIn('id="work"', dashboard)
        self.assertIn('id="workSession"', dashboard)
        self.assertIn('id="workStarts"', dashboard)
        self.assertIn('id="advancedFilters"', dashboard)
        self.assertIn("Start a work session", dashboard)
        self.assertIn("More filters", dashboard)
        self.assertIn("Sit-down", dashboard)
        self.assertIn("Logic (export honesty, WAVs/AIFF/MIDI preference, no Ableton-first)", dashboard)
        self.assertIn("open in Logic (export honesty:", dashboard)
        self.assertIn("Logic projects, keys, and WAV/AIFF/MIDI exports stay on your Mac", dashboard)
        self.assertIn("Copy work card", dashboard)
        self.assertIn("function songWorkKind(", dashboard)
        self.assertIn("function buildSongWorkCard(", dashboard)
        self.assertIn("function openWork(", dashboard)
        self.assertIn("function updateWorkSessionState(", dashboard)
        self.assertIn("function safeWorkNextStep(", dashboard)
        self.assertIn("function copyCurrentWorkNext(", dashboard)
        self.assertIn("function reviewCurrentWorkEvidence(", dashboard)
        self.assertIn("function allowedExactWorkSongId(", dashboard)
        self.assertIn("function copyExactSongNextStep(", dashboard)
        self.assertIn("function copyResumeWorkNext(", dashboard)
        self.assertIn("function intakeNameSummary(", dashboard)
        self.assertIn("safeWorkNextStep(d)", dashboard)
        self.assertIn('id="workSessionNext"', dashboard)
        self.assertIn('id="copyWorkNext"', dashboard)
        self.assertIn('id="openWorkEvidence"', dashboard)
        self.assertIn('id="resumeWorkNext"', dashboard)
        self.assertIn('id="copyResumeNext"', dashboard)
        self.assertIn("function latestMemoForSong(", dashboard)
        self.assertIn("Sit-down handoff stays in Session Log: copy next step + intake name before leaving.", dashboard)
        self.assertIn(
            "Work in Logic (export honesty, WAVs/AIFF/MIDI preference, no Ableton-first). "
            "Sit-down handoff stays in Session Log: copy next step + intake name before leaving.",
            dashboard,
        )
        self.assertIn("then log the sit-down handoff in Session Log.", dashboard)
        self.assertIn(
            "No searchable memo evidence for this song. The next step comes from the catalog. "
            "Work in Logic (export honesty, WAVs/AIFF/MIDI preference, no Ableton-first). "
            "This page does not open audio.",
            dashboard,
        )
        self.assertIn("Sit-down handoff: pair intake name + Copy next step in Session Log.", dashboard)
        self.assertIn(
            "Transcripts are machine-made (Whisper, run locally on your Mac) — "
            "they mishear sung words constantly, so treat hits as leads, not gospel. "
            "Copy the intake name only (sanitized); write, produce, or listen in Logic "
            "(export honesty, WAVs/AIFF/MIDI preference, no Ableton-first).",
            dashboard,
        )
        self.assertIn("Copy the intake name only (sanitized)", dashboard)
        self.assertIn("No copy-safe intake name on this memo row yet;", dashboard)
        self.assertIn("no copy-safe intake name yet", dashboard)
        self.assertNotIn("Latest source (auto-resolved)", dashboard)
        self.assertNotIn("<h4>Known assets</h4>", dashboard)


class DashboardSongWorkTests(unittest.TestCase):
    def test_work_kind_reads_existing_next_action_text(self):
        self.assertEqual(
            song_work_kind(
                "Jeff: confirm the 2 unclear chorus lines by ear (60s), "
                "then this is a finished lyric."
            ),
            "write",
        )
        self.assertEqual(
            song_work_kind(
                "Record lead guitar over choruses + solos "
                "(the one finishing overdub)."
            ),
            "produce",
        )
        self.assertEqual(
            song_work_kind(
                "Listen to latest (Jeff Story - Morgan the Wizard v1.0.logicx) "
                "and rate: finish / rest."
            ),
            "listen",
        )
        self.assertEqual(
            song_work_kind(
                "Archive-with-honor: finished, released, still playable live; "
                "not a development priority"
            ),
            "rest",
        )
        self.assertEqual(
            song_work_kind("No dated source resolved — flag for next inventory pass."),
            "inventory",
        )
        self.assertEqual(
            song_work_kind(
                "Candidate for next-EP shortlist; v1.5 mix may be nearly done "
                "— needs a listening pass"
            ),
            "decide",
        )
        self.assertEqual(song_work_kind(""), "unknown")
        self.assertEqual(song_work_kind("   "), "unknown")

    def test_write_beats_later_produce_clause(self):
        self.assertEqual(
            song_work_kind(
                'Locate/transcribe lyrics (no doc exists!); then guitar solos '
                '+ "Jeff take me away" chorus vox per Overdubs doc'
            ),
            "write",
        )

    def test_live_originals_classify_without_unknown(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        kinds = {}
        for song in catalog["songs"]:
            if song.get("classification") != "original":
                continue
            kind = song_work_kind(song.get("next_action"))
            kinds[kind] = kinds.get(kind, 0) + 1
        self.assertEqual(
            kinds,
            {
                "listen": 56,
                "write": 29,
                "inventory": 23,
                "rest": 11,
                "produce": 5,
                "decide": 2,
            },
        )
        self.assertNotIn("unknown", kinds)

    def test_work_card_strips_owner_audio_and_street_fragments(self):
        self.assertEqual(
            strip_private_locators(
                "Listen to latest (Jeff Story - Morgan the Wizard v1.0.logicx) "
                "and rate: finish / rest."
            ),
            "Listen to latest and rate: finish / rest.",
        )
        self.assertEqual(
            strip_private_locators(
                'LISTEN: play Maxwell Dr 99 (latest take). Verdict: gem / meh.'
            ),
            "LISTEN: play. Verdict: gem / meh.",
        )
        self.assertEqual(
            strip_private_locators("Listen to latest (arrangement.mid) and decide."),
            "Listen to latest and decide.",
        )
        card = song_work_card(
            {
                "id": "JS-0130",
                "t": "Been Loving You",
                "nx": "LISTEN: play Maxwell Dr 99 (latest take). arrangement.midi Verdict: gem.",
                "hk": "Been loving you",
                "src": ["mix.wav", "song.logicx"],
                "bs": "file:///Users/jeff/Music/take.wav",
            }
        )
        self.assertIn("Work: listen", card)
        self.assertIn("Hook: Been loving you", card)
        self.assertNotIn("Maxwell", card)
        self.assertNotIn(".wav", card)
        self.assertNotIn(".logicx", card)
        self.assertNotIn(".midi", card)
        self.assertNotIn("file://", card)
        self.assertFalse(work_card_leaks_private_locators(card))

    def test_session_next_step_is_actionable_and_fails_closed(self):
        self.assertEqual(
            safe_song_next_step(
                {
                    "next_action": "Listen to latest (private-mix.wav) and rate: finish / rest."
                }
            ),
            "Listen to latest and rate: finish / rest.",
        )
        self.assertEqual(
            safe_song_next_step({"next_action": "Listen to latest (private-arrangement.mid) and rate: finish / rest."}),
            "Listen to latest and rate: finish / rest.",
        )
        self.assertEqual(safe_song_next_step({"nx": ""}), "")
        self.assertEqual(safe_song_next_step(None), "")
        self.assertEqual(
            safe_song_next_step(
                {"nx": "Open mix.wav", "next_action": "file:///tmp/mix.wav"}
            ),
            "",
        )
        self.assertTrue(next_step_is_incomplete("LISTEN:."))
        self.assertEqual(
            safe_song_next_step({"nx": "LISTEN: Crescent Dr 21."}),
            "",
        )
        leftover = song_work_card(
            {
                "id": "JS-0133",
                "t": "Leftover Listen",
                "nx": "LISTEN: Maxwell Dr 104 (later take).",
            }
        )
        self.assertIn("Work: listen", leftover)
        self.assertNotIn("Next:", leftover)
        self.assertNotIn("Maxwell", leftover)
        self.assertNotIn("LISTEN:.", leftover)

    def test_latest_memo_is_newest_searchable_row(self):
        latest = latest_memo_for_song(
            "JS-0001",
            [
                {"s": "JS-0001", "d": "2020-01-01", "f": "old.m4a"},
                {"s": "JS-0001", "d": "2024-12-01", "f": "new.m4a"},
                {"s": "JS-0002", "d": "2025-01-01", "f": "other.m4a"},
            ],
        )
        self.assertEqual(latest["f"], "new.m4a")
        self.assertIsNone(latest_memo_for_song("JS-9999", [{"s": "JS-0001", "f": "x.m4a"}]))

    def test_work_card_can_include_memo_count_without_intake_name(self):
        card = song_work_card(
            {
                "id": "JS-0128",
                "t": "It's Alright",
                "nx": "Jeff: confirm the 2 unclear chorus lines by ear (60s)",
                "hk": "I know it's alright",
            },
            {"n": 5, "last": "2025-10-14", "f": "1922 Maxwell Dr.m4a"},
        )
        self.assertIn("Work: write", card)
        self.assertIn("Memos: 5 searchable · latest 2025-10-14", card)
        self.assertNotIn("Maxwell", card)
        self.assertNotIn(".m4a", card)

    def test_work_card_omits_sources_and_fails_closed_on_leftover_locator(self):
        safe = song_work_card(
            {
                "canonical_title": "It's Alright",
                "song_id": "JS-0128",
                "next_action": "Jeff: confirm the 2 unclear chorus lines by ear (60s)",
                "hook": "I know it's alright",
                "open_questions": ["noisy and Something Dirty?"],
            }
        )
        self.assertIn("It's Alright (JS-0128)", safe)
        self.assertIn("Work: write", safe)
        self.assertNotIn("Also known as:", safe)
        self.assertIn("Open questions: noisy and Something Dirty?", safe)
        aka_card = song_work_card(
            {
                "canonical_title": "Candi Lane",
                "song_id": "ST-0019",
                "alt_titles": ["Candy Lane (2017)", "Candi Lane"],
                "next_action": "Listen to latest and rate: finish / rest.",
            }
        )
        self.assertIn("Also known as: Candy Lane (2017)", aka_card)
        self.assertNotIn("Also known as: Candi Lane", aka_card)
        self.assertNotIn("sources", safe.lower())
        leaked = song_work_card(
            {
                "t": "Leak",
                "id": "JS-9999",
                "nx": "do the thing",
                "key": "open mix.wav",
            }
        )
        self.assertEqual(leaked, "")

    def test_live_work_cards_do_not_leak_private_locators(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        cards = 0
        for song in catalog["songs"]:
            card = song_work_card(song)
            if not card:
                continue
            cards += 1
            self.assertFalse(
                work_card_leaks_private_locators(card),
                song.get("song_id"),
            )
            self.assertNotIn("file://", card)
        self.assertGreater(cards, 100)

    def test_embedded_data_and_tx_hashes_stay_on_main(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        payloads = embedded_dashboard_payloads(dashboard)
        self.assertEqual(
            hashlib.sha256(payloads["DATA"].encode()).hexdigest(),
            EMBEDDED_DATA_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(payloads["TX"].encode()).hexdigest(),
            EMBEDDED_TX_SHA256,
        )


class DashboardSongFindTests(unittest.TestCase):
    def test_normalize_search_folds_apostrophes_and_punctuation(self):
        self.assertEqual(
            normalize_search_text("Don't Put Your Life Away"),
            normalize_search_text("dont put your life away"),
        )
        self.assertEqual(normalize_search_text("Manic?  No way!"), "manic no way")
        self.assertEqual(normalize_search_text("  Candy   Lane  "), "candy lane")

    def test_song_aliases_use_existing_titles_only(self):
        self.assertEqual(
            song_aliases(
                {
                    "canonical_title": "Candi Lane",
                    "alt_titles": ["Candy Lane (2017)", "Candi Lane", "", "Candy Lane (2017)"],
                }
            ),
            ["Candy Lane (2017)"],
        )
        self.assertEqual(song_aliases({"t": "Manic", "aka": ["Manic!", "Manic?  No way!"]}), ["Manic?  No way!"])
        self.assertEqual(song_aliases({"canonical_title": "Resist"}), [])
        self.assertEqual(song_aliases(None), [])

    def test_name_and_alias_queries_outrank_field_and_memo_hits(self):
        candi = {
            "song_id": "ST-0019",
            "canonical_title": "Candi Lane",
            "alt_titles": ["Candy Lane (2017)"],
            "theme": "garden anniversary",
        }
        garden = {
            "song_id": "JS-9998",
            "canonical_title": "Other Song",
            "theme": "candy lane is in the notes",
        }
        memo_only = {
            "song_id": "JS-9999",
            "canonical_title": "Unrelated",
        }
        memos = {
            "JS-9999": normalize_search_text("we drove down candy lane tonight"),
        }
        self.assertEqual(song_search_hit(candi, "candy lane")["via"], "name")
        self.assertEqual(song_search_hit(candi, "candy lane")["rank"], 0)
        self.assertEqual(song_search_hit(garden, "candy lane")["via"], "field")
        self.assertEqual(song_search_hit(garden, "candy lane")["rank"], 3)
        self.assertEqual(
            song_search_hit(memo_only, "candy lane", memos)["via"],
            "memo",
        )
        self.assertEqual(song_search_hit(memo_only, "candy lane", memos)["rank"], 4)
        self.assertFalse(song_search_hit(memo_only, "ca", memos)["hit"])
        self.assertFalse(song_search_hit(memo_only, "missing", memos)["hit"])

    def test_short_memo_query_does_not_scan_titles_or_filenames(self):
        memos = memo_lyric_norm_by_song(
            [
                {
                    "s": "JS-0001",
                    "n": "1922 Maxwell Dr 99",
                    "f": "maxwell.m4a",
                    "x": "hey there darling don't put your life away",
                }
            ]
        )
        self.assertIn("dont put your life", memos["JS-0001"])
        self.assertNotIn("maxwell", memos["JS-0001"])
        hit = song_search_hit(
            {"id": "JS-0001", "t": "Don't Put Your Life Away (working title)"},
            "dont put your life",
            memos,
        )
        self.assertEqual(hit["via"], "name")

    def test_live_catalog_aliases_surface_the_remembered_song_first(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        cases = {
            "candy lane": "ST-0019",
            "manic no way": "ST-0004",
            "graveyard scwifty": "ST-0013",
            "new found love": "ST-0031",
            "resist lyrics": "JS-0064",
            "only 18": "ST-0008",
            "chicken fried": "JS-0105",
            "dont put your life": "JS-0132",
            "to be fucking honest": "ST-0003",
        }
        for term, song_id in cases.items():
            ranked = []
            for song in catalog["songs"]:
                hit = song_search_hit(song, term)
                if hit["hit"]:
                    ranked.append((hit["rank"], song["song_id"], song))
            ranked.sort(key=lambda item: (item[0], item[1]))
            self.assertTrue(ranked, term)
            self.assertEqual(ranked[0][1], song_id, term)

    def test_committed_dashboard_projects_existing_aliases_only(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        expected = {
            song["song_id"]: song_aliases(song)
            for song in catalog["songs"]
            if song_aliases(song)
        }
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        payloads = embedded_dashboard_payloads(dashboard)
        rows = json.loads(payloads["DATA"])
        projected = {row["id"]: row.get("aka") for row in rows if row.get("aka")}
        self.assertEqual(projected, expected)
        self.assertIn("Candy Lane (2017)", projected["ST-0019"])
        self.assertNotIn("Speak Now", json.dumps(projected))


WALK_ORIGINAL_LOGIC_READY = {
    "closest_logic_dropin": [
        "JS-0004", "SD-0006", "SD-0007", "ST-0001", "ST-0006",
        "ST-0008", "ST-0018", "ST-0022", "ST-0032",
    ],
    "logic_project_plus_key": [
        "JS-0003", "ST-0007", "ST-0015", "ST-0021", "ST-0031",
    ],
    "logic_project_no_key": [
        "JS-0005", "JS-0006", "JS-0009", "JS-0012", "JS-0017", "JS-0022",
        "JS-0047", "JS-0061", "JS-0101", "JS-0102", "JS-0103", "JS-0104",
        "JS-0105", "JS-0106", "JS-0109", "ST-0023", "ST-0027", "ST-0028",
        "ST-0110",
    ],
    "audio_plus_key_no_logic": [
        "JS-0001", "JS-0002", "SD-0004", "ST-0003", "ST-0009", "ST-0010",
        "ST-0012", "ST-0013", "ST-0014", "ST-0019",
    ],
    "audio_only": [
        "JS-0007", "JS-0008", "JS-0011", "JS-0013", "JS-0014", "JS-0015",
        "JS-0016", "JS-0018", "JS-0019", "JS-0020", "JS-0021", "JS-0023",
        "JS-0108", "JS-0110", "JS-0122", "SD-0002", "SD-0003", "SD-0005",
        "ST-0004", "ST-0011", "ST-0024", "ST-0025", "ST-0026", "ST-0101",
        "ST-0102", "ST-0103", "ST-0104", "ST-0105", "ST-0106", "ST-0107",
        "ST-0108",
    ],
    "key_only": [
        "JS-0128", "JS-0130", "JS-0131", "JS-0132", "JS-0133", "JS-0134",
        "JS-0135", "JS-0136", "JS-0137", "JS-0138", "SD-0008", "SD-0010",
        "ST-0016", "ST-0017", "ST-0029", "ST-0030",
    ],
    "empty_logic_ready": [
        "JS-0010", "JS-0048", "JS-0049", "JS-0050", "JS-0051", "JS-0053",
        "JS-0055", "JS-0056", "JS-0057", "JS-0058", "JS-0059", "JS-0060",
        "JS-0062", "JS-0063", "JS-0064", "JS-0065", "JS-0066", "JS-0067",
        "JS-0068", "JS-0070", "JS-0100", "JS-0111", "JS-0112", "JS-0120",
        "JS-0121", "JS-0123", "JS-0124", "JS-0125", "JS-0126", "JS-0127",
        "JS-0129", "JS-0139", "JS-0140", "SD-0001", "SD-0009", "SD-0011",
    ],
}


class DashboardLogicReadyTests(unittest.TestCase):
    def test_canned_logic_ready_next_never_leaks_locators(self):
        self.assertFalse(logic_ready_next_leaks_private_locators())
        for cluster in LOGIC_READY_CLUSTERS:
            nxt = song_logic_ready_next(cluster)
            self.assertTrue(nxt, cluster)
            self.assertFalse(work_card_leaks_private_locators(nxt), nxt)
            self.assertNotIn(".logicx", nxt.lower())
            self.assertNotIn(".wav", nxt.lower())
            self.assertNotIn("exported", nxt.lower())
            self.assertNotIn("upload", nxt.lower())

    def test_evidence_tags_read_logic_native_asset_types_only(self):
        self.assertEqual(
            song_logic_ready_evidence_tags(
                {"key": "Am", "sources": ["song v1.0.logicx", "mix.wav"]}
            ),
            ["Logic Pro project", "WAV/AIFF", "Key on file"],
        )
        self.assertEqual(
            song_logic_ready_evidence_tags(
                {"sources": ["stems bounce"]}
            ),
            ["Stems"],
        )
        self.assertEqual(
            song_logic_ready_evidence_tags(
                {"key": "Am"}, {"files": [{"title": "take 1", "kind": "studio-take"}]}
            ),
            ["Recorded take", "Key on file"],
        )
        self.assertEqual(song_logic_ready_evidence_tags({}), [])
        self.assertEqual(song_logic_ready_evidence_tags(None), [])
        self.assertEqual(
            song_logic_ready_evidence_label({"key": "Am"}),
            "Key on file",
        )
        self.assertEqual(song_logic_ready_evidence_label({}), "")

    def test_evidence_tags_never_carry_a_filename_or_path(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        with open(
            os.path.join(ROOT, "data", "version_chains.json"), encoding="utf-8"
        ) as handle:
            chains = json.load(handle)
        seen_any = False
        for song in catalog["songs"]:
            tags = song_logic_ready_evidence_tags(
                song, chains.get(song["song_id"])
            )
            if tags:
                seen_any = True
            label = " · ".join(tags)
            self.assertFalse(work_card_leaks_private_locators(label), label)
            self.assertNotIn(".", label, label)
        self.assertTrue(seen_any)

    def test_evidence_tags_agree_with_the_cluster_they_explain(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        with open(
            os.path.join(ROOT, "data", "version_chains.json"), encoding="utf-8"
        ) as handle:
            chains = json.load(handle)
        for song in catalog["songs"]:
            chain = chains.get(song["song_id"])
            cluster = song_logic_ready_cluster(song, chain)
            tags = song_logic_ready_evidence_tags(song, chain)
            if cluster == "closest_logic_dropin":
                self.assertIn("Logic Pro project", tags, song["song_id"])
                self.assertTrue(
                    "WAV/AIFF" in tags or "Stems" in tags, song["song_id"]
                )
                self.assertIn("Key on file", tags, song["song_id"])
            if cluster == "empty_logic_ready":
                self.assertEqual(tags, [], song["song_id"])
            if cluster == "key_only":
                self.assertEqual(tags, ["Key on file"], song["song_id"])

    def test_work_card_carries_asset_tags_from_precomputed_lrf(self):
        card = song_work_card(
            {
                "id": "ST-0001",
                "t": "Turn Over The Flag",
                "nx": "Track overdubs",
                "lr": "closest_logic_dropin",
                "lrf": ["Logic Pro project", "WAV/AIFF", "Key on file"],
            }
        )
        self.assertIn(
            "Assets on file: Logic Pro project · WAV/AIFF · Key on file", card
        )
        self.assertNotIn(".logicx", card)
        self.assertNotIn(".wav", card)
        no_tags_card = song_work_card(
            {
                "id": "JS-9999",
                "t": "No Evidence",
                "nx": "Track overdubs",
                "lr": "empty_logic_ready",
                "lrf": [],
            }
        )
        self.assertNotIn("Assets on file", no_tags_card)

    def test_system_and_midi_horns_are_not_stems_or_keys(self):
        row = {
            "song_id": "ST-0004",
            "key": "",
            "notes": (
                "first aesthetic evaluation in the system; "
                "possible future MIDI horns"
            ),
            "sources": ["band bounce"],
        }
        self.assertEqual(song_logic_ready_cluster(row), "empty_logic_ready")
        self.assertEqual(
            song_logic_ready_cluster(
                {"song_id": "X", "key": "Am", "sources": ["demo.m4a"]}
            ),
            "key_only",
        )
        self.assertEqual(
            song_logic_ready_cluster(
                {
                    "song_id": "X",
                    "key": "C",
                    "sources": ["song v1.0.logicx", "mix.wav"],
                }
            ),
            "closest_logic_dropin",
        )

    def test_originals_match_the_logic_ready_walk(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        with open(
            os.path.join(ROOT, "data", "version_chains.json"), encoding="utf-8"
        ) as handle:
            chains = json.load(handle)
        expected = {
            song_id: cluster
            for cluster, ids in WALK_ORIGINAL_LOGIC_READY.items()
            for song_id in ids
        }
        self.assertEqual(len(expected), 126)
        got = {}
        for song in catalog["songs"]:
            if song.get("classification") != "original":
                continue
            cluster = song_logic_ready_cluster(
                song, chains.get(song["song_id"])
            )
            got[song["song_id"]] = cluster
        self.assertEqual(got, expected)
        self.assertEqual(got["ST-0004"], "audio_only")
        self.assertFalse(str(next(
            song for song in catalog["songs"] if song["song_id"] == "ST-0004"
        ).get("key") or "").strip())

    def test_work_card_includes_sanitized_logic_ready_next(self):
        card = song_work_card(
            {
                "id": "ST-0001",
                "t": "Turn Over The Flag",
                "nx": "Track the remaining overdubs",
                "lr": "closest_logic_dropin",
            }
        )
        self.assertIn("Logic-ready: Closest Logic Pro drop-in", card)
        self.assertIn(
            "Logic next: Open the existing Logic Pro project on your Mac",
            card,
        )
        self.assertNotIn(".logicx", card)
        self.assertNotIn(".wav", card)

    def test_committed_dashboard_projects_logic_ready_clusters_only(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        with open(
            os.path.join(ROOT, "data", "version_chains.json"), encoding="utf-8"
        ) as handle:
            chains = json.load(handle)
        expected = {
            song["song_id"]: song_logic_ready_cluster(
                song, chains.get(song["song_id"])
            )
            for song in catalog["songs"]
        }
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        payloads = embedded_dashboard_payloads(dashboard)
        rows = json.loads(payloads["DATA"])
        projected = {row["id"]: row.get("lr") for row in rows}
        self.assertEqual(projected, expected)
        self.assertIn("const LOGIC_READY = ", dashboard)
        self.assertEqual(
            json.loads(dashboard.split("const LOGIC_READY = ", 1)[1].split(";\n", 1)[0]),
            logic_ready_maps(),
        )
        self.assertTrue(dashboard_exposes_logic_ready(dashboard))
        self.assertNotIn("folder", json.dumps(logic_ready_maps()))

    def test_committed_dashboard_projects_logic_native_asset_tags_only(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        with open(
            os.path.join(ROOT, "data", "version_chains.json"), encoding="utf-8"
        ) as handle:
            chains = json.load(handle)
        expected = {
            song["song_id"]: song_logic_ready_evidence_tags(
                song, chains.get(song["song_id"])
            )
            for song in catalog["songs"]
        }
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        payloads = embedded_dashboard_payloads(dashboard)
        rows = json.loads(payloads["DATA"])
        projected = {row["id"]: row.get("lrf") or [] for row in rows}
        self.assertEqual(projected, expected)
        self.assertGreater(sum(1 for tags in expected.values() if tags), 0)
        for tags in expected.values():
            for tag in tags:
                self.assertNotIn(".", tag)
                self.assertNotIn("/Users", tag)
                self.assertNotIn("file://", tag)
        self.assertIn("function logicReadyFormats(", dashboard)
        self.assertIn("Assets on file", dashboard)


class DashboardPhoneA11yTests(unittest.TestCase):
    def test_committed_dashboard_is_usable_at_375px(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertTrue(dashboard_phone_and_a11y_ready(dashboard))
        self.assertTrue(dashboard_phone_layout_covers(dashboard, 390))
        self.assertIn("Skip to work session", dashboard)
        self.assertIn("<header>", dashboard)
        self.assertIn('<main id="main"', dashboard)
        self.assertIn("<footer", dashboard)
        self.assertIn('aria-label="Sort songs"', dashboard)
        self.assertIn('aria-label="Search memo transcripts"', dashboard)
        self.assertIn("@media(max-width:640px)", dashboard)
        self.assertNotIn("@media(max-width:375px)", dashboard)
        self.assertIn("min-height:44px", dashboard)
        self.assertIn("overflow-x:hidden", dashboard)
        self.assertIn(":focus-visible", dashboard)
        self.assertIn('class="score-lab"', dashboard)
        self.assertNotIn('role="columnheader"', dashboard)
        self.assertIn('<h2 id="workNowTitle" tabindex="-1">', dashboard)
        self.assertIn('class="row-heading"', dashboard)
        self.assertIn('aria-controls="song-detail-', dashboard)
        self.assertNotIn("grid-template-columns:1fr 90px 90px", dashboard)

    def test_phone_padding_and_two_up_stats_apply_at_640px_not_375px(self):
        padding = (
            "body{padding:12px;font-size:16px}.rhead{padding:10px}"
            ".stat{min-width:0;flex-basis:calc(50% - 10px)}"
        )
        only_375 = f"<style>@media(max-width:375px){{{padding}}}</style>"
        at_640 = f"<style>@media(max-width:640px){{{padding}}}</style>"
        at_400 = f"<style>@media(max-width:400px){{{padding}}}</style>"
        self.assertFalse(dashboard_phone_layout_covers(only_375, 390))
        self.assertTrue(dashboard_phone_layout_covers(at_640, 390))
        self.assertTrue(dashboard_phone_layout_covers(at_400, 390))
        self.assertFalse(dashboard_phone_layout_covers(at_640, 800))

        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        reverted = dashboard.replace(
            "body{padding:12px;font-size:16px}.rhead{padding:10px}"
            ".stat{min-width:0;flex-basis:calc(50% - 10px)}",
            "",
        ).replace(
            "</style>",
            f"@media(max-width:375px){{{padding}}}</style>",
            1,
        )
        self.assertFalse(dashboard_phone_layout_covers(reverted, 390))
        self.assertFalse(dashboard_phone_and_a11y_ready(reverted))

    def test_computed_home_layout_at_390px_uses_phone_padding_and_two_up_stats(self):
        padding = (
            "body{padding:12px;font-size:16px}.rhead{padding:10px}"
            ".stat{min-width:0;flex-basis:calc(50% - 10px)}"
        )
        base = (
            "<style>body{padding:20px;font-size:16px}"
            ".stat{min-width:100px;flex:1 1 140px}"
            f"@media(max-width:640px){{{padding}}}</style>"
        )
        self.assertEqual(
            dashboard_computed_home_layout(base, 390),
            {"padding": "12px", "stat_flex_basis": "calc(50% - 10px)"},
        )
        self.assertEqual(dashboard_computed_home_layout(base, 800)["padding"], "20px")
        self.assertNotEqual(
            dashboard_computed_home_layout(base, 800)["stat_flex_basis"],
            "calc(50% - 10px)",
        )
        only_375 = base.replace("max-width:640px", "max-width:375px")
        self.assertEqual(dashboard_computed_home_layout(only_375, 390)["padding"], "20px")
        self.assertIsNone(dashboard_computed_home_layout(only_375, 390)["stat_flex_basis"])

        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        phone = dashboard_computed_home_layout(dashboard, 390)
        desktop = dashboard_computed_home_layout(dashboard, 800)
        self.assertEqual(phone["padding"], "12px")
        self.assertEqual(phone["stat_flex_basis"], "calc(50% - 10px)")
        self.assertEqual(desktop["padding"], "20px")
        self.assertNotEqual(desktop["stat_flex_basis"], "calc(50% - 10px)")
        overridden = dashboard.replace("</style>", "body{padding:20px}</style>", 1)
        self.assertTrue(dashboard_phone_layout_covers(overridden, 390))
        self.assertEqual(dashboard_computed_home_layout(overridden, 390)["padding"], "20px")
        self.assertFalse(dashboard_phone_and_a11y_ready(overridden))

    def test_phone_home_browser_check_measures_390px_padding_and_two_up_stats(self):
        with open(
            os.path.join(ROOT, "tests", "test_dashboard_phone_home.js"),
            encoding="utf-8",
        ) as handle:
            source = handle.read()
        self.assertIn("width: 390, height: 844", source)
        self.assertIn("paddingLeft", source)
        self.assertIn("12px", source)
        self.assertIn("firstRowCount", source)
        self.assertIn("expanded stats must be 2-up at 390px", source)
        self.assertIn("390px home must use 12px body padding", source)
        self.assertIn("Write / Produce / Listen must be on the first 390×844 screen", source)
        self.assertIn("will not download a browser", source)

    def test_phone_gate_fails_closed_without_landmarks(self):
        self.assertFalse(dashboard_phone_and_a11y_ready("<html></html>"))

    def test_phone_gate_rejects_table_roles_and_skip_past_work(self):
        with open(os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"), encoding="utf-8") as handle:
            dashboard = handle.read()
        self.assertFalse(dashboard_phone_and_a11y_ready(
            dashboard.replace('class="score-lab"', 'class="score-lab" role="columnheader"')
        ))
        self.assertFalse(dashboard_phone_and_a11y_ready(
            dashboard.replace('href="#workNowTitle"', 'href="#main"')
        ))

    def test_resume_browser_check_still_rejects_offscreen_fold(self):
        with open(
            os.path.join(ROOT, "tests", "test_dashboard_resume_browser.js"),
            encoding="utf-8",
        ) as handle:
            source = handle.read()
        self.assertIn("{ name: \"phone\", width: 390, height: 844", source)
        self.assertIn("{ name: \"desktop\", width: 1280, height: 800", source)
        self.assertIn("must fit above the fold", source)
        self.assertIn(".resume-work{margin-top:2000px!important}", source)
        self.assertIn("resumeWorkButton", source)
        self.assertIn("resumeWorkNext", source)
        self.assertIn("copyResumeNext", source)
        self.assertIn("forgetWorkSession", source)
        self.assertIn("Do this now:", source)
        self.assertIn("will not download a browser", source)


class DashboardFirstPaintTests(unittest.TestCase):
    def test_cover_and_recovered_counts_come_from_catalog(self):
        self.assertEqual(catalog_cover_count({"covers": ["a", "b"], "covers_reference": 99}), 2)
        self.assertEqual(catalog_cover_count({"covers_reference": 4}), 4)
        self.assertEqual(catalog_cover_count({"covers_reference": "nope"}), 0)
        self.assertEqual(catalog_cover_count(None), 0)
        self.assertEqual(
            catalog_recovered_count(
                {
                    "songs": [
                        {"stage": "voice memo only (recovered 2026-08 via transcript pass)"},
                        {"stage": "mixing — album track 1"},
                        {"stage": "voice memo only (recovered 2026-08, discovery pass)"},
                        {"notes": "lyric 85% recovered"},
                        {"lyric_status": "partial — recovered from memo transcript(s)"},
                        {
                            "lyric_status": (
                                'OPENING MOVEMENT RECOVERED from "Blue skies beginning" '
                                "memo transcript"
                            )
                        },
                    ]
                }
            ),
            3,
        )
        self.assertEqual(catalog_recovered_count({"songs": []}), 0)
        self.assertEqual(catalog_recovered_count(None), 0)

        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        self.assertEqual(catalog_cover_count(catalog), len(catalog.get("covers") or []))
        self.assertEqual(catalog_recovered_count(catalog), 11)
        recovered_ids = [
            song["song_id"]
            for song in catalog["songs"]
            if "recovered" in str(song.get("stage") or "").lower()
            or "recovered from memo" in str(song.get("lyric_status") or "").lower()
        ]
        self.assertEqual(len(recovered_ids), 11)
        self.assertIn("JS-0131", recovered_ids)
        self.assertNotIn("JS-0107", recovered_ids)
        self.assertNotIn("JS-0128", recovered_ids)

    def test_committed_dashboard_keeps_work_buttons_on_first_paint(self):
        with open(
            os.path.join(ROOT, "data", "master_catalog.json"), encoding="utf-8"
        ) as handle:
            catalog = json.load(handle)
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        with open(
            os.path.join(ROOT, "scripts", "build_dashboard.py"), encoding="utf-8"
        ) as handle:
            builder = handle.read()
        self.assertTrue(dashboard_first_paint_ready(dashboard))
        self.assertIn("No audio in this repo, and catalog rows are not the live set.", dashboard)
        self.assertIn(f"const COVER_COUNT = {catalog_cover_count(catalog)};", dashboard)
        self.assertIn(f"const RECOVERED_COUNT = {catalog_recovered_count(catalog)};", dashboard)
        self.assertIn("${RECOVERED_COUNT}", dashboard)
        self.assertNotIn("<b>9</b>", dashboard)
        self.assertNotIn("<b>9</b>", builder)
        self.assertNotIn("93 covers cataloged", builder)
        self.assertIn("id=\"statsFold\"", dashboard)
        chrome_head = dashboard.split("<script>", 1)[0]
        self.assertLess(chrome_head.find('id="workStarts"'), chrome_head.find('id="statsFold"'))

    def test_first_paint_gate_fails_closed_without_collapsed_counts(self):
        self.assertFalse(dashboard_first_paint_ready("<html></html>"))
        self.assertFalse(
            dashboard_first_paint_ready(
                'No audio in this repo, and catalog rows are not the live set. '
                'id="statsFold" <details id="statsLine" id="stats" '
                'const COVER_COUNT const RECOVERED_COUNT data-open-work='
            )
        )

    def test_resume_leads_first_paint_without_extra_storage_fields(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertTrue(dashboard_resume_leads_first_paint(dashboard))
        chrome = dashboard.split("<script>", 1)[0]
        self.assertLess(chrome.find('id="resumeWork"'), chrome.find('id="resumeWorkNext"'))
        self.assertLess(chrome.find('id="resumeWorkNext"'), chrome.find('id="copyResumeNext"'))
        self.assertLess(chrome.find('id="copyResumeNext"'), chrome.find('id="forgetWorkSession"'))
        self.assertLess(chrome.find('id="forgetWorkSession"'), chrome.find('id="workStarts"'))
        self.assertIn("has-resume", dashboard)
        self.assertIn("Object.keys(value).sort().join('|')!=='id|kind|v'", dashboard)
        store = dashboard[dashboard.find("function storeWorkSession("):dashboard.find("function clearStoredWorkSession(")]
        self.assertIn("JSON.stringify(parsed)", store)
        self.assertNotIn("title", store)
        self.assertNotIn("next", store)

    def test_work_next_stays_in_view_while_song_expands(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertTrue(dashboard_work_next_stays_in_view(dashboard))
        focus = dashboard[dashboard.find("function focusWorkSong("):dashboard.find("function stepWork(")]
        self.assertIn("scrollIntoView({block:'nearest'})", focus)
        self.assertIn("sessionEl.scrollIntoView({block:'nearest'})", focus)
        self.assertIn("toggleSong(head,true)", focus)
        self.assertIn("#workSession{position:sticky", dashboard)
        self.assertIn("overflow-x:clip", dashboard)

    def test_listen_button_cannot_mean_playback(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertTrue(dashboard_listen_is_not_playback(dashboard))
        self.assertIn("if(k==='listen')return 'Listen in Logic';", dashboard)
        self.assertIn("${workKindLabel(kind)} <span>${workCounts[kind]} songs</span>", dashboard)
        self.assertIn('option value="listen">Listen in Logic</option>', dashboard)
        self.assertNotIn("<audio", dashboard)
        self.assertIn("this page does not open audio", dashboard)


# Pre-A06 oranges from the UX audit. Kept here so the contrast gate
# stays red if someone restores them. Light-scheme PNGs were NOT RUN.
_OLD_RDY_DARK = "#d95926"
_OLD_RDY_LIGHT = "#eb6834"
_AUDIT_RDY_SNIPPET = """<style>
:root{--bg:#1a1a19;--card:#242423;--card2:#2c2c2a;--ink:#ffffff;--rdy:#d95926;}
@media (prefers-color-scheme: light){:root{--bg:#fcfcfb;--card:#ffffff;--card2:#f3f3f0;--ink:#1a1a19;--rdy:#eb6834;}}
.pill.wk-produce{color:var(--rdy)}.bar-n{color:var(--ink)}
</style><span class="bar-n">74</span><span class="pill wk-produce">produce</span>"""
_FIXED_RDY_SNIPPET = """<style>
:root{--bg:#1a1a19;--card:#242423;--card2:#2c2c2a;--ink:#ffffff;--rdy:#ee7a3a;}
@media (prefers-color-scheme: light){:root{--bg:#fcfcfb;--card:#ffffff;--card2:#f3f3f0;--ink:#1a1a19;--rdy:#b84414;}}
.pill.wk-produce{color:var(--rdy)}.bar-n{color:var(--ink)}
</style><span class="bar-n">74</span><span class="pill wk-produce">produce</span>"""


class DashboardRdyContrastTests(unittest.TestCase):
    def test_audit_oranges_miss_aa_on_bg_and_card(self):
        self.assertLess(contrast_ratio(_OLD_RDY_DARK, "#1a1a19"), WCAG_AA_NORMAL_TEXT)
        self.assertLess(contrast_ratio(_OLD_RDY_DARK, "#242423"), WCAG_AA_NORMAL_TEXT)
        self.assertLess(contrast_ratio(_OLD_RDY_LIGHT, "#fcfcfb"), WCAG_AA_NORMAL_TEXT)
        self.assertLess(contrast_ratio(_OLD_RDY_LIGHT, "#ffffff"), WCAG_AA_NORMAL_TEXT)
        self.assertAlmostEqual(contrast_ratio(_OLD_RDY_DARK, "#1a1a19"), 4.48, places=2)
        self.assertAlmostEqual(contrast_ratio(_OLD_RDY_LIGHT, "#fcfcfb"), 3.12, places=2)
        self.assertFalse(dashboard_rdy_contrast_ready(_AUDIT_RDY_SNIPPET))

    def test_gate_fails_closed_without_light_scheme_or_ink_labels(self):
        self.assertFalse(dashboard_rdy_contrast_ready("<html></html>"))
        no_light = _FIXED_RDY_SNIPPET.replace(
            "@media (prefers-color-scheme: light)", "@media (min-width: 1px)"
        )
        self.assertFalse(dashboard_rdy_contrast_ready(no_light))
        no_ink = _FIXED_RDY_SNIPPET.replace(".bar-n{color:var(--ink)}", "")
        self.assertFalse(dashboard_rdy_contrast_ready(no_ink))
        no_produce = _FIXED_RDY_SNIPPET.replace(
            ".pill.wk-produce{color:var(--rdy)}", ".pill.wk-produce{color:var(--pot)}"
        )
        self.assertFalse(dashboard_rdy_contrast_ready(no_produce))

    def test_fixed_tokens_meet_aa_and_keep_light_scheme(self):
        self.assertTrue(dashboard_rdy_contrast_ready(_FIXED_RDY_SNIPPET))
        dark, light = dashboard_theme_tokens(_FIXED_RDY_SNIPPET)
        for theme in (dark, light):
            self.assertGreaterEqual(
                contrast_ratio(theme["rdy"], theme["bg"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["rdy"], theme["card"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["rdy"], theme["card2"]), WCAG_AA_NORMAL_TEXT
            )

    def test_committed_dashboard_produce_and_readiness_meet_aa(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertTrue(dashboard_rdy_contrast_ready(dashboard))
        self.assertIn("@media (prefers-color-scheme: light)", dashboard)
        self.assertIn(".pill.wk-produce{color:var(--rdy)}", dashboard)
        self.assertIn(".bar-n{color:var(--ink)}", dashboard)
        self.assertIn('class="bar-n"', dashboard)
        self.assertNotIn("--rdy:#d95926", dashboard)
        self.assertNotIn("--rdy:#eb6834", dashboard)
        dark, light = dashboard_theme_tokens(dashboard)
        self.assertEqual(dark.get("ink"), "#ffffff")
        self.assertEqual(light.get("ink"), "#1a1a19")
        for theme in (dark, light):
            self.assertGreaterEqual(
                contrast_ratio(theme["rdy"], theme["bg"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["rdy"], theme["card"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["ink"], theme["bg"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["ink"], theme["card"]), WCAG_AA_NORMAL_TEXT
            )


# Pre-fix Potential blues used as write/link text. Bar --pot stays.
_OLD_WRITE_DARK = "#3987e5"
_OLD_WRITE_LIGHT = "#2a78d6"
_AUDIT_WRITE_SNIPPET = """<style>
:root{--bg:#1a1a19;--card:#242423;--card2:#2c2c2a;--ink:#ffffff;--write:#3987e5;}
@media (prefers-color-scheme: light){:root{--bg:#fcfcfb;--card:#ffffff;--card2:#f3f3f0;--ink:#1a1a19;--write:#2a78d6;}}
.pill.wk-write{color:var(--write)}.memo-link,.song-link{padding:8px 10px;color:var(--write)}.tag.f{color:var(--write)}
</style><span class="pill wk-write">write</span>"""
_FIXED_WRITE_SNIPPET = """<style>
:root{--bg:#1a1a19;--card:#242423;--card2:#2c2c2a;--ink:#ffffff;--write:#3993fd;}
@media (prefers-color-scheme: light){:root{--bg:#fcfcfb;--card:#ffffff;--card2:#f3f3f0;--ink:#1a1a19;--write:#2466b8;}}
.pill.wk-write{color:var(--write)}.memo-link,.song-link{padding:8px 10px;color:var(--write)}.tag.f{color:var(--write)}
</style><span class="pill wk-write">write</span>"""


class DashboardWriteContrastTests(unittest.TestCase):
    def test_audit_blues_miss_aa_on_card_and_light_bg(self):
        self.assertGreaterEqual(contrast_ratio(_OLD_WRITE_DARK, "#1a1a19"), WCAG_AA_NORMAL_TEXT)
        self.assertLess(contrast_ratio(_OLD_WRITE_DARK, "#242423"), WCAG_AA_NORMAL_TEXT)
        self.assertLess(contrast_ratio(_OLD_WRITE_LIGHT, "#fcfcfb"), WCAG_AA_NORMAL_TEXT)
        self.assertLess(contrast_ratio(_OLD_WRITE_LIGHT, "#ffffff"), WCAG_AA_NORMAL_TEXT)
        self.assertAlmostEqual(contrast_ratio(_OLD_WRITE_DARK, "#242423"), 4.27, places=2)
        self.assertAlmostEqual(contrast_ratio(_OLD_WRITE_LIGHT, "#fcfcfb"), 4.30, places=2)
        self.assertFalse(dashboard_write_contrast_ready(_AUDIT_WRITE_SNIPPET))

    def test_gate_fails_closed_without_write_token_or_light_scheme(self):
        self.assertFalse(dashboard_write_contrast_ready("<html></html>"))
        no_light = _FIXED_WRITE_SNIPPET.replace(
            "@media (prefers-color-scheme: light)", "@media (min-width: 1px)"
        )
        self.assertFalse(dashboard_write_contrast_ready(no_light))
        no_write_pill = _FIXED_WRITE_SNIPPET.replace(
            ".pill.wk-write{color:var(--write)}", ".pill.wk-write{color:var(--pot)}"
        )
        self.assertFalse(dashboard_write_contrast_ready(no_write_pill))
        no_link = _FIXED_WRITE_SNIPPET.replace(
            ".memo-link,.song-link{padding:8px 10px;color:var(--write)}",
            ".memo-link,.song-link{padding:8px 10px;color:var(--pot)}",
        )
        self.assertFalse(dashboard_write_contrast_ready(no_link))

    def test_fixed_write_tokens_meet_aa_and_keep_light_scheme(self):
        self.assertTrue(dashboard_write_contrast_ready(_FIXED_WRITE_SNIPPET))
        dark, light = dashboard_theme_tokens(_FIXED_WRITE_SNIPPET)
        for theme in (dark, light):
            self.assertGreaterEqual(
                contrast_ratio(theme["write"], theme["bg"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["write"], theme["card"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["write"], theme["card2"]), WCAG_AA_NORMAL_TEXT
            )

    def test_committed_dashboard_write_and_links_meet_aa(self):
        with open(
            os.path.join(ROOT, "Jeff Story Song Vault Dashboard.html"),
            encoding="utf-8",
        ) as handle:
            dashboard = handle.read()
        self.assertTrue(dashboard_write_contrast_ready(dashboard))
        self.assertIn("--write:#3993fd", dashboard)
        self.assertIn("--write:#2466b8", dashboard)
        self.assertIn(".pill.wk-write{color:var(--write)}", dashboard)
        self.assertIn(".memo-link,.song-link{padding:8px 10px;color:var(--write)}", dashboard)
        self.assertIn(".tag.f{color:var(--write)}", dashboard)
        self.assertIn("--pot:#3987e5", dashboard)
        self.assertIn("--pot:#2a78d6", dashboard)
        dark, light = dashboard_theme_tokens(dashboard)
        for theme in (dark, light):
            self.assertGreaterEqual(
                contrast_ratio(theme["write"], theme["bg"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["write"], theme["card"]), WCAG_AA_NORMAL_TEXT
            )
            self.assertGreaterEqual(
                contrast_ratio(theme["write"], theme["card2"]), WCAG_AA_NORMAL_TEXT
            )


if __name__ == "__main__":
    unittest.main()
