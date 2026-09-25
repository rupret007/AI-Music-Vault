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
    build_memo_search_index,
    dashboard_displays_owner_audio_index,
    dashboard_exposes_song_work,
    dashboard_finds_remembered_song_names,
    dashboard_opens_owner_audio,
    dashboard_resumes_song_work_privately,
    embedded_dashboard_payloads,
    latest_memo_for_song,
    memo_evidence_by_song,
    memo_lyric_norm_by_song,
    next_step_is_incomplete,
    normalize_search_text,
    parse_vault_hash,
    safe_song_next_step,
    song_aliases,
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
        self.assertIn("807 usable-text transcripts searchable", dashboard)
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
        self.assertIn("then log the sit-down handoff in Session Log.", dashboard)
        self.assertIn("Sit-down handoff: pair intake name + Copy next step in Session Log.", dashboard)
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
        card = song_work_card(
            {
                "id": "JS-0130",
                "t": "Been Loving You",
                "nx": 'LISTEN: play Maxwell Dr 99 (latest take). Verdict: gem.',
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


if __name__ == "__main__":
    unittest.main()
