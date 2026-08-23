#!/usr/bin/env python3
"""Export honesty: StoryBoard reads bpm/key/project, not the PR #1 field-map guesses."""
from __future__ import annotations

import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys_path_scripts = os.path.join(ROOT, "scripts")

import sys

sys.path.insert(0, sys_path_scripts)

from export_app_api import (  # noqa: E402
    SCHEMA_VERSION,
    build_payload,
    check_committed,
    comparable,
)
from storyboard_contract import (  # noqa: E402
    CATALOG_IMPORT_POLICY_VERSION,
    bpm_int,
    clean_title,
    default_decisions,
    import_scope,
    parse_bpm,
    source_key,
    storyboard_mapping,
    storyboard_parse_bpm,
)
from test_validate_catalog import fixture  # noqa: E402


class ExportHonestyTests(unittest.TestCase):
    def test_schema_version_is_importer_honest(self):
        self.assertEqual(SCHEMA_VERSION, 3)
        payload = build_payload(fixture())
        self.assertEqual(payload["schema_version"], 3)
        self.assertEqual(payload["primary_consumer"], "StoryBoard")

    def test_bpm_field_is_what_storyboard_parses(self):
        cat = fixture()
        cat["songs"][0]["bpm"] = "214 (cut)"
        payload = build_payload(cat)
        rec = next(s for s in payload["songs"] if s["id"] == "ST-0001")
        self.assertEqual(rec["bpm"], 214)
        self.assertEqual(rec["bpm_raw"], "214 (cut)")
        self.assertEqual(rec["bpm_int"], 214)
        self.assertEqual(storyboard_parse_bpm(rec["bpm"]), 214)
        self.assertEqual(parse_bpm(rec), 214)
        self.assertEqual(storyboard_parse_bpm(rec["bpm_raw"]), 214)

    def test_empty_bpm_exports_null(self):
        cat = fixture()
        cat["songs"][0]["bpm"] = ""
        rec = build_payload(cat)["songs"][0]
        self.assertIsNone(rec["bpm"])
        self.assertEqual(rec["bpm_raw"], "")

    def test_field_map_matches_importer(self):
        mapping = storyboard_mapping()
        self.assertEqual(mapping["field_map"]["bpm"], "bpm_int")
        self.assertEqual(mapping["field_map"]["musicalKey"], "key")
        self.assertIn("is_original", mapping["field_map"]["active"])
        self.assertEqual(mapping["field_map"]["notes"], "vault_ref")
        self.assertIn("catalog_import_v1", mapping["merge_key"])
        self.assertEqual(mapping["storyliner_role"], "promo only")
        self.assertEqual(mapping["booker_policy"], "travis_books")
        self.assertTrue(mapping["no_fourth_live_band"])
        self.assertEqual(mapping["live_catalog_projects"], ["Rad Dad", "Jeff Story"])

    def test_default_live_setlist_is_empty_without_live_repertoire(self):
        payload = build_payload(fixture())
        self.assertEqual(payload["setlist_ready_default_import"], [])
        self.assertEqual(payload["counts"]["storyboard_default_live"], 0)
        self.assertGreater(payload["counts"]["setlist_ready"], 0)
        self.assertTrue(all(s["import_scope"] != "default_live" for s in payload["songs"]))

    def test_rad_dad_label_enters_default_import(self):
        cat = fixture()
        cat["songs"][0]["artist_project"] = "Rad Dad"
        payload = build_payload(cat)
        rec = next(s for s in payload["songs"] if s["id"] == "ST-0001")
        self.assertEqual(rec["import_scope"], "default_live")
        self.assertEqual(payload["counts"]["storyboard_default_live"], 1)
        self.assertEqual(
            [row["id"] for row in payload["setlist_ready_default_import"]],
            ["ST-0001"],
        )

    def test_jeff_story_label_enters_default_import(self):
        cat = fixture()
        cat["songs"][0]["artist_project"] = "Jeff Story"
        payload = build_payload(cat)
        rec = next(s for s in payload["songs"] if s["id"] == "ST-0001")
        self.assertEqual(rec["import_scope"], "default_live")
        self.assertEqual(
            [row["id"] for row in payload["setlist_ready_default_import"]],
            ["ST-0001"],
        )

    def test_played_live_rad_dad_enters_default_import(self):
        cat = fixture()
        cat["songs"][0]["live_presence"] = [{"band": "Rad Dad", "date": "2026-05"}]
        payload = build_payload(cat)
        rec = next(s for s in payload["songs"] if s["id"] == "ST-0001")
        self.assertEqual(rec["played_live"], ["Rad Dad (2026-05)"])
        self.assertEqual(rec["import_scope"], "default_live")
        self.assertEqual(
            [row["id"] for row in payload["setlist_ready_default_import"]],
            ["ST-0001"],
        )

    def test_travis_is_booker_not_a_live_band(self):
        cat = fixture()
        cat["songs"].append(
            {
                **cat["songs"][0],
                "song_id": "JS-0997",
                "canonical_title": "Your New Boyfriend",
                "artist_project": "Travis Story",
                "classification": "original",
                "writers": ["Travis Story"],
                "ai_upload_ok": "NO — someone else's composition",
                "key": "C",
            }
        )
        cat["original_song_entities"] = 6
        payload = build_payload(cat)
        rec = next(s for s in payload["songs"] if s["id"] == "JS-0997")
        self.assertEqual(rec["import_scope"], "travis_books")
        self.assertEqual(payload["counts"]["storyboard_booker"], 1)
        self.assertNotIn(
            "JS-0997",
            [row["id"] for row in payload["setlist_ready_default_import"]],
        )

    def test_cover_stays_out_of_default_import(self):
        cat = fixture()
        cat["songs"][5]["classification"] = "cover"
        cat["songs"][5]["live_presence"] = [{"band": "Rad Dad", "date": "2026-05"}]
        cat["original_song_entities"] = 4
        payload = build_payload(cat)
        rec = next(s for s in payload["songs"] if s["id"] == "JS-0001")
        self.assertEqual(rec["import_scope"], "cover_not_active")
        self.assertNotIn(
            "JS-0001",
            [row["id"] for row in payload["setlist_ready_default_import"]],
        )

    def test_clean_title_strips_arrows(self):
        self.assertEqual(clean_title("Harbor Lights →"), "Harbor Lights")

    def test_source_key_matches_storyboard_constructor(self):
        self.assertEqual(
            source_key("ST-0004"),
            f"vault:{CATALOG_IMPORT_POLICY_VERSION}:ST-0004",
        )
        rec = next(s for s in build_payload(fixture())["songs"] if s["id"] == "ST-0004")
        self.assertEqual(rec["source_key"], "vault:catalog_import_v1:ST-0004")

    def test_duration_stays_null(self):
        for rec in build_payload(fixture())["songs"]:
            self.assertIsNone(rec["duration_seconds"])

    def test_check_passes_against_its_own_write(self):
        cat = fixture()
        payload = build_payload(cat, generated="2026-08-23")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "app_api.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            self.assertEqual(check_committed(cat, path), [])

    def test_check_fails_on_stale_field_map(self):
        cat = fixture()
        payload = build_payload(cat, generated="2026-08-23")
        payload["storyboard"]["field_map"]["bpm"] = "bpm"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "app_api.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            errors = check_committed(cat, path)
        self.assertTrue(errors)

    def test_comparable_ignores_generated_date(self):
        a = build_payload(fixture(), generated="2026-08-23")
        b = build_payload(fixture(), generated="2026-08-24")
        self.assertEqual(comparable(a), comparable(b))

    def test_live_repo_export_matches_committed_file(self):
        from export_app_api import CAT, OUT

        with open(CAT, encoding="utf-8") as handle:
            cat = json.load(handle)
        self.assertEqual(check_committed(cat, OUT), [], "re-run export_app_api.py")

    def test_live_repo_default_import_matches_storyboard_planner(self):
        from export_app_api import CAT, OUT

        with open(CAT, encoding="utf-8") as handle:
            cat = json.load(handle)
        with open(OUT, encoding="utf-8") as handle:
            api = json.load(handle)
        ready_ids = {row["id"] for row in api["setlist_ready"]}
        planned = {
            song["id"]
            for song, decision in default_decisions(api["songs"], ready_ids)
            if decision.include
        }
        published = {row["id"] for row in api["setlist_ready_default_import"]}
        self.assertEqual(published, planned)
        self.assertEqual(len(published), api["counts"]["storyboard_default_live"])
        self.assertGreater(len(published), 0)
        self.assertTrue(all(sid in ready_ids for sid in published))

    def test_bpm_int_alias(self):
        self.assertEqual(bpm_int(103), 103)
        self.assertEqual(import_scope("rad dad"), "default_live")


if __name__ == "__main__":
    unittest.main()
