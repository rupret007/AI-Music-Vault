#!/usr/bin/env python3
"""Regression tests for scripts/validate_catalog.py — fail closed on broken catalogs."""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from catalog_surface import (  # noqa: E402
    ON_DECK_NOTE,
    SURFACE_STAGE_REPLACEMENT,
    SURFACE_SUBTITLE,
    catalog_surface_admits_not_official_set,
    catalog_surface_claims_official_set,
    dashboard_displays_owner_audio_index,
    dashboard_exposes_song_work,
    dashboard_opens_owner_audio,
    catalog_workspace_uses_vault_framing,
    overlay_feed_scopes,
    played_badge_label,
    surface_row_claims_official_set,
    surface_stage_label,
)
from export_app_api import build_payload  # noqa: E402
from export_catalog_csv import (  # noqa: E402
    csv_rows_from_catalog,
    covers_rows_from_catalog,
)
from storyboard_contract import (  # noqa: E402
    BAND_OPERATIONS_IMPORT,
    LOCAL_JSON_ONLY,
    NEVER_AUTO_POST,
    PARKED_NAMED_IN_DEFAULT_LIVE_WARNING,
    REMOTE_CATALOG_URLS,
    SHOW_NIGHT_FEED_IMPORT_ERROR,
    SHOW_NIGHT_NOT_IN_VAULT,
    SHOW_NIGHT_OFFICIAL_SET_IMPORT_ERROR,
    SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME,
    VAULT_DEFAULT_LIVE_SETLIST_NAME,
    VAULT_IMPORT_FILE,
    VAULT_SETLIST_READY_SETLIST_NAME,
    VAULT_STORYBOARD_FIELD_MAP,
    bind_official_set_dump,
    catalog_import_scope,
    catalog_locator_looks_remote,
    decide_vault_song,
    import_scope,
    live_default_decisions,
    parked_named_default_live_ids,
    parse_bpm,
    parse_local_catalog_json,
    official_set_write_allowed,
    planned_vault_titles,
    project_name_looks_parked,
    public_suggestion_has_official_set_mutation,
    public_suggestion_writer_is_canonical,
    recognized_import_scope,
    show_night_bind_title,
    show_night_catalog_payload_error,
    show_night_payload_looks_like_official_set_dump,
    show_night_payload_looks_like_suggestion,
    spine_default_plan_ids,
    storyboard_parse_bpm,
    vault_payload_looks_like_spine,
    vault_payload_validation_error,
    VAULT_FEED_IMPORT_ERROR,
    VAULT_SPINE_IMPORT_ERROR,
    vault_setlist_identity,
    vault_skip_by_title,
)
from validate_catalog import (  # noqa: E402
    ACTIVE_LANES,
    PROTECTED_LANES,
    YES_GATE,
    apps_md_admits_catalog_not_official_set,
    apps_md_admits_empty_runner,
    apps_md_admits_official_set_dump,
    apps_md_admits_show_night_owner_only,
    apps_md_admits_spine_reject,
    apps_md_claims_catalog_is_official_set,
    apps_md_claims_feed_writes_official_set,
    apps_md_claims_hosted_ci,
    apps_md_claims_spine_still_accepted,
    apps_md_claims_suggestion_dump_is_official_set,
    catalog_ok_report,
    catalog_ok_report_leaks_published_ids,
    duplicate_session_log_headings,
    latest_session_log_has_continuation,
    latest_session_log_section,
    module_doc_claims_hosted_ci,
    public_doc_has_collaborator_map,
    public_doc_has_live_lane_titles,
    public_doc_has_other_catalog_titles,
    public_doc_has_protected_opus_names,
    public_doc_has_published_ids,
    public_facing_doc_errors,
    session_log_h2_headings,
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


APPS_MD_HONEST = (
    "Local python3 scripts/validate_catalog.py fails closed "
    "if this file drifts. Hosted catalog-validate may be a "
    "0-step empty-runner — not a catalog fail. "
    "StoryBoard rejects the spine as an import. "
    "Show Night official set is owner-only. "
    "StoryBoard binds a local official-set dump as "
    "Rad Dad — official set. Show Night is the live set surface. "
    "Catalog rows are not the official set. Show Night owns official sets.\n"
)

OFFICIAL_SET_DUMP = {
    "show": {
        "title": "Example Night",
        "venue": "Example Room",
        "date": "Saturday, September 19, 2026",
    },
    "sets": [
        {"slug": "stalemate", "title": "Stalemate"},
        {"slug": "rad-dad", "title": "Rad Dad"},
    ],
    "songs": [
        {
            "setSlug": "stalemate",
            "position": 1,
            "title": "Parked Demo",
            "isOriginal": True,
        },
        {
            "setSlug": "rad-dad",
            "position": 1,
            "title": "Harbor Lights →",
            "isOriginal": True,
            "transition": True,
        },
        {
            "setSlug": "rad-dad",
            "position": 2,
            "title": "Cover Example",
            "isOriginal": False,
        },
    ],
}

SUGGESTION_DUMP = {
    "suggestions": [
        {
            "title": "Cover Example",
            "artist": "Example Artist",
            "notes": "please add this",
        }
    ]
}

LEGACY_SHOW_JSON = {
    "event": {"name": "Example Night"},
    "radDadSet": [
        {"number": 1, "song": "Harbor Lights →", "transition": True},
        {"number": 2, "song": "Cover Example"},
    ],
    "guestSets": [
        {"name": "Stalemate", "songs": [{"number": 1, "song": "Parked Demo"}]},
    ],
}


def extras_ok(cat=None):
    cat = cat or fixture()
    return {
        "app_api": build_payload(cat),
        "catalog_csv": csv_rows_from_catalog(cat),
        "covers_csv": covers_rows_from_catalog(cat),
        "version_chains": {},
        "momentum": [],
        "vm_matches": {"ST-0001": ["uid-a", "uid-b"]},
        "priority_queue": (
            "ACTIVE (max 3 — unchanged)\n"
            "ST-0001 Turn Over The Flag\n"
            "ST-0004 Manic\n"
            "ST-0009 Long Long Drive\n"
        ),
        "session_log": (
            "# Session Log\n\n"
            "## usable catalog local-JSON — 2026-08-26 (Cloud Agent, no audio)\n\n"
            "once\n\n"
            "### Next continuation point\n\n"
            "standing Jeff-owned items unchanged\n"
        ),
        "dashboard_html": (
            "Catalog v1.6 · Turn Over The Flag · Manic · Long Long Drive · "
            "It's Alright · Blue Skies Fade · data/app_api.json · "
            "Show Night owns official sets · catalog rows are not the live set "
            'id="work" Copy work card function songWorkKind( '
            'function buildSongWorkCard( data-copy-work '
            'data-open-song="ST-0001" id="workSession" '
            'id="workStarts" id="advancedFilters" '
            'function openWork( function updateWorkSessionState( '
            'function latestMemoForSong( data-open-work= '
            'Start a work session More filters Sit-down'
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

    def test_missing_catalog_csv_fails_closed(self):
        extra = extras_ok()
        extra["catalog_csv"] = None
        errors = validate(fixture(), extra)
        self.assertTrue(any("master_catalog.csv is required" in e for e in errors), errors)

    def test_stale_catalog_csv_fails_closed(self):
        extra = extras_ok()
        extra["catalog_csv"] = extra["catalog_csv"][:-1]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("master_catalog.csv drifted" in e for e in errors),
            errors,
        )

    def test_covers_csv_drift_fails_closed(self):
        cat = fixture()
        cat["covers"] = [
            {
                "title": "Cover Example",
                "original_artist": "Someone Else",
                "context": "setlist",
                "classification": "cover",
            }
        ]
        extra = extras_ok(cat)
        extra["covers_csv"] = []
        errors = validate(cat, extra)
        self.assertTrue(
            any("covers_reference.csv drifted" in e for e in errors),
            errors,
        )

    def test_version_chain_unknown_id_fails_closed(self):
        extra = extras_ok()
        extra["version_chains"] = {"JS-9999": {"files": []}}
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("version_chains.json points at unknown" in e for e in errors),
            errors,
        )

    def test_momentum_unknown_id_fails_closed(self):
        extra = extras_ok()
        extra["momentum"] = [{"id": "JS-9999", "title": "Not A Song"}]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("momentum.json points at unknown" in e for e in errors),
            errors,
        )

    def test_momentum_title_mismatch_fails_closed(self):
        extra = extras_ok()
        extra["momentum"] = [{"id": "ST-0001", "title": "Wrong Title", "momentum": 10}]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("momentum.json ST-0001 title drifted" in e for e in errors),
            errors,
        )

    def test_momentum_score_drift_is_not_a_catalog_fail(self):
        """Live-set floors may lift spine momentum without rewriting momentum.json."""
        extra = extras_ok()
        extra["momentum"] = [
            {"id": "ST-0001", "title": "Turn Over The Flag", "momentum": 10}
        ]
        self.assertEqual(validate(fixture(), extra), [])

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

    def test_inspected_must_name_storyboard_12(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["inspected"] = "2026-08-26 after StoryBoard #9"
        errors = validate(fixture(), extra)
        self.assertTrue(any("StoryBoard #12" in e for e in errors), errors)

    def test_inspected_must_name_storyboard_16(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["inspected"] = (
            "2026-08-26 after StoryBoard #12 local JSON only"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(any("StoryBoard #16" in e for e in errors), errors)

    def test_missing_local_json_only_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["local_json_only"] = False
        extra["app_api"]["storyboard"]["ops"]["local_json_only"] = False
        errors = validate(fixture(), extra)
        self.assertTrue(any("local_json_only" in e for e in errors), errors)

    def test_claiming_remote_catalog_urls_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["remote_catalog_urls"] = True
        extra["app_api"]["storyboard"]["ops"]["remote_catalog_urls"] = True
        errors = validate(fixture(), extra)
        self.assertTrue(any("remote_catalog_urls" in e for e in errors), errors)

    def test_missing_band_operations_import_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["band_operations_import"] = "fetch from GitHub"
        extra["app_api"]["storyboard"]["ops"]["band_operations_import"] = (
            "fetch from GitHub"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(any("band_operations_import" in e for e in errors), errors)

    def test_remote_locator_on_feed_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["catalogUrl"] = "https://example.invalid/app_api.json"
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("remote catalog locator" in e or "local JSON" in e for e in errors),
            errors,
        )

    def test_catalog_locator_looks_remote_matches_storyboard(self):
        self.assertTrue(catalog_locator_looks_remote("https://example.invalid/feed"))
        self.assertTrue(catalog_locator_looks_remote("//cdn.example.invalid/feed"))
        self.assertTrue(
            catalog_locator_looks_remote({"url": "https://example.invalid/feed"})
        )
        self.assertFalse(catalog_locator_looks_remote("data/app_api.json"))
        self.assertFalse(catalog_locator_looks_remote({"songs": []}))

    def test_parse_local_catalog_json_rejects_url(self):
        with self.assertRaises(ValueError):
            parse_local_catalog_json("https://example.invalid/app_api.json")
        with self.assertRaises(ValueError):
            parse_local_catalog_json(
                '{"catalogUrl": "https://example.invalid/app_api.json"}'
            )
        self.assertIsNone(parse_local_catalog_json("   "))
        self.assertEqual(parse_local_catalog_json('{"songs": []}'), {"songs": []})

    def test_missing_never_auto_post_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["never_auto_post"] = False
        extra["app_api"]["storyboard"]["ops"]["never_auto_post"] = False
        errors = validate(fixture(), extra)
        self.assertTrue(any("never_auto_post" in e for e in errors), errors)

    def test_claiming_spine_is_the_import_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["master_catalog_is_not_the_import"] = False
        extra["app_api"]["storyboard"]["import_file"] = "data/master_catalog.json"
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("master_catalog" in e or "import_file" in e for e in errors),
            errors,
        )

    def test_claiming_spine_is_accepted_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["master_catalog_is_rejected"] = False
        extra["app_api"]["storyboard"]["ops"]["master_catalog_is_rejected"] = False
        errors = validate(fixture(), extra)
        self.assertTrue(any("master_catalog_is_rejected" in e for e in errors), errors)

    def test_missing_show_night_does_not_expand_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["show_night_does_not_expand_vault"] = False
        extra["app_api"]["storyboard"]["ops"]["show_night_does_not_expand_vault"] = (
            False
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("show_night_does_not_expand_vault" in e for e in errors),
            errors,
        )

    def test_missing_show_night_owner_only_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["show_night_official_set_is_owner_only"] = False
        extra["app_api"]["storyboard"]["ops"]["show_night_official_set_is_owner_only"] = (
            False
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("show_night_official_set_is_owner_only" in e for e in errors),
            errors,
        )

    def test_missing_public_suggestion_cannot_mutate_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"][
            "show_night_public_suggestions_cannot_mutate_set"
        ] = False
        extra["app_api"]["storyboard"]["ops"][
            "show_night_public_suggestions_cannot_mutate_set"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any(
                "show_night_public_suggestions_cannot_mutate_set" in e
                for e in errors
            ),
            errors,
        )

    def test_claiming_feed_is_a_show_night_writer_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["vault_feed_is_not_a_show_night_writer"] = False
        extra["app_api"]["storyboard"]["ops"][
            "vault_feed_is_not_a_show_night_writer"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("vault_feed_is_not_a_show_night_writer" in e for e in errors),
            errors,
        )

    def test_inspected_without_show_night_owner_only_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["inspected"] = (
            "2026-08-27 after StoryBoard #16 "
            "(StoryBoard #12 local JSON; spine rejected)"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("Show Night #1" in e or "owner-only" in e for e in errors),
            errors,
        )

    def test_missing_official_set_dump_bind_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["show_night_binds_official_set_dump"] = False
        extra["app_api"]["storyboard"]["ops"][
            "show_night_binds_official_set_dump"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("show_night_binds_official_set_dump" in e for e in errors),
            errors,
        )

    def test_missing_guest_sets_opt_in_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["show_night_guest_sets_stay_opt_in"] = False
        extra["app_api"]["storyboard"]["ops"][
            "show_night_guest_sets_stay_opt_in"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("show_night_guest_sets_stay_opt_in" in e for e in errors),
            errors,
        )

    def test_inspected_without_storyboard_19_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["inspected"] = (
            "2026-08-27 after StoryBoard #16 "
            "(StoryBoard #12 local JSON; spine rejected; "
            "Show Night #1/#2 official set owner-only)"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(any("StoryBoard #19" in e for e in errors), errors)

    def test_missing_catalog_not_official_set_flag_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["catalog_rows_are_not_the_official_set"] = False
        extra["app_api"]["storyboard"]["ops"][
            "catalog_rows_are_not_the_official_set"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("catalog_rows_are_not_the_official_set" in e for e in errors),
            errors,
        )

    def test_missing_default_live_not_official_set_flag_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"][
            "vault_default_live_is_not_the_official_set"
        ] = False
        extra["app_api"]["storyboard"]["ops"][
            "vault_default_live_is_not_the_official_set"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("vault_default_live_is_not_the_official_set" in e for e in errors),
            errors,
        )

    def test_inspected_without_storyboard_20_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["inspected"] = (
            "2026-08-27 after StoryBoard #19 "
            "(StoryBoard #12 local JSON; StoryBoard #16 spine rejected; "
            "Show Night #1/#2 official set owner-only; "
            "official-set dump binds Rad Dad — official set; "
            "Show Night #3 live set surface)"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(any("StoryBoard #20" in e for e in errors), errors)
        self.assertTrue(
            any("catalog rows are not the official set" in e for e in errors),
            errors,
        )

    def test_dump_bind_lock_still_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["storyboard"]["show_night_binds_official_set_dump"] = False
        extra["app_api"]["storyboard"]["ops"][
            "show_night_binds_official_set_dump"
        ] = False
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("show_night_binds_official_set_dump" in e for e in errors),
            errors,
        )

    def test_harbor_lights_default_live_is_not_official_set(self):
        rows = overlay_feed_scopes(
            [{"id": "VAULT-1", "t": "Harbor Lights"}],
            {
                "songs": [
                    {
                        "id": "VAULT-1",
                        "title": "Harbor Lights",
                        "import_scope": "default_live",
                    }
                ]
            },
        )
        self.assertEqual(rows[0]["scope"], "default_live")
        self.assertIn("not official set", rows[0]["scope_label"])
        self.assertFalse(surface_row_claims_official_set(rows[0]))
        self.assertEqual(played_badge_label("2024-04-26"), "played 2024-04-26")
        self.assertFalse(
            catalog_surface_claims_official_set(rows[0]["scope_label"])
        )

    def test_official_set_dump_plus_vault_stays_catalog_framed(self):
        leftover = catalog_workspace_uses_vault_framing(
            {
                "source": "mixed",
                "vaultSongCount": 3,
                "showNightSongCount": 0,
                "demoSongCount": 0,
                "manualSongCount": 0,
            }
        )
        self.assertTrue(leftover)
        self.assertFalse(
            catalog_workspace_uses_vault_framing(
                {
                    "source": "mixed",
                    "vaultSongCount": 3,
                    "showNightSongCount": 1,
                    "demoSongCount": 0,
                    "manualSongCount": 0,
                }
            )
        )
        self.assertIn("app_api.json", SURFACE_SUBTITLE)
        self.assertIn("not the live set", SURFACE_SUBTITLE)
        self.assertIn("not the official set", ON_DECK_NOTE)

    def test_dashboard_in_the_live_set_fails_closed(self):
        extra = extras_ok()
        extra["dashboard_html"] = (
            extra["dashboard_html"] + " · It's Alright — in the live set"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("catalog rows are the live set" in e for e in errors),
            errors,
        )
        self.assertTrue(
            catalog_surface_claims_official_set(extra["dashboard_html"])
        )

    def test_dashboard_current_live_set_reprint_fails_closed(self):
        extra = extras_ok()
        extra["dashboard_html"] = (
            extra["dashboard_html"]
            + " · written + IN CURRENT LIVE SET (Oct 2025 practice)"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("IN CURRENT LIVE SET" in e for e in errors),
            errors,
        )
        self.assertTrue(
            catalog_surface_claims_official_set(extra["dashboard_html"])
        )

    def test_surface_stage_label_sanitizes_current_live_set(self):
        raw = (
            "written + IN CURRENT LIVE SET (Oct 2025 practice) "
            "— unrecorded, no lyric doc"
        )
        sanitized = surface_stage_label(raw)
        self.assertIn(SURFACE_STAGE_REPLACEMENT, sanitized)
        self.assertIn("Oct 2025 practice", sanitized)
        self.assertIn("unrecorded, no lyric doc", sanitized)
        self.assertFalse(catalog_surface_claims_official_set(sanitized))
        self.assertIn("not the official set", sanitized)
        self.assertFalse(catalog_surface_claims_official_set("not the live set"))
        self.assertTrue(catalog_surface_claims_official_set("in current live set"))
        self.assertTrue(catalog_surface_claims_official_set("in the current live set"))
        self.assertEqual(
            surface_stage_label("written — catalog only"),
            "written — catalog only",
        )

    def test_dashboard_owner_audio_open_fails_closed(self):
        extra = extras_ok()
        extra["dashboard_html"] = extra["dashboard_html"] + '<audio src="take.wav"></audio>'
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("must not open Logic keys, WAVs, or audio" in e for e in errors),
            errors,
        )
        self.assertTrue(dashboard_opens_owner_audio(extra["dashboard_html"]))

    def test_dashboard_without_song_work_fails_closed(self):
        extra = extras_ok()
        extra["dashboard_html"] = extra["dashboard_html"].replace(
            'id="work"', ""
        ).replace("Copy work card", "")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("write/produce/listen sit-down" in e for e in errors),
            errors,
        )
        self.assertFalse(dashboard_exposes_song_work(extra["dashboard_html"]))

    def test_dashboard_owner_audio_index_fails_closed(self):
        extra = extras_ok()
        extra["dashboard_html"] = extra["dashboard_html"] + "<h4>Known assets</h4>"
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("must not display Logic/WAV/best_source locators" in e for e in errors),
            errors,
        )
        self.assertTrue(dashboard_displays_owner_audio_index(extra["dashboard_html"]))

    def test_dashboard_without_feed_reuse_fails_closed(self):
        extra = extras_ok()
        extra["dashboard_html"] = (
            "Catalog v1.6 · Turn Over The Flag · Manic · Long Long Drive · "
            "It's Alright · Blue Skies Fade"
        )
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("reuse data/app_api.json" in e for e in errors),
            errors,
        )
        self.assertFalse(
            catalog_surface_admits_not_official_set(extra["dashboard_html"])
        )

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

    def test_missing_originals_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("originals")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.originals is required" in e for e in errors),
            errors,
        )

    def test_stale_originals_count_fails(self):
        extra = extras_ok()
        extra["app_api"]["counts"]["originals"] = 0
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.originals=" in e and "expected" in e for e in errors),
            errors,
        )

    def test_originals_count_cannot_conflate_with_setlist_ready(self):
        """Hand-edit must not make 5 originals look like 4 keyed setlist rows."""
        cat = fixture()
        cat["songs"][5]["key"] = ""
        extra = extras_ok(cat)
        extra["app_api"]["counts"]["originals"] = extra["app_api"]["counts"][
            "setlist_ready"
        ]
        errors = validate(cat, extra)
        self.assertTrue(
            any(
                "counts.originals" in e
                and ("expected" in e or "must not equal the setlist-ready" in e)
                for e in errors
            ),
            errors,
        )

    def test_missing_scored_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("scored")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.scored is required" in e for e in errors),
            errors,
        )

    def test_stale_scored_count_fails(self):
        extra = extras_ok()
        extra["app_api"]["counts"]["scored"] = 0
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.scored=" in e and "expected" in e for e in errors),
            errors,
        )

    def test_scored_count_cannot_conflate_with_originals(self):
        """Fixture is 6 scored / 5 originals — do not pretend every original is scored."""
        extra = extras_ok()
        extra["app_api"]["counts"]["scored"] = extra["app_api"]["counts"]["originals"]
        errors = validate(fixture(), extra)
        self.assertTrue(
            any(
                "counts.scored" in e
                and ("expected" in e or "must not equal counts.originals" in e)
                for e in errors
            ),
            errors,
        )

    def test_missing_ai_upload_ok_count_fails_closed(self):
        extra = extras_ok()
        extra["app_api"]["counts"].pop("ai_upload_ok")
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.ai_upload_ok is required" in e for e in errors),
            errors,
        )

    def test_stale_ai_upload_ok_count_fails(self):
        extra = extras_ok()
        extra["app_api"]["counts"]["ai_upload_ok"] = 0
        errors = validate(fixture(), extra)
        self.assertTrue(
            any("counts.ai_upload_ok=" in e and "expected" in e for e in errors),
            errors,
        )

    def test_ai_upload_ok_count_cannot_conflate_with_originals(self):
        """A YES fragment is not an original — the counts must stay distinct."""
        cat = fixture()
        cat["songs"].append(
            song(
                "JS-0002",
                "Moonlight Pride sketch",
                classification="original fragment",
            )
        )
        extra = extras_ok(cat)
        extra["app_api"]["counts"]["ai_upload_ok"] = extra["app_api"]["counts"][
            "originals"
        ]
        errors = validate(cat, extra)
        self.assertTrue(
            any(
                "counts.ai_upload_ok" in e
                and ("expected" in e or "must not equal counts.originals" in e)
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

    def test_show_night_does_not_mint_excluded_or_unknown_titles(self):
        songs = [
            {
                "id": "JS-0128",
                "title": "It's Alright",
                "project": "Jeff Story",
                "is_original": True,
                "import_scope": "default_live",
            },
            {
                "id": "ST-0002",
                "title": "Cover Example",
                "project": "Stalemate",
                "is_original": False,
                "import_scope": "cover_not_active",
            },
            {
                "id": "JS-0997",
                "title": "Booker Tune",
                "project": "Travis Story",
                "is_original": True,
                "import_scope": "travis_books",
            },
        ]
        published = {"JS-0128"}
        ready = {"JS-0128"}
        planned = planned_vault_titles(songs, ready, published)
        skip = vault_skip_by_title(songs, ready, published)
        self.assertEqual(
            show_night_bind_title("It's Alright", planned, skip),
            ("bind", "JS-0128"),
        )
        self.assertEqual(
            show_night_bind_title("Cover Example", planned, skip),
            ("skip", "cover_not_active"),
        )
        self.assertEqual(
            show_night_bind_title("Booker Tune", planned, skip),
            ("skip", "travis_books"),
        )
        self.assertEqual(
            show_night_bind_title("Not In Vault", planned, skip),
            ("skip", SHOW_NIGHT_NOT_IN_VAULT),
        )

    def test_public_suggestion_official_set_fields_are_mutations(self):
        self.assertTrue(
            public_suggestion_has_official_set_mutation(
                {"setSlug": "x", "songs": []}
            )
        )
        self.assertTrue(
            public_suggestion_has_official_set_mutation({"order": 1})
        )
        self.assertFalse(
            public_suggestion_has_official_set_mutation(
                {"notes": "x", "addedBy": "x"}
            )
        )
        self.assertFalse(public_suggestion_has_official_set_mutation("x"))

    def test_official_set_write_requires_owner(self):
        self.assertFalse(
            official_set_write_allowed("POST", "/api/show", owner=False)
        )
        self.assertTrue(
            official_set_write_allowed("POST", "/api/show", owner=True)
        )
        self.assertFalse(
            official_set_write_allowed("GET", "/api/show", owner=True)
        )
        self.assertFalse(
            official_set_write_allowed("POST", "/api/suggestions", owner=True)
        )

    def test_one_public_suggestion_writer(self):
        self.assertTrue(public_suggestion_writer_is_canonical("/api/suggestions"))
        self.assertFalse(
            public_suggestion_writer_is_canonical("/api/suggestions/submit")
        )
        self.assertFalse(public_suggestion_writer_is_canonical("/api/show"))

    def test_official_set_dump_binds_rad_dad_only(self):
        """Harbor Lights / Cover Example / Parked Demo fixtures only."""
        self.assertTrue(show_night_payload_looks_like_official_set_dump(OFFICIAL_SET_DUMP))
        self.assertFalse(show_night_payload_looks_like_official_set_dump(LEGACY_SHOW_JSON))
        self.assertFalse(show_night_payload_looks_like_suggestion(OFFICIAL_SET_DUMP))
        self.assertIsNone(show_night_catalog_payload_error(OFFICIAL_SET_DUMP))
        leftover = bind_official_set_dump(OFFICIAL_SET_DUMP)
        self.assertTrue(leftover["ok"])
        self.assertEqual(leftover["official_name"], SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME)
        self.assertEqual(leftover["official_titles"], ["Harbor Lights", "Cover Example"])
        self.assertEqual(leftover["guests"], [])
        self.assertTrue(
            any(
                row["reason"] == "guest_set_skipped" and row["title"] == "Stalemate"
                for row in leftover["skipped"]
            )
        )
        self.assertNotIn("Parked Demo", leftover["official_titles"])

    def test_official_set_dump_with_vault_binds_planned_only(self):
        songs = [
            {
                "id": "RD-0001",
                "title": "Harbor Lights",
                "project": "Rad Dad",
                "is_original": True,
                "import_scope": "default_live",
            },
            {
                "id": "CV-0001",
                "title": "Cover Example",
                "project": "Rad Dad",
                "is_original": False,
                "import_scope": "cover_not_active",
            },
        ]
        published = {"RD-0001"}
        ready = {"RD-0001"}
        planned = planned_vault_titles(songs, ready, published)
        skip = vault_skip_by_title(songs, ready, published)
        leftover = bind_official_set_dump(OFFICIAL_SET_DUMP, planned, skip)
        self.assertTrue(leftover["ok"])
        self.assertEqual(leftover["official_titles"], ["Harbor Lights"])
        self.assertTrue(
            any(
                row["reason"] == "cover_not_active"
                and row["title"] == "Cover Example"
                and row.get("source") == "show_night"
                for row in leftover["skipped"]
            )
        )
        self.assertTrue(
            any(
                row["reason"] == "guest_set_skipped" and row["title"] == "Stalemate"
                for row in leftover["skipped"]
            )
        )
        guests = bind_official_set_dump(
            OFFICIAL_SET_DUMP, planned, skip, include_guest_sets=True
        )
        self.assertTrue(any(guest["name"] == "Stalemate" for guest in guests["guests"]))
        self.assertFalse(
            any(row["reason"] == "guest_set_skipped" for row in guests["skipped"])
        )

    def test_suggestion_dump_is_refused(self):
        self.assertTrue(show_night_payload_looks_like_suggestion(SUGGESTION_DUMP))
        self.assertEqual(
            show_night_catalog_payload_error(SUGGESTION_DUMP),
            SHOW_NIGHT_OFFICIAL_SET_IMPORT_ERROR,
        )
        leftover = bind_official_set_dump(SUGGESTION_DUMP)
        self.assertFalse(leftover["ok"])
        self.assertEqual(leftover["error"], SHOW_NIGHT_OFFICIAL_SET_IMPORT_ERROR)
        self.assertEqual(leftover["official_titles"], [])
        self.assertIsNone(leftover["official_name"])

    def test_legacy_raddadset_still_works(self):
        self.assertFalse(show_night_payload_looks_like_official_set_dump(LEGACY_SHOW_JSON))
        self.assertIsNone(show_night_catalog_payload_error(LEGACY_SHOW_JSON))
        leftover = bind_official_set_dump(LEGACY_SHOW_JSON)
        self.assertTrue(leftover["ok"])
        self.assertEqual(leftover["official_name"], SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME)
        self.assertEqual(leftover["official_titles"], ["Harbor Lights", "Cover Example"])
        self.assertTrue(
            any(
                row["reason"] == "guest_set_skipped" and row["title"] == "Stalemate"
                for row in leftover["skipped"]
            )
        )
        self.assertEqual(
            show_night_catalog_payload_error({"radDadSet": "nope"}),
            SHOW_NIGHT_FEED_IMPORT_ERROR,
        )

    def test_show_night_does_not_fill_empty_published_slice(self):
        songs = [
            {
                "id": "JS-0128",
                "title": "It's Alright",
                "project": "Jeff Story",
                "is_original": True,
                "import_scope": "default_live",
            }
        ]
        planned = planned_vault_titles(songs, {"JS-0128"}, set())
        skip = vault_skip_by_title(songs, {"JS-0128"}, set())
        self.assertEqual(planned, {})
        action, reason = show_night_bind_title("It's Alright", planned, skip)
        self.assertEqual(action, "skip")
        self.assertNotEqual(action, "bind")
        self.assertIn(reason, {"not_setlist_ready", SHOW_NIGHT_NOT_IN_VAULT})

    def test_spine_payload_is_rejected(self):
        """StoryBoard #16 rejects spine shape. No songs are planned."""
        cat = fixture()
        feed = build_payload(cat)
        self.assertTrue(vault_payload_looks_like_spine(cat))
        self.assertFalse(vault_payload_looks_like_spine(feed))
        self.assertEqual(vault_payload_validation_error(cat), VAULT_SPINE_IMPORT_ERROR)
        self.assertIsNone(vault_payload_validation_error(feed))
        self.assertEqual(spine_default_plan_ids(cat["songs"]), [])
        raw_spine_rows = [
            {
                "song_id": "TEST-0001",
                "canonical_title": "Synthetic Test",
                "artist_project": "Rad Dad",
                "classification": "original",
            }
        ]
        self.assertTrue(vault_payload_looks_like_spine(raw_spine_rows))
        self.assertEqual(
            vault_payload_validation_error(raw_spine_rows),
            VAULT_SPINE_IMPORT_ERROR,
        )
        self.assertEqual(
            vault_payload_validation_error([{"id": "TEST-0001", "title": "Synthetic Test"}]),
            VAULT_FEED_IMPORT_ERROR,
        )

    def test_catalog_import_scope_honors_declared_not_live(self):
        self.assertEqual(catalog_import_scope("Jeff Story"), "default_live")
        self.assertEqual(
            catalog_import_scope("Jeff Story", "not_live_band"),
            "not_live_band",
        )
        self.assertEqual(recognized_import_scope("travis_books"), "travis_books")
        self.assertIsNone(recognized_import_scope("rad_dad_only"))

    def test_duplicate_session_log_heading_fails(self):
        extras = extras_ok()
        extras["session_log"] = (
            "# Session Log\n\n"
            "## usable catalog local-JSON — 2026-08-26 (Cloud Agent, no audio)\n\n"
            "once\n\n"
            "## usable catalog local-JSON — 2026-08-26 (Cloud Agent, no audio)\n\n"
            "once again\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "Session Log.md heading appears more than once" in e
                and "usable catalog local-JSON" in e
                for e in errors
            ),
            errors,
        )

    def test_unique_session_log_headings_pass(self):
        extras = extras_ok()
        extras["session_log"] = (
            "# Session Log\n\n"
            "## usable catalog local-JSON — 2026-08-26 (Cloud Agent, no audio)\n\n"
            "once\n\n"
            "## Session Log once — 2026-08-26 (Cloud Agent, no audio)\n\n"
            "leftover removed\n\n"
            "### Next continuation point\n\n"
            "standing Jeff-owned items unchanged\n"
        )
        self.assertEqual(validate(fixture(), extras), [])

    def test_session_log_h3_repeat_is_not_a_duplicate_pass(self):
        extras = extras_ok()
        extras["session_log"] = (
            "# Session Log\n\n"
            "## one pass\n\n"
            "### Done\n\n"
            "## other pass\n\n"
            "### Done\n\n"
            "### Next continuation point\n\n"
            "standing Jeff-owned items unchanged\n"
        )
        self.assertEqual(validate(fixture(), extras), [])
        self.assertEqual(duplicate_session_log_headings(extras["session_log"]), [])

    def test_missing_session_log_fails(self):
        extras = extras_ok()
        extras["session_log"] = None
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("Session Log.md is required for resume" in e for e in errors),
            errors,
        )

    def test_empty_session_log_fails(self):
        extras = extras_ok()
        extras["session_log"] = "   \n"
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("Session Log.md is required for resume" in e for e in errors),
            errors,
        )

    def test_latest_session_log_without_continuation_fails(self):
        extras = extras_ok()
        extras["session_log"] = (
            "# Session Log\n\n"
            "## first pass\n\n"
            "### Next continuation point\n\n"
            "old\n\n"
            "## latest pass\n\n"
            "no continuation here\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "latest Session Log H2 pass has no Next continuation point" in e
                for e in errors
            ),
            errors,
        )
        self.assertFalse(latest_session_log_has_continuation(extras["session_log"]))

    def test_session1_style_continuation_on_latest_pass(self):
        extras = extras_ok()
        extras["session_log"] = (
            "# Session Log\n\n"
            "## Session 1 — 2026-08-18\n\n"
            "### NOT done / next continuation point\n\n"
            "old\n"
        )
        self.assertEqual(validate(fixture(), extras), [])
        self.assertTrue(latest_session_log_has_continuation(extras["session_log"]))

    def test_stale_producer_readme_resume_fails(self):
        extras = extras_ok()
        extras["producer_readme"] = (
            'Continue from "NOT done / next continuation point" in the Session Log.\n'
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "Producer README resume still points at the Session 1" in e
                for e in errors
            ),
            errors,
        )

    def test_producer_readme_without_latest_session_log_fails(self):
        extras = extras_ok()
        extras["producer_readme"] = "Resume somehow.\n"
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "Producer README resume must start from the latest Session Log H2" in e
                for e in errors
            ),
            errors,
        )

    def test_producer_readme_latest_session_log_passes(self):
        extras = extras_ok()
        extras["producer_readme"] = (
            "Continue from the latest Session Log H2 pass.\n"
        )
        self.assertEqual(validate(fixture(), extras), [])

    def test_apps_md_ci_fails_closed_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "CI fails closed if this file drifts.\n"
            "Hosted validate may be a 0-step empty-runner — not a catalog fail.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "APPS.md still claims CI fails closed" in e
                for e in errors
            ),
            errors,
        )
        self.assertTrue(apps_md_claims_hosted_ci(extras["apps_md"]))

    def test_apps_md_without_empty_runner_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "APPS.md must say hosted validate may be an empty-runner" in e
                for e in errors
            ),
            errors,
        )
        self.assertFalse(apps_md_admits_empty_runner(extras["apps_md"]))

    def test_apps_md_local_validate_honesty_passes(self):
        extras = extras_ok()
        extras["apps_md"] = APPS_MD_HONEST
        self.assertEqual(validate(fixture(), extras), [])
        self.assertFalse(apps_md_claims_hosted_ci(extras["apps_md"]))
        self.assertTrue(apps_md_admits_empty_runner(extras["apps_md"]))
        self.assertFalse(apps_md_claims_spine_still_accepted(extras["apps_md"]))
        self.assertTrue(apps_md_admits_spine_reject(extras["apps_md"]))
        self.assertTrue(apps_md_admits_show_night_owner_only(extras["apps_md"]))
        self.assertTrue(apps_md_admits_official_set_dump(extras["apps_md"]))
        self.assertTrue(apps_md_admits_catalog_not_official_set(extras["apps_md"]))
        self.assertFalse(
            apps_md_claims_feed_writes_official_set(extras["apps_md"])
        )
        self.assertFalse(
            apps_md_claims_suggestion_dump_is_official_set(extras["apps_md"])
        )
        self.assertFalse(
            apps_md_claims_catalog_is_official_set(extras["apps_md"])
        )

    def test_apps_md_spine_remap_lie_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail. "
            "StoryBoard rejects the spine as an import. "
            "Show Night official set is owner-only. "
            "StoryBoard binds a local official-set dump as "
            "Rad Dad — official set. Show Night is the live set surface. "
            "Catalog rows are not the official set. Show Night owns official sets. "
            "StoryBoard pointed at master_catalog.json does not remap "
            "live_presence.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("deleted spine-accept path" in e for e in errors),
            errors,
        )
        self.assertTrue(apps_md_claims_spine_still_accepted(extras["apps_md"]))

    def test_apps_md_without_spine_reject_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("rejects the spine" in e for e in errors),
            errors,
        )
        self.assertFalse(apps_md_admits_spine_reject(extras["apps_md"]))

    def test_apps_md_without_show_night_owner_only_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail. "
            "StoryBoard rejects the spine as an import.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("official set is owner-only" in e for e in errors),
            errors,
        )
        self.assertFalse(apps_md_admits_show_night_owner_only(extras["apps_md"]))

    def test_apps_md_without_catalog_not_official_set_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail. "
            "StoryBoard rejects the spine as an import. "
            "Show Night official set is owner-only. "
            "StoryBoard binds a local official-set dump as "
            "Rad Dad — official set. Show Night is the live set surface.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("catalog rows are not the official" in e for e in errors),
            errors,
        )
        self.assertFalse(apps_md_admits_catalog_not_official_set(extras["apps_md"]))

    def test_apps_md_catalog_is_official_set_lie_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            APPS_MD_HONEST + "Catalog rows are the official set.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("catalog rows are the official" in e for e in errors),
            errors,
        )
        self.assertTrue(apps_md_claims_catalog_is_official_set(extras["apps_md"]))

    def test_apps_md_without_official_set_dump_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail. "
            "StoryBoard rejects the spine as an import. "
            "Show Night official set is owner-only.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("official-set dump binds" in e or "live set surface" in e for e in errors),
            errors,
        )
        self.assertFalse(apps_md_admits_official_set_dump(extras["apps_md"]))

    def test_apps_md_suggestion_dump_lie_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            APPS_MD_HONEST + "Suggestion dump is the official set.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("suggestion dump as the official" in e for e in errors),
            errors,
        )
        self.assertTrue(
            apps_md_claims_suggestion_dump_is_official_set(extras["apps_md"])
        )

    def test_apps_md_feed_writes_official_set_lie_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail. "
            "StoryBoard rejects the spine as an import. "
            "Show Night official set is owner-only. "
            "StoryBoard binds a local official-set dump as "
            "Rad Dad — official set. Show Night is the live set surface. "
            "Catalog rows are not the official set. Show Night owns official sets. "
            "This feed writes the official set.\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("writes the official set" in e for e in errors),
            errors,
        )
        self.assertTrue(
            apps_md_claims_feed_writes_official_set(extras["apps_md"])
        )

    def test_readme_in_the_live_set_fails(self):
        extras = extras_ok()
        extras["readme"] = "On deck — in the live set, lyric recovered\n"
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("README.md" in e and "catalog rows are the live set" in e for e in errors),
            errors,
        )
        self.assertTrue(catalog_surface_claims_official_set(extras["readme"]))

    def test_readme_live_lane_title_fails(self):
        extras = extras_ok()
        extras["readme"] = "Flagship — Turn Over The Flag\n"
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("README.md" in e and "live-lane titles" in e for e in errors),
            errors,
        )
        self.assertTrue(public_doc_has_live_lane_titles(extras["readme"], fixture()))

    def test_readme_protected_opus_name_fails(self):
        extras = extras_ok()
        extras["readme"] = "The Opus — Blue Skies Fade\n"
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("README.md" in e and "protected-opus names" in e for e in errors),
            errors,
        )
        self.assertTrue(
            public_doc_has_protected_opus_names(extras["readme"], fixture())
        )

    def test_readme_published_id_fails(self):
        extras = extras_ok()
        extras["readme"] = "Flagship ST-0001\n"
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("README.md" in e and "published ids" in e for e in errors),
            errors,
        )
        self.assertTrue(public_doc_has_published_ids(extras["readme"]))

    def test_readme_collaborator_map_fails(self):
        extras = extras_ok()
        extras["readme"] = (
            "collaborators' compositions (Dustin Duffy, Sean, "
            "Paco Estrada, Greg Baldia)\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any(
                "README.md" in e and "collaborator-as-catalog-map" in e
                for e in errors
            ),
            errors,
        )
        self.assertTrue(public_doc_has_collaborator_map(extras["readme"], fixture()))

    def test_apps_md_writeback_ids_fail(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail.\n"
            'songs: ["ST-0002", "ST-0014", "JS-0001"]\n'
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("APPS.md" in e and "published ids" in e for e in errors),
            errors,
        )
        self.assertTrue(public_doc_has_published_ids(extras["apps_md"]))
        self.assertFalse(apps_md_claims_hosted_ci(extras["apps_md"]))
        self.assertTrue(apps_md_admits_empty_runner(extras["apps_md"]))

    def test_apps_md_catalog_title_fails(self):
        extras = extras_ok()
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail.\n"
            "Drinking Song as a catalog map\n"
        )
        errors = validate(fixture(), extras)
        self.assertTrue(
            any("APPS.md" in e and "catalog titles" in e for e in errors),
            errors,
        )
        self.assertTrue(
            public_doc_has_other_catalog_titles(extras["apps_md"], fixture())
        )

    def test_public_docs_roles_counts_only_pass(self):
        extras = extras_ok()
        extras["readme"] = (
            "Vault is the catalog brain. 150 entities. "
            "Flagship, Quick win, Experimental, On deck, The Opus. "
            "128 YES / 20 NO / 2 NEEDS-CONSENT. "
            "40 setlist-ready keyed originals; 20-row Vault default-live slice.\n"
        )
        extras["apps_md"] = (
            "Local python3 scripts/validate_catalog.py fails closed "
            "if this file drifts. Hosted catalog-validate may be a "
            "0-step empty-runner — not a catalog fail. "
            "Roles only: Flagship · Quick win · Experimental. On deck. "
            "Protected opus. Andrea-Assistant is inbound. "
            "Travis rows are travis_books. Write-back songs array uses "
            "vault ids — do not paste published ids here. "
            "StoryBoard rejects the spine as an import. "
            "Show Night official set is owner-only. "
            "StoryBoard binds a local official-set dump as "
            "Rad Dad — official set. Show Night is the live set surface. "
            "Catalog rows are not the official set. Show Night owns official sets.\n"
        )
        self.assertEqual(validate(fixture(), extras), [])
        self.assertEqual(
            public_facing_doc_errors("README.md", extras["readme"], fixture()),
            [],
        )
        self.assertEqual(
            public_facing_doc_errors("APPS.md", extras["apps_md"], fixture()),
            [],
        )
        self.assertFalse(apps_md_claims_hosted_ci(extras["apps_md"]))
        self.assertTrue(apps_md_admits_empty_runner(extras["apps_md"]))
        self.assertFalse(apps_md_claims_spine_still_accepted(extras["apps_md"]))
        self.assertTrue(apps_md_admits_spine_reject(extras["apps_md"]))
        self.assertTrue(apps_md_admits_show_night_owner_only(extras["apps_md"]))
        self.assertTrue(apps_md_admits_official_set_dump(extras["apps_md"]))
        self.assertTrue(apps_md_admits_catalog_not_official_set(extras["apps_md"]))
        self.assertFalse(
            apps_md_claims_feed_writes_official_set(extras["apps_md"])
        )
        self.assertFalse(
            apps_md_claims_catalog_is_official_set(extras["apps_md"])
        )

    def test_validator_docstring_does_not_claim_hosted_ci(self):
        self.assertFalse(module_doc_claims_hosted_ci())

    def test_catalog_ok_report_is_roles_counts_only(self):
        line = catalog_ok_report(150, 126)
        self.assertIn("catalog OK", line)
        self.assertIn("150 entities", line)
        self.assertIn("126 originals", line)
        self.assertIn("3 active lanes", line)
        self.assertIn("protected opus", line)
        self.assertNotIn("lanes ST-", line)
        self.assertNotIn("lanes JS-", line)
        self.assertFalse(public_doc_has_published_ids(line))
        self.assertFalse(catalog_ok_report_leaks_published_ids(line))
        self.assertFalse(catalog_ok_report_leaks_published_ids())

    def test_catalog_ok_report_with_published_id_is_a_leak(self):
        leaked = catalog_ok_report(1, 1) + " ST-0000"
        self.assertTrue(public_doc_has_published_ids(leaked))
        self.assertTrue(catalog_ok_report_leaks_published_ids(leaked))

    def test_validate_fails_when_success_line_ships_ids(self):
        import validate_catalog as vc

        original = vc.catalog_ok_report
        vc.catalog_ok_report = lambda *_a, **_k: "catalog OK — lanes ST-0000"
        try:
            errors = validate(fixture(), extras_ok())
            self.assertTrue(
                any("success line still ships published ids" in e for e in errors),
                errors,
            )
        finally:
            vc.catalog_ok_report = original

    def test_live_validate_stdout_is_roles_counts_only(self):
        import subprocess

        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "validate_catalog.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("catalog OK", proc.stdout)
        self.assertIn("3 active lanes", proc.stdout)
        self.assertIn("protected opus", proc.stdout)
        self.assertNotIn("lanes ST-", proc.stdout)
        self.assertNotIn("lanes JS-", proc.stdout)
        self.assertFalse(public_doc_has_published_ids(proc.stdout))
        self.assertFalse(public_doc_has_published_ids(proc.stderr))
        self.assertFalse(catalog_ok_report_leaks_published_ids(proc.stdout))

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
        self.assertEqual(api["counts"]["originals"], 126)
        self.assertEqual(api["counts"]["scored"], 59)
        self.assertEqual(api["counts"]["ai_upload_ok"], 128)
        csv_ids = [row["song_id"] for row in extra["catalog_csv"]]
        spine_ids = [song["song_id"] for song in cat["songs"]]
        self.assertEqual(csv_ids, spine_ids)
        self.assertEqual(len(csv_ids), 150)
        self.assertEqual(len(extra["covers_csv"]), 93)
        self.assertTrue(
            set(extra["version_chains"]).issubset({song["song_id"] for song in cat["songs"]})
        )
        mom_ids = {row["id"] for row in extra["momentum"]}
        self.assertTrue(mom_ids.issubset({song["song_id"] for song in cat["songs"]}))
        self.assertNotEqual(
            api["counts"]["setlist_ready"],
            api["counts"]["storyboard_default_live"],
        )
        self.assertNotEqual(
            api["counts"]["originals"],
            api["counts"]["setlist_ready"],
        )
        self.assertNotEqual(
            api["counts"]["originals"],
            api["counts"]["storyboard_default_live"],
        )
        self.assertNotEqual(
            api["counts"]["scored"],
            api["counts"]["originals"],
        )
        self.assertNotEqual(
            api["counts"]["ai_upload_ok"],
            api["counts"]["originals"],
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
        self.assertIn("StoryBoard #12", api["storyboard"]["inspected"])
        self.assertIn("StoryBoard #16", api["storyboard"]["inspected"])
        self.assertIn("StoryBoard #19", api["storyboard"]["inspected"])
        self.assertIn("Show Night #1", api["storyboard"]["inspected"])
        self.assertIn("Show Night #3", api["storyboard"]["inspected"])
        self.assertIn("owner-only", api["storyboard"]["inspected"])
        self.assertIn("official-set dump", api["storyboard"]["inspected"])
        self.assertIn("live set surface", api["storyboard"]["inspected"])
        self.assertEqual(api["storyboard"]["import_file"], VAULT_IMPORT_FILE)
        self.assertTrue(api["storyboard"]["master_catalog_is_not_the_import"])
        self.assertTrue(api["storyboard"]["master_catalog_is_rejected"])
        self.assertEqual(
            api["storyboard"]["vault_spine_import_error"],
            VAULT_SPINE_IMPORT_ERROR,
        )
        self.assertTrue(api["storyboard"]["never_auto_post"])
        self.assertTrue(api["storyboard"]["show_night_does_not_expand_vault"])
        self.assertTrue(api["storyboard"]["show_night_official_set_is_owner_only"])
        self.assertTrue(
            api["storyboard"]["show_night_public_suggestions_cannot_mutate_set"]
        )
        self.assertTrue(api["storyboard"]["vault_feed_is_not_a_show_night_writer"])
        self.assertTrue(api["storyboard"]["show_night_binds_official_set_dump"])
        self.assertTrue(api["storyboard"]["show_night_official_set_dump_is_local"])
        self.assertEqual(api["storyboard"]["show_night_official_set_slug"], "rad-dad")
        self.assertEqual(
            api["storyboard"]["show_night_official_set_setlist_name"],
            SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME,
        )
        self.assertTrue(api["storyboard"]["show_night_guest_sets_stay_opt_in"])
        self.assertEqual(api["storyboard"]["show_night_role"], "live_set_surface")
        self.assertEqual(api["storyboard"]["vault_role"], "catalog")
        self.assertEqual(api["storyboard"]["raddad_site_role"], "public_site")
        self.assertTrue(api["storyboard"]["ops"]["show_night_binds_official_set_dump"])
        self.assertTrue(api["storyboard"]["ops"]["show_night_guest_sets_stay_opt_in"])
        self.assertTrue(api["storyboard"]["local_json_only"])
        self.assertIs(api["storyboard"]["remote_catalog_urls"], False)
        self.assertEqual(
            api["storyboard"]["band_operations_import"], BAND_OPERATIONS_IMPORT
        )
        self.assertFalse(catalog_locator_looks_remote(api))
        self.assertTrue(LOCAL_JSON_ONLY)
        self.assertIs(REMOTE_CATALOG_URLS, False)
        self.assertTrue(NEVER_AUTO_POST)
        self.assertTrue(vault_payload_looks_like_spine(cat))
        self.assertFalse(vault_payload_looks_like_spine(api))
        self.assertEqual(vault_payload_validation_error(cat), VAULT_SPINE_IMPORT_ERROR)
        self.assertIsNone(vault_payload_validation_error(api))
        self.assertEqual(spine_default_plan_ids(cat["songs"]), [])
        live_ids = {
            rec["id"]
            for rec, decision in live_default_decisions(
                api["songs"], ready_ids, default_ids
            )
            if decision.include
        }
        self.assertEqual(live_ids, default_ids)
        headings = session_log_h2_headings(extra["session_log"])
        leftover = "usable catalog local-JSON — 2026-08-26 (Cloud Agent, no audio)"
        latest = latest_session_log_section(extra["session_log"])
        self.assertEqual(duplicate_session_log_headings(extra["session_log"]), [])
        self.assertEqual(len(headings), len(set(headings)))
        self.assertEqual(headings.count(leftover), 1)
        self.assertIn("Session Log once — 2026-08-26 (Cloud Agent, no audio)", headings)
        self.assertIn(
            "Session Log resume from latest — 2026-08-26 (Cloud Agent, no audio)",
            headings,
        )
        self.assertIn(
            "Local validate is the catalog gate — 2026-08-26 (Cloud Agent, no audio)",
            headings,
        )
        self.assertTrue(latest_session_log_has_continuation(extra["session_log"]))
        self.assertIn("### Next continuation point", latest)
        self.assertIn("latest Session Log", extra["producer_readme"])
        self.assertNotIn(
            'Continue from "NOT done / next continuation point"',
            extra["producer_readme"],
        )
        self.assertFalse(module_doc_claims_hosted_ci())
        self.assertTrue(isinstance(extra["apps_md"], str) and extra["apps_md"].strip())
        self.assertFalse(apps_md_claims_hosted_ci(extra["apps_md"]))
        self.assertTrue(apps_md_admits_empty_runner(extra["apps_md"]))
        self.assertNotIn("CI fails closed", extra["apps_md"])
        self.assertTrue(isinstance(extra["readme"], str) and extra["readme"].strip())
        self.assertEqual(
            public_facing_doc_errors("README.md", extra["readme"], cat),
            [],
        )
        self.assertEqual(
            public_facing_doc_errors("APPS.md", extra["apps_md"], cat),
            [],
        )
        self.assertFalse(public_doc_has_live_lane_titles(extra["readme"], cat))
        self.assertFalse(public_doc_has_protected_opus_names(extra["readme"], cat))
        self.assertFalse(public_doc_has_other_catalog_titles(extra["readme"], cat))
        self.assertFalse(public_doc_has_published_ids(extra["readme"]))
        self.assertFalse(public_doc_has_collaborator_map(extra["readme"], cat))
        self.assertFalse(public_doc_has_live_lane_titles(extra["apps_md"], cat))
        self.assertFalse(public_doc_has_protected_opus_names(extra["apps_md"], cat))
        self.assertFalse(public_doc_has_other_catalog_titles(extra["apps_md"], cat))
        self.assertFalse(public_doc_has_published_ids(extra["apps_md"]))
        self.assertFalse(public_doc_has_collaborator_map(extra["apps_md"], cat))
        leftover_docs = (
            "Jeff-facing docs roles and counts only — 2026-08-26 "
            "(Cloud Agent, no audio)"
        )
        leftover_stdout = (
            "Local validate success is roles and counts only — 2026-08-27 "
            "(Cloud Agent, no audio)"
        )
        leftover_spine = (
            "StoryBoard rejects the spine — 2026-08-27 "
            "(Cloud Agent, no audio)"
        )
        leftover_owner = (
            "Show Night official set is owner-only — 2026-08-27 "
            "(Cloud Agent, no audio)"
        )
        leftover_dump = (
            "Official-set dump binds Rad Dad — official set — 2026-08-27 "
            "(Cloud Agent, no audio)"
        )
        leftover_catalog = (
            "Catalog rows are not the official set — 2026-08-27 "
            "(Cloud Agent, no audio)"
        )
        leftover_csv = (
            "Satellite catalog tables fail closed — 2026-08-28 "
            "(Cloud Agent, no audio)"
        )
        leftover_song = (
            "Song analysis Logic-ready walk — 2026-08-28 "
            "(Cloud Agent, no audio)"
        )
        leftover_covers = (
            "Covers book leftover walk — 2026-08-28 "
            "(Cloud Agent, no audio)"
        )
        leftover_memos = (
            "Catalog memo evidence find-and-act — 2026-09-03 "
            "(Cloud Agent, no audio)"
        )
        leftover_work = (
            "Catalog song work card — 2026-09-03 "
            "(Cloud Agent, no audio)"
        )
        leftover_sitdown = (
            "Catalog write/produce/listen sit-down — 2026-09-03 "
            "(Cloud Agent, no audio)"
        )
        product_session_start = (
            "Catalog one-song session start — 2026-09-03 "
            "(Codex Extra High, no audio)"
        )
        self.assertIn(leftover_docs, headings)
        self.assertIn(leftover_stdout, headings)
        self.assertIn(leftover_spine, headings)
        self.assertIn(leftover_owner, headings)
        self.assertIn(leftover_dump, headings)
        self.assertIn(leftover_catalog, headings)
        self.assertIn(leftover_csv, headings)
        self.assertIn(leftover_song, headings)
        self.assertIn(leftover_covers, headings)
        self.assertIn(leftover_memos, headings)
        self.assertIn(leftover_work, headings)
        self.assertIn(leftover_sitdown, headings)
        self.assertIn(product_session_start, headings)
        self.assertEqual(headings[-1], product_session_start)
        self.assertFalse(apps_md_claims_spine_still_accepted(extra["apps_md"]))
        self.assertTrue(apps_md_admits_spine_reject(extra["apps_md"]))
        self.assertTrue(apps_md_admits_show_night_owner_only(extra["apps_md"]))
        self.assertTrue(apps_md_admits_official_set_dump(extra["apps_md"]))
        self.assertTrue(apps_md_admits_catalog_not_official_set(extra["apps_md"]))
        self.assertFalse(
            apps_md_claims_feed_writes_official_set(extra["apps_md"])
        )
        self.assertFalse(
            apps_md_claims_suggestion_dump_is_official_set(extra["apps_md"])
        )
        self.assertFalse(
            apps_md_claims_catalog_is_official_set(extra["apps_md"])
        )
        self.assertTrue(extra["app_api"]["storyboard"]["catalog_rows_are_not_the_official_set"])
        self.assertTrue(
            extra["app_api"]["storyboard"]["vault_default_live_is_not_the_official_set"]
        )
        self.assertTrue(extra["app_api"]["storyboard"]["show_night_owns_official_sets"])
        self.assertTrue(
            extra["app_api"]["storyboard"]["ops"]["catalog_rows_are_not_the_official_set"]
        )
        self.assertIn("StoryBoard #20", extra["app_api"]["storyboard"]["inspected"])
        self.assertIn(
            "catalog rows are not the official set",
            extra["app_api"]["storyboard"]["inspected"],
        )
        self.assertTrue(catalog_surface_admits_not_official_set(extra["dashboard_html"]))
        self.assertFalse(catalog_surface_claims_official_set(extra["dashboard_html"]))
        self.assertFalse(catalog_surface_claims_official_set(extra["readme"]))
        self.assertNotIn("IN CURRENT LIVE SET", extra["dashboard_html"])
        self.assertFalse(dashboard_opens_owner_audio(extra["dashboard_html"]))
        self.assertFalse(dashboard_displays_owner_audio_index(extra["dashboard_html"]))
        self.assertIn("this page does not open audio", extra["dashboard_html"])
        self.assertIn("Has searchable memos", extra["dashboard_html"])
        self.assertIn("Sit-down", extra["dashboard_html"])
        self.assertIn('id="workSession"', extra["dashboard_html"])
        self.assertTrue(dashboard_exposes_song_work(extra["dashboard_html"]))
        self.assertNotIn("in the live set", extra["readme"])
        self.assertTrue(extra["app_api"]["storyboard"]["show_night_binds_official_set_dump"])
        self.assertFalse(catalog_ok_report_leaks_published_ids())
        originals = sum(
            1 for s in cat["songs"] if s.get("classification") == "original"
        )
        live_ok = catalog_ok_report(len(cat["songs"]), originals)
        self.assertIn("3 active lanes", live_ok)
        self.assertFalse(public_doc_has_published_ids(live_ok))
        discovery = extra.get("song_analysis_discovery")
        if discovery is None:
            discovery_path = os.path.join(
                ROOT, "00_control_room", "Catalog Discovery — song analysis.md"
            )
            with open(discovery_path, encoding="utf-8") as handle:
                discovery = handle.read()
        original_ids = [
            song["song_id"]
            for song in cat["songs"]
            if song.get("classification") == "original"
        ]
        self.assertEqual(len(original_ids), 126)
        missing = [sid for sid in original_ids if sid not in discovery]
        self.assertEqual(missing, [], missing)
        self.assertIn("Official-set originals | 0", discovery)
        self.assertIn("reported-only", discovery)
        self.assertIn("Tooted last Tuesday", discovery)
        self.assertIn("stay unmatched", discovery.lower())
        self.assertIn("ST-0004 | Manic", discovery)
        self.assertIn("audio_only", discovery)
        covers = cat.get("covers") or []
        self.assertEqual(len(covers), 93)
        self.assertEqual(cat.get("covers_reference"), 93)
        self.assertEqual(len(extra["covers_csv"]), 93)
        for cover in covers:
            self.assertEqual(
                set(cover),
                {"title", "original_artist", "context", "classification"},
            )
            self.assertFalse(cover.get("song_id"))
            self.assertFalse(cover.get("key"))
            self.assertFalse(cover.get("official_set"))
        trailer_originals = [
            song
            for song in cat["songs"]
            if song.get("classification") == "original"
            and "trailer" in str(song.get("artist_project") or "").lower()
        ]
        self.assertEqual(trailer_originals, [])
        official_set_originals = [
            song
            for song in cat["songs"]
            if song.get("classification") == "original" and song.get("official_set")
        ]
        self.assertEqual(official_set_originals, [])
        self.assertEqual(
            sum(1 for song in extra["app_api"]["songs"] if song.get("official_set")),
            0,
        )
        ready_titles = {row["title"] for row in extra["app_api"]["setlist_ready"]}
        cover_titles = [cover["title"] for cover in covers]
        self.assertTrue(set(cover_titles).isdisjoint(ready_titles))
        manic = next(song for song in cat["songs"] if song["song_id"] == "ST-0004")
        self.assertFalse(str(manic.get("key") or "").strip())
        covers_discovery = extra.get("covers_book_discovery")
        if covers_discovery is None:
            covers_path = os.path.join(
                ROOT, "00_control_room", "Catalog Discovery — covers book leftover.md"
            )
            with open(covers_path, encoding="utf-8") as handle:
                covers_discovery = handle.read()
        missing_covers = [title for title in cover_titles if title not in covers_discovery]
        self.assertEqual(missing_covers, [], missing_covers)
        self.assertIn("Official-set originals | 0", covers_discovery)
        self.assertIn("Trailer Swift original rows | 0", covers_discovery)
        self.assertIn("empty_logic_ready", covers_discovery)
        self.assertIn("stay unmatched", covers_discovery.lower())
        self.assertIn("Speak Now", covers_discovery)
        self.assertIn("Tooted last Tuesday", covers_discovery)


if __name__ == "__main__":
    unittest.main()
