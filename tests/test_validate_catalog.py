#!/usr/bin/env python3
"""Regression tests for scripts/validate_catalog.py — fail closed on broken catalogs."""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from export_app_api import build_payload  # noqa: E402
from storyboard_contract import (  # noqa: E402
    PARKED_NAMED_IN_DEFAULT_LIVE_WARNING,
    VAULT_DEFAULT_LIVE_SETLIST_NAME,
    VAULT_SETLIST_READY_SETLIST_NAME,
    VAULT_STORYBOARD_FIELD_MAP,
    catalog_import_scope,
    decide_vault_song,
    import_scope,
    live_default_decisions,
    parked_named_default_live_ids,
    parse_bpm,
    project_name_looks_parked,
    recognized_import_scope,
    storyboard_parse_bpm,
    vault_setlist_identity,
)
from validate_catalog import (  # noqa: E402
    ACTIVE_LANES,
    PROTECTED_LANES,
    YES_GATE,
    validate,
)


def song(sid, title, **kw):
    rec = {
        "song_id": sid,
        "canonical_title": title,
        "artist_project": "Stalemate",
        "classification": "original",
        "writers": ["Jeff Story"],
        "rights_confidence": "high",
        "stage": "cataloged",
        "ai_upload_ok": YES_GATE,
        "potential": 70,
        "readiness": 80,
        "next_action": "parked",
        "key": "A",
        "bpm": "120",
        "alt_titles": [],
        "sources": [],
        "soundcloud": [],
        "open_questions": "",
    }
    rec.update(kw)
    return rec


def fixture():
    songs = [
        song("ST-0001", "Turn Over The Flag"),
        song("ST-0004", "Manic"),
        song(
            "ST-0009",
            "Long Long Drive",
            rights_confidence='high — CONFIRMED by Jeff 2026-08-18: "i wrote it"',
        ),
        song("JS-0128", "It's Alright", next_action="confirm two chorus lines"),
        song(
            "JS-0107",
            "Blue Skies Fade",
            classification="co-write — concept suite (Jeff Story & Greg Baldia, 2010)",
            writers=["Jeff Story", "Greg Baldia"],
            rights_confidence="co-write — no external/AI use without Greg Baldia",
            ai_upload_ok="NEEDS CONSENT — co-write (Jeff Story, Greg Baldia)",
            next_action="protected opus — do not casually rewrite",
        ),
        song("JS-0001", "Drinking Song", next_action="rests"),
    ]
    return {
        "version": "1.6",
        "original_song_entities": 5,
        "covers_reference": 0,
        "covers": [],
        "songs": songs,
        "voice_memo_pool": {"matched": 2, "matched_songs": 1},
    }


def extras_ok(cat=None):
    cat = cat or fixture()
    return {
        "app_api": build_payload(cat),
        "vm_matches": {"ST-0001": ["uid-a", "uid-b"]},
        "priority_queue": (
            "ACTIVE (max 3 — unchanged)\n"
            "ST-0001 Turn Over The Flag\n"
            "ST-0004 Manic\n"
            "ST-0009 Long Long Drive\n"
        ),
        "dashboard_html": (
            "Catalog v1.6 · Turn Over The Flag · Manic · Long Long Drive · "
            "It's Alright · Blue Skies Fade"
        ),
        "audio_files": [],
    }


class ValidateCatalogTests(unittest.TestCase):
    def test_fixture_passes(self):
        self.assertEqual(validate(fixture(), extras_ok()), [])

    def test_duplicate_id_fails(self):
        cat = fixture()
        cat["songs"].append(song("ST-0001", "Turn Over Clone"))
        cat["original_song_entities"] = 6
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("duplicate song_id" in e for e in errors), errors)

    def test_score_out_of_range_fails(self):
        cat = fixture()
        cat["songs"][0]["potential"] = 140
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("potential=140" in e for e in errors), errors)

    def test_missing_gate_fails(self):
        cat = fixture()
        cat["songs"][0]["ai_upload_ok"] = ""
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("ai_upload_ok" in e for e in errors), errors)

    def test_long_long_drive_stale_gate_fails(self):
        """The overnight bug: rights high, gate still 'NO — rights confidence not high'."""
        cat = fixture()
        cat["songs"][2]["ai_upload_ok"] = "NO — rights confidence not high (resolve first)"
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("ST-0009" in e and "YES" in e for e in errors), errors)

    def test_blank_next_action_on_original_fails(self):
        cat = fixture()
        cat["songs"][0]["next_action"] = "   "
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("next_action" in e for e in errors), errors)

    def test_missing_lane_fails(self):
        cat = fixture()
        cat["songs"] = [s for s in cat["songs"] if s["song_id"] != "ST-0004"]
        cat["original_song_entities"] = 4
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("quick_win" in e for e in errors), errors)

    def test_opus_must_stay_needs_consent(self):
        cat = fixture()
        cat["songs"][4]["ai_upload_ok"] = YES_GATE
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("JS-0107" in e or "Blue Skies Fade" in e for e in errors), errors)

    def test_cover_cannot_be_yes(self):
        cat = fixture()
        cat["songs"].append(
            song(
                "JS-0999",
                "Fake Cover",
                classification="cover chart — Tom Petty",
                next_action="",
            )
        )
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("JS-0999" in e and "must not be AI-upload YES" in e for e in errors), errors)

    def test_stale_original_count_fails(self):
        cat = fixture()
        cat["original_song_entities"] = 113
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("original_song_entities" in e for e in errors), errors)

    def test_app_api_id_drift_fails(self):
        cat = fixture()
        extra = extras_ok(cat)
        extra["app_api"]["songs"] = extra["app_api"]["songs"][:-1]
        errors = validate(cat, extra)
        self.assertTrue(any("app_api.json song ids" in e for e in errors), errors)

    def test_setlist_order_must_stay_jeffs(self):
        cat = fixture()
        extra = extras_ok(cat)
        extra["app_api"]["storyboard"]["setlist"]["jeff_owns_order"] = False
        extra["app_api"]["storyboard"]["setlist"]["seed_from"] = "invented_set"
        errors = validate(cat, extra)
        self.assertTrue(any("setlist_ready" in e or "running order" in e for e in errors), errors)

    def test_app_api_must_name_storyboard(self):
        cat = fixture()
        extra = extras_ok(cat)
        extra["app_api"]["primary_consumer"] = "StoryDesk"
        errors = validate(cat, extra)
        self.assertTrue(any("StoryBoard" in e for e in errors), errors)

    def test_app_api_extra_lane_fails(self):
        cat = fixture()
        extra = extras_ok(cat)
        extra["app_api"]["lanes"] = {
            **extra["app_api"]["lanes"],
            "secret_fourth": "JS-0001",
        }
        errors = validate(cat, extra)
        self.assertTrue(any("lanes drifted" in e or "extra lanes" in e for e in errors), errors)

    def test_priority_queue_missing_cap_fails(self):
        cat = fixture()
        extra = extras_ok(cat)
        extra["priority_queue"] = "ST-0001 ST-0004 ST-0009 and also a fourth song"
        errors = validate(cat, extra)
        self.assertTrue(any("max-3" in e for e in errors), errors)

    def test_audio_in_repo_fails(self):
        cat = fixture()
        extra = extras_ok(cat)
        extra["audio_files"] = ["secret/master.wav"]
        errors = validate(cat, extra)
        self.assertTrue(any("audio masters must not live" in e for e in errors), errors)

    def test_bpm_int_parse(self):
        from export_app_api import bpm_int
        self.assertEqual(bpm_int("123"), 123)
        self.assertEqual(bpm_int("214 (cut)"), 214)
        self.assertIsNone(bpm_int(""))
        self.assertIsNone(bpm_int("Eb tuning"))

    def test_storyboard_parse_bpm_prefers_bpm_int(self):
        """StoryBoard #4: bpm_int first; leading tempo on bpm is fallback."""
        self.assertEqual(storyboard_parse_bpm(214), 214)
        self.assertEqual(storyboard_parse_bpm("145"), 145)
        self.assertEqual(storyboard_parse_bpm("214 (cut)"), 214)
        self.assertIsNone(storyboard_parse_bpm(""))
        self.assertIsNone(storyboard_parse_bpm("Eb tuning"))
        self.assertIsNone(storyboard_parse_bpm(True))
        self.assertEqual(
            parse_bpm({"bpm": "214 (cut)", "bpm_int": 214}),
            214,
        )
        self.assertEqual(
            parse_bpm({"bpm": "96", "bpm_int": 118}),
            118,
        )

    def test_hybrid_rad_dad_phrase_is_live_repertoire(self):
        self.assertEqual(import_scope("Rad Dad"), "default_live")
        self.assertEqual(import_scope("Jeff Story"), "default_live")
        self.assertEqual(import_scope("Stalemate"), "parked_catalog")
        self.assertEqual(import_scope("Trailer Swift"), "parked_catalog")
        self.assertEqual(import_scope("Something Dirty"), "parked_catalog")
        self.assertEqual(
            import_scope("Something Dirty / Stalemate / Rad Dad"),
            "default_live",
        )
        self.assertEqual(
            import_scope("Stalemate / Something Dirty"),
            "parked_catalog",
        )
        self.assertEqual(import_scope("Travis Story"), "travis_books")

    def test_missing_app_api_fails_closed(self):
        extra = extras_ok()
        extra["app_api"] = None
        errors = validate(fixture(), extra)
        self.assertTrue(any("app_api.json is required" in e for e in errors), errors)

    def test_validate_without_extras_fails_closed(self):
        errors = validate(fixture())
        self.assertTrue(any("app_api.json is required" in e for e in errors), errors)

    def test_field_map_bpm_not_bpm_int_fails(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["field_map"]["bpm"] = "bpm"
        errors = validate(fixture(), extra)
        self.assertTrue(any("prefers bpm_int" in e for e in errors), errors)

    def test_field_map_active_always_true_lie_fails(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["field_map"]["active"] = "always true on import"
        errors = validate(fixture(), extra)
        self.assertTrue(any("is_original" in e for e in errors), errors)

    def test_field_map_notes_constructed_lie_fails(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["field_map"]["notes"] = (
            "constructed: source {id} · {project} · original|not original"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(any("vault_ref" in e for e in errors), errors)

    def test_annotated_bpm_in_feed_fails(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0]["bpm"] = "214 (cut)"
        errors = validate(fixture(), extra)
        self.assertTrue(any("pre-parsed" in e or "bpm_raw" in e for e in errors), errors)

    def test_title_mismatch_fails(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0]["title"] = "Not The Flag"
        errors = validate(fixture(), extra)
        self.assertTrue(any("title does not match" in e for e in errors), errors)

    def test_fourth_live_band_fails(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["live_catalog_projects"] = [
            "Rad Dad",
            "Stalemate",
        ]
        errors = validate(fixture(), extra)
        self.assertTrue(any("fourth live band" in e for e in errors), errors)

    def test_storyliner_as_consumer_fails(self):
        extra = extras_ok()
        extra["app_api"]["primary_consumer"] = "StoryLiner"
        errors = validate(fixture(), extra)
        self.assertTrue(any("promo only" in e or "StoryBoard" in e for e in errors), errors)

    def test_yes_gate_with_cowriter_fails(self):
        cat = fixture()
        cat["songs"].append(
            song(
                "JS-0998",
                "Shared Tune",
                writers=["Jeff Story", "Greg Baldia"],
            )
        )
        cat["original_song_entities"] = 6
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(
            any("JS-0998" in e and "writers=['Jeff Story']" in e for e in errors),
            errors,
        )

    def test_score_bool_fails(self):
        cat = fixture()
        cat["songs"][0]["potential"] = True
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("potential=True" in e for e in errors), errors)

    def test_score_string_fails(self):
        cat = fixture()
        cat["songs"][0]["readiness"] = "90"
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("readiness='90'" in e for e in errors), errors)

    def test_live_presence_incomplete_fails(self):
        cat = fixture()
        cat["songs"][0]["live_presence"] = [{"band": "Rad Dad"}]
        errors = validate(cat, extras_ok(cat))
        self.assertTrue(any("band and date" in e for e in errors), errors)

    def test_setlist_ready_unknown_id_fails(self):
        extra = extras_ok()
        extra["app_api"]["setlist_ready"].append({"id": "JS-9999", "title": "Nope"})
        errors = validate(fixture(), extra)
        self.assertTrue(any("unknown id" in e for e in errors), errors)

    def test_setlist_ready_non_original_fails(self):
        extra = extras_ok()
        extra["app_api"]["setlist_ready"].append(
            {"id": "JS-0107", "title": "Blue Skies Fade", "project": "Stalemate", "key": "A"}
        )
        extra["app_api"]["setlist_ready_default_import"] = []
        errors = validate(fixture(), extra)
        self.assertTrue(any("not an original" in e for e in errors), errors)

    def test_invented_default_live_setlist_fails(self):
        extra = extras_ok()
        extra["app_api"]["setlist_ready_default_import"] = [
            {"id": "ST-0001", "title": "Turn Over The Flag"}
        ]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("not an invented setlist" in e or "invents ids" in e for e in errors),
            errors,
        )

    def test_missing_vm_matches_fails_closed(self):
        extra = extras_ok()
        extra["vm_matches"] = None
        errors = validate(fixture(), extra)
        self.assertTrue(any("vm_matches.json is missing" in e for e in errors), errors)

    def test_old_schema_version_fails(self):
        extra = extras_ok()
        extra["app_api"]["schema_version"] = 2
        errors = validate(fixture(), extra)
        self.assertTrue(any("schema_version must be 3" in e for e in errors), errors)

    def test_merge_key_vault_id_lie_fails(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["merge_key"] = "vault_id"
        errors = validate(fixture(), extra)
        self.assertTrue(any("catalog_import_v1" in e for e in errors), errors)

    def test_missing_source_key_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0].pop("source_key")
        errors = validate(fixture(), extra)
        self.assertTrue(any("source_key" in e for e in errors), errors)

    def test_missing_bpm_raw_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0].pop("bpm_raw")
        errors = validate(fixture(), extra)
        self.assertTrue(any("bpm_raw" in e for e in errors), errors)

    def test_missing_default_live_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("storyboard_default_live")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.storyboard_default_live is required" in e for e in errors),
            errors,
        )

    def test_storyboard_reads_must_match_importer(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["reads"] = ["id", "title"]
        errors = validate(fixture(), extra)
        self.assertTrue(any("storyboard.reads" in e for e in errors), errors)

    def test_missing_vault_ref_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0].pop("vault_ref")
        errors = validate(fixture(), extra)
        self.assertTrue(any("vault_ref" in e for e in errors), errors)

    def test_missing_bpm_int_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0].pop("bpm_int")
        errors = validate(fixture(), extra)
        self.assertTrue(any("bpm_int" in e for e in errors), errors)

    def test_missing_played_live_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0].pop("played_live")
        errors = validate(fixture(), extra)
        self.assertTrue(any("played_live" in e for e in errors), errors)

    def test_missing_booker_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("storyboard_booker")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.storyboard_booker is required" in e for e in errors),
            errors,
        )

    def test_does_not_read_cannot_hide_bpm_int(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["does_not_read"] = list(
            extra["app_api"]["storyboard"]["does_not_read"]
        ) + ["bpm_int"]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("must not claim bpm_int" in e for e in errors),
            errors,
        )

    def test_does_not_read_cannot_hide_import_scope(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["does_not_read"] = list(
            extra["app_api"]["storyboard"]["does_not_read"]
        ) + ["import_scope"]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("must not claim import_scope" in e for e in errors),
            errors,
        )

    def test_field_map_must_match_live_vault_map(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["field_map"]["sourceKey"] = "vault_id"
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("VAULT_STORYBOARD_FIELD_MAP" in e or "sourceKey" in e for e in errors),
            errors,
        )

    def test_inspected_must_name_storyboard_6(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["inspected"] = "2026-08-23 after StoryBoard #5"
        errors = validate(fixture(), extra)
        self.assertTrue(any("StoryBoard #6" in e for e in errors), errors)

    def test_default_setlist_name_must_be_vault_default_live(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["default_live_setlist_name"] = (
            VAULT_SETLIST_READY_SETLIST_NAME
        )
        extra["app_api"]["storyboard"]["setlist"]["default_import_name"] = (
            VAULT_SETLIST_READY_SETLIST_NAME
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("Vault default-live" in e for e in errors),
            errors,
        )

    def test_missing_parked_named_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("storyboard_default_live_parked_named")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any(
                "counts.storyboard_default_live_parked_named is required" in e
                for e in errors
            ),
            errors,
        )

    def test_hidden_parked_named_default_live_fails(self):
        cat = fixture()
        cat["songs"][0]["live_presence"] = [{"band": "Rad Dad", "date": "2026-05"}]
        extra = extras_ok(cat)
        extra["app_api"]["storyboard"]["default_live_parked_named_ids"] = []
        extra["app_api"]["counts"]["storyboard_default_live_parked_named"] = 0
        errors = validate(cat, extra)
        self.assertTrue(
            any("parked-named" in e or "current-artist" in e for e in errors),
            errors,
        )

    def test_project_name_looks_parked_matches_importer(self):
        self.assertTrue(project_name_looks_parked("Stalemate"))
        self.assertTrue(project_name_looks_parked("Trailer Swift"))
        self.assertTrue(project_name_looks_parked("Something Dirty"))
        self.assertTrue(
            project_name_looks_parked("Something Dirty / Stalemate / Rad Dad")
        )
        self.assertFalse(project_name_looks_parked("Jeff Story"))
        self.assertFalse(project_name_looks_parked("Rad Dad"))
        self.assertEqual(
            vault_setlist_identity(True)["name"],
            VAULT_DEFAULT_LIVE_SETLIST_NAME,
        )
        self.assertEqual(
            vault_setlist_identity(False)["name"],
            VAULT_SETLIST_READY_SETLIST_NAME,
        )
        self.assertEqual(
            PARKED_NAMED_IN_DEFAULT_LIVE_WARNING,
            (
                "Published default-live includes songs whose Vault project is a "
                "parked catalog name. They stay on the current artist — not a "
                "fourth live band."
            ),
        )

    def test_missing_default_import_from_fails(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["setlist"].pop("default_import_from")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("default_import_from" in e for e in errors),
            errors,
        )

    def test_empty_published_slice_with_default_live_stamps_fails(self):
        cat = fixture()
        cat["songs"][0]["artist_project"] = "Jeff Story"
        extra = extras_ok(cat)
        extra["app_api"]["setlist_ready_default_import"] = []
        extra["app_api"]["counts"]["setlist_ready_default_import"] = 0
        extra["app_api"]["counts"]["storyboard_default_live"] = 0
        extra["app_api"]["songs"][0]["import_scope"] = "default_live"
        errors = validate(cat, extra)
        self.assertTrue(
            any(
                "empty" in e and ("default_live" in e or "published" in e)
                for e in errors
            ),
            errors,
        )

    def test_published_slice_row_must_be_default_live(self):
        cat = fixture()
        cat["songs"][0]["artist_project"] = "Jeff Story"
        extra = extras_ok(cat)
        extra["app_api"]["setlist_ready_default_import"][0]["import_scope"] = (
            "parked_catalog"
        )
        errors = validate(cat, extra)
        self.assertTrue(
            any("import_scope=default_live" in e for e in errors),
            errors,
        )

    def test_missing_setlist_ready_default_import_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("setlist_ready_default_import")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any(
                "counts.setlist_ready_default_import is required" in e
                for e in errors
            ),
            errors,
        )

    def test_missing_setlist_ready_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("setlist_ready")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.setlist_ready is required" in e for e in errors),
            errors,
        )

    def test_stale_setlist_ready_count_fails(self):
        extra = extras_ok()
        extra["app_api"]["counts"]["setlist_ready"] = 0
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.setlist_ready=" in e and "expected" in e for e in errors),
            errors,
        )

    def test_setlist_ready_count_cannot_conflate_with_default_live(self):
        """Hand-edit must not make the 5 keyed originals look like the 1 live row."""
        cat = fixture()
        cat["songs"][0]["artist_project"] = "Jeff Story"
        extra = extras_ok(cat)
        extra["app_api"]["counts"]["setlist_ready"] = extra["app_api"]["counts"][
            "storyboard_default_live"
        ]
        errors = validate(cat, extra)
        self.assertTrue(
            any(
                "counts.setlist_ready" in e
                and ("expected" in e or "must not equal the default-live" in e)
                for e in errors
            ),
            errors,
        )

    def test_setlist_names_must_stay_distinct(self):
        self.assertNotEqual(
            VAULT_DEFAULT_LIVE_SETLIST_NAME,
            VAULT_SETLIST_READY_SETLIST_NAME,
        )
        extra = extras_ok()
        extra["app_api"]["storyboard"]["setlist_ready_setlist_name"] = (
            VAULT_DEFAULT_LIVE_SETLIST_NAME
        )
        extra["app_api"]["storyboard"]["setlist"]["opt_in_name"] = (
            VAULT_DEFAULT_LIVE_SETLIST_NAME
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any(
                "distinct" in e or "Vault setlist-ready" in e
                for e in errors
            ),
            errors,
        )

    def test_unrecognized_import_scope_fails(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0]["import_scope"] = "rad_dad_only"
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("not a StoryBoard-recognized scope" in e for e in errors),
            errors,
        )

    def test_zero_default_live_count_when_planner_keeps_songs_fails(self):
        cat = fixture()
        cat["songs"][0]["artist_project"] = "Jeff Story"
        extra = extras_ok(cat)
        extra["app_api"]["counts"]["storyboard_default_live"] = 0
        extra["app_api"]["setlist_ready_default_import"] = []
        extra["app_api"]["songs"][0]["import_scope"] = "not_live_band"
        errors = validate(cat, extra)
        self.assertTrue(
            any("default_live" in e and ("lie" in e or "expected" in e) for e in errors),
            errors,
        )

    def test_setlist_ready_drop_fails(self):
        extra = extras_ok()
        extra["app_api"]["setlist_ready"] = extra["app_api"]["setlist_ready"][:-1]
        errors = validate(fixture(), extra)
        self.assertTrue(any("invent or drop setlist rows" in e for e in errors), errors)

    def test_played_live_over_schema_max_fails(self):
        extra = extras_ok()
        extra["app_api"]["songs"][0]["played_live"] = [f"Band ({i})" for i in range(51)]
        errors = validate(fixture(), extra)
        self.assertTrue(any("played_live exceeds" in e for e in errors), errors)

    def test_decide_skips_cover_even_with_rad_dad_play(self):
        decision = decide_vault_song(
            {
                "id": "ST-0002",
                "project": "Stalemate",
                "is_original": False,
                "played_live": ["Rad Dad (2026-05)"],
            },
            has_ready_list=True,
            in_ready_set=True,
        )
        self.assertFalse(decision.include)
        self.assertEqual(decision.reason, "cover_not_active")

    def test_decide_keeps_parked_original_with_rad_dad_play(self):
        decision = decide_vault_song(
            {
                "id": "ST-0014",
                "project": "Stalemate",
                "is_original": True,
                "played_live": ["Rad Dad (2026-05)"],
            },
            has_ready_list=True,
            in_ready_set=True,
        )
        self.assertTrue(decision.include)

    def test_live_planner_empty_published_slice_stays_empty(self):
        """StoryBoard #5: present-but-empty setlist_ready_default_import wins."""
        songs = [
            {
                "id": "JS-0001",
                "project": "Jeff Story",
                "is_original": True,
                "import_scope": "not_live_band",
                "played_live": ["Rad Dad (2026-05)"],
            },
            {
                "id": "ST-0001",
                "project": "Stalemate",
                "is_original": True,
                "import_scope": "parked_catalog",
            },
        ]
        planned = {
            rec["id"]
            for rec, decision in live_default_decisions(
                songs, {"JS-0001", "ST-0001"}, set()
            )
            if decision.include
        }
        self.assertEqual(planned, set())

    def test_live_planner_prefers_published_ids(self):
        songs = [
            {
                "id": "JS-0128",
                "project": "Jeff Story",
                "is_original": True,
                "import_scope": "default_live",
            },
            {
                "id": "ST-0014",
                "project": "Stalemate",
                "is_original": True,
                "import_scope": "default_live",
                "played_live": ["Rad Dad (2026-05)"],
            },
            {
                "id": "ST-0001",
                "project": "Stalemate",
                "is_original": True,
                "import_scope": "parked_catalog",
            },
        ]
        planned = {
            rec["id"]
            for rec, decision in live_default_decisions(
                songs, {"JS-0128", "ST-0014", "ST-0001"}, {"JS-0128", "ST-0014"}
            )
            if decision.include
        }
        self.assertEqual(planned, {"JS-0128", "ST-0014"})

    def test_catalog_import_scope_honors_declared_not_live(self):
        self.assertEqual(catalog_import_scope("Jeff Story"), "default_live")
        self.assertEqual(
            catalog_import_scope("Jeff Story", "not_live_band"),
            "not_live_band",
        )
        self.assertEqual(recognized_import_scope("travis_books"), "travis_books")
        self.assertIsNone(recognized_import_scope("rad_dad_only"))

    def test_real_repo_catalog_passes(self):
        """Live spine must stay green after this pass — no weakening the check."""
        from validate_catalog import load_repo

        cat, extra = load_repo(ROOT)
        errors = validate(cat, extra)
        self.assertEqual(errors, [], errors)
        api = extra["app_api"]
        default_order = [row["id"] for row in api["setlist_ready_default_import"]]
        default_ids = set(default_order)
        ready_ids = {row["id"] for row in api["setlist_ready"]}
        self.assertEqual(len(default_ids), 20)
        self.assertEqual(api["counts"]["setlist_ready_default_import"], 20)
        self.assertEqual(api["counts"]["storyboard_default_live"], 20)
        self.assertEqual(len(ready_ids), 40)
        self.assertEqual(api["counts"]["setlist_ready"], 40)
        self.assertNotEqual(
            api["counts"]["setlist_ready"],
            api["counts"]["storyboard_default_live"],
        )
        self.assertNotEqual(
            api["storyboard"]["default_live_setlist_name"],
            api["storyboard"]["setlist_ready_setlist_name"],
        )
        self.assertEqual(api["schema_version"], 3)
        self.assertEqual(api["storyboard"]["field_map"], dict(VAULT_STORYBOARD_FIELD_MAP))
        self.assertEqual(api["storyboard"]["booker_policy"], "travis_books")
        self.assertIn("import_scope", api["storyboard"]["reads"])
        self.assertNotIn("import_scope", api["storyboard"]["does_not_read"])
        self.assertTrue(api["storyboard"]["prefers_published_default_import"])
        self.assertIn("JS-0128", default_ids)
        self.assertIn("ST-0014", default_ids)
        self.assertNotIn("ST-0001", default_ids)
        self.assertNotIn("ST-0002", default_ids)
        parked_named = parked_named_default_live_ids(api["songs"], default_order)
        self.assertEqual(set(parked_named), {"ST-0014", "JS-0001"})
        self.assertEqual(api["storyboard"]["default_live_parked_named_ids"], parked_named)
        self.assertEqual(api["counts"]["storyboard_default_live_parked_named"], 2)
        self.assertEqual(
            api["storyboard"]["default_live_setlist_name"],
            VAULT_DEFAULT_LIVE_SETLIST_NAME,
        )
        self.assertTrue(
            api["storyboard"]["parked_named_in_default_live_stay_current_artist"]
        )
        self.assertIn("StoryBoard #6", api["storyboard"]["inspected"])
        live_ids = {
            rec["id"]
            for rec, decision in live_default_decisions(
                api["songs"], ready_ids, default_ids
            )
            if decision.include
        }
        self.assertEqual(live_ids, default_ids)


if __name__ == "__main__":
    unittest.main()
