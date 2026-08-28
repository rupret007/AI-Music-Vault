#!/usr/bin/env python3
"""Derived CSV honesty: master_catalog.csv is the spine, not a second catalog."""
from __future__ import annotations

import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys

sys.path.insert(0, os.path.join(ROOT, "scripts"))

from export_catalog_csv import (  # noqa: E402
    CSV_FIELDS,
    check_committed,
    comparable_csv,
    csv_rows_from_catalog,
    write_catalog_csv,
)
from test_validate_catalog import fixture  # noqa: E402


class ExportCatalogCsvTests(unittest.TestCase):
    def test_rows_follow_spine_order_and_ids(self):
        cat = fixture()
        rows = csv_rows_from_catalog(cat)
        self.assertEqual(
            [row["song_id"] for row in rows],
            [song["song_id"] for song in cat["songs"]],
        )
        self.assertEqual(list(rows[0].keys()), list(CSV_FIELDS))

    def test_lists_join_with_semicolons(self):
        cat = fixture()
        cat["songs"][0]["alt_titles"] = ["turn over", "flag"]
        cat["songs"][0]["writers"] = ["Jeff Story"]
        row = csv_rows_from_catalog(cat)[0]
        self.assertEqual(row["alt_titles"], "turn over; flag")
        self.assertEqual(row["writers"], "Jeff Story")

    def test_blank_scores_stay_blank(self):
        cat = fixture()
        cat["songs"][0]["potential"] = None
        cat["songs"][0]["readiness"] = None
        row = csv_rows_from_catalog(cat)[0]
        self.assertEqual(row["potential"], "")
        self.assertEqual(row["readiness"], "")

    def test_check_passes_against_its_own_write(self):
        cat = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "master_catalog.csv")
            write_catalog_csv(cat, path)
            self.assertEqual(check_committed(cat, path), [])

    def test_check_fails_on_dropped_row(self):
        cat = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "master_catalog.csv")
            write_catalog_csv(cat, path)
            stale = csv_rows_from_catalog(cat)[:-1]
            with open(path, "w", encoding="utf-8", newline="") as handle:
                import csv

                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(stale)
            errors = check_committed(cat, path)
        self.assertTrue(errors)

    def test_live_repo_csv_matches_export_after_write(self):
        from export_catalog_csv import CAT, OUT, check_committed
        import json

        with open(CAT, encoding="utf-8") as handle:
            cat = json.load(handle)
        expected = csv_rows_from_catalog(cat)
        with open(OUT, encoding="utf-8", newline="") as handle:
            import csv

            committed = list(csv.DictReader(handle))
        self.assertEqual(comparable_csv(committed), comparable_csv(expected))
        self.assertEqual(check_committed(cat), [])


if __name__ == "__main__":
    unittest.main()
