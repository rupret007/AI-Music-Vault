#!/usr/bin/env python3
"""Dashboard transcript totals must stay distinct from its useful search index."""
from __future__ import annotations

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from catalog_surface import build_memo_search_index  # noqa: E402


class DashboardMemoHonestyTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
