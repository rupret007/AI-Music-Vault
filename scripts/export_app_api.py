#!/usr/bin/env python3
"""
export_app_api.py — the StoryBoard import feed.

Vault (data/master_catalog.json) is the song brain.
StoryBoard is the band-management OS that consumes it.
This script publishes ONE slim, stable-schema file — data/app_api.json —
so StoryBoard does not hand-enter songs and we do not invent a second catalog.

Field honesty: emit StoryBoard-importable values on the fields
catalog-import.ts actually reads (id, title, project, is_original, key,
bpm, bpm_int, vault_id, vault_ref, played_live, import_scope). StoryBoard
#6 prefers the published setlist_ready_default_import slice and names
that draft "Vault default-live". Parked-named rows in that slice stay
current-artist repertoire, not a fourth live band. Not StoryDesk. Not
StoryOps. StoryLiner is promo only. No new app. No fourth live band.

Run:  python3 scripts/export_app_api.py
Check: python3 scripts/export_app_api.py --check
Out:  data/app_api.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

from storyboard_contract import (
    SCOPE_COVER,
    SCOPE_DEFAULT_LIVE,
    SCOPE_NOT_LIVE,
    SCOPE_NOT_READY,
    SCOPE_PARKED,
    SCOPE_BOOKER,
    bpm_int,
    bpm_raw_string,
    default_decisions,
    parked_named_default_live_ids,
    played_live_from_presence,
    source_key,
    storyboard_mapping,
    storyboard_parse_key,
    vault_ref_for,
)

SCHEMA_VERSION = 3
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(HERE, "data", "master_catalog.json")
OUT = os.path.join(HERE, "data", "app_api.json")

LANES = {
    "flagship": "ST-0001",      # Turn Over The Flag
    "quick_win": "ST-0004",     # Manic
    "experimental": "ST-0009",  # Long Long Drive
    "on_deck": "JS-0128",       # It's Alright
    "opus": "JS-0107",          # Blue Skies Fade
}


def export_song(src: dict) -> dict:
    gate = src.get("ai_upload_ok", "") or ""
    sid = src["song_id"]
    title = src["canonical_title"]
    project = src.get("artist_project", "")
    is_original = src.get("classification") == "original"
    raw_bpm = src.get("bpm")
    parsed_bpm = bpm_int(raw_bpm)
    return {
        "id": sid,
        "vault_id": sid,
        "vault_ref": vault_ref_for(sid),
        "source_key": source_key(sid),
        "title": title,
        "alt_titles": src.get("alt_titles", []),
        "project": project,
        "import_scope": None,
        "is_original": is_original,
        "writers": src.get("writers", []),
        "key": src.get("key", "") or "",
        # StoryBoard parseBpm prefers bpm_int, then bpm.
        "bpm": parsed_bpm,
        "bpm_raw": bpm_raw_string(raw_bpm),
        "bpm_int": parsed_bpm,
        "duration_seconds": None,
        "potential": src.get("potential"),
        "readiness": src.get("readiness"),
        "momentum": src.get("momentum"),
        "last_activity": src.get("last_activity", ""),
        "live_latest": src.get("live_latest", ""),
        "played_live": played_live_from_presence(src.get("live_presence")),
        "stage": src.get("stage", ""),
        "theme": src.get("theme", ""),
        "hook": src.get("hook", ""),
        "next_action": src.get("next_action", ""),
        # machine-readable rights gate: only True means an AI service is OK,
        # and only for Jeff's SOLO recordings, privately. See README rule 3.
        "ai_upload_ok": str(gate).startswith("YES"),
        "ai_upload_note": gate,
    }


def _ready_row(song: dict) -> dict:
    return {
        "id": song["id"],
        "title": song["title"],
        "key": song["key"],
        "project": song["project"],
        "bpm": song["bpm"],
        "bpm_int": song["bpm_int"],
        "vault_ref": song["vault_ref"],
        "import_scope": song["import_scope"],
    }


def _assign_import_scopes(songs: list[dict], ready_ids: set[str]) -> dict[str, int]:
    """Stamp StoryBoard default-plan reasons onto each exported song."""
    scope_counts = {
        SCOPE_DEFAULT_LIVE: 0,
        SCOPE_PARKED: 0,
        SCOPE_NOT_LIVE: 0,
        SCOPE_NOT_READY: 0,
        SCOPE_BOOKER: 0,
        SCOPE_COVER: 0,
    }
    for song, decision in default_decisions(songs, ready_ids):
        scope = decision.reason if not decision.include else SCOPE_DEFAULT_LIVE
        song["import_scope"] = scope
        if scope in scope_counts:
            scope_counts[scope] += 1
    return scope_counts


def build_payload(cat: dict, generated: str | None = None) -> dict:
    songs = [export_song(src) for src in cat["songs"]]
    originals = [s for s in songs if s["is_original"]]
    setlist_ready = sorted(
        [s for s in originals if storyboard_parse_key(s["key"])],
        key=lambda s: -(s["momentum"] or 0),
    )
    ready_ids = {s["id"] for s in setlist_ready}
    scope_counts = _assign_import_scopes(songs, ready_ids)
    setlist_ready_default = [
        s for s in setlist_ready if s["import_scope"] == SCOPE_DEFAULT_LIVE
    ]
    parked_named_ids = parked_named_default_live_ids(
        songs, [s["id"] for s in setlist_ready_default]
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated": generated or datetime.date.today().isoformat(),
        "catalog_version": cat.get("version", ""),
        "primary_consumer": "StoryBoard",
        "counts": {
            "entities": len(songs),
            "originals": len(originals),
            "scored": sum(1 for s in songs if s["potential"]),
            "ai_upload_ok": sum(1 for s in songs if s["ai_upload_ok"]),
            "storyboard_default_live": scope_counts[SCOPE_DEFAULT_LIVE],
            "storyboard_default_live_parked_named": len(parked_named_ids),
            "storyboard_parked": scope_counts[SCOPE_PARKED],
            "storyboard_not_live_band": scope_counts[SCOPE_NOT_LIVE],
            "storyboard_not_setlist_ready": scope_counts[SCOPE_NOT_READY],
            "storyboard_booker": scope_counts[SCOPE_BOOKER],
            "storyboard_cover": scope_counts[SCOPE_COVER],
            "setlist_ready": len(setlist_ready),
            "setlist_ready_default_import": len(setlist_ready_default),
        },
        "lanes": LANES,
        "storyboard": storyboard_mapping(parked_named_ids),
        "songs": songs,
        "setlist_ready": [_ready_row(s) for s in setlist_ready],
        "setlist_ready_default_import": [_ready_row(s) for s in setlist_ready_default],
        "notes": {
            "scores": "potential = how good; readiness = how close to done; "
                      "momentum = how alive in Jeff's hands. Never merge them.",
            "rights": "ai_upload_ok=false means NEVER send this song's audio or "
                      "lyrics to an AI music service. Covers, co-writes and "
                      "collaborators' songs are all false.",
            "audio": "No audio lives in this repo. Masters stay local + Drive.",
            "storyboard_import": (
                "PRIMARY PATH: StoryBoard imports THIS file. It reads songs[] "
                "id, title, project, is_original, key, bpm, bpm_int, vault_id, "
                "vault_ref, played_live, import_scope. Default live is the "
                "published setlist_ready_default_import slice (empty published "
                "slice stays empty). StoryBoard names that draft 'Vault "
                "default-live'. Parked-named rows in that slice (Everyday / "
                "Stalemate, hybrids) stay current-artist repertoire — not a "
                "fourth live band. Fallback when that array is absent: Rad "
                "Dad + Jeff Story + recorded Rad Dad plays, gated by "
                "setlist_ready ('Vault setlist-ready'). Parked catalogs that "
                "are not in the published slice are not a fourth live band. "
                "Travis books. StoryLiner is promo only. Jeff owns setlist "
                "order, duration, and lead vocalist. Do not invent a second "
                "catalog."
            ),
        },
    }


def comparable(payload: dict) -> dict:
    """Drop the date stamp so --check is stable across midnight CI."""
    out = dict(payload)
    out.pop("generated", None)
    return out


def write_payload(payload: dict, path: str = OUT) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1, ensure_ascii=False)
        handle.write("\n")


def check_committed(cat: dict, path: str = OUT) -> list[str]:
    if not os.path.exists(path):
        return [f"missing StoryBoard feed at {path}"]
    with open(path, encoding="utf-8") as handle:
        committed = json.load(handle)
    expected = comparable(build_payload(cat, generated=committed.get("generated")))
    actual = comparable(committed)
    if expected == actual:
        return []
    return [
        "data/app_api.json is stale vs scripts/export_app_api.py — "
        "re-run python3 scripts/export_app_api.py"
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export the StoryBoard catalog feed")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if data/app_api.json does not match a fresh export",
    )
    args = parser.parse_args(argv)

    with open(CAT, encoding="utf-8") as handle:
        cat = json.load(handle)

    if args.check:
        errors = check_committed(cat)
        if errors:
            print("export CHECK FAILED", file=sys.stderr)
            for err in errors:
                print(f"  • {err}", file=sys.stderr)
            return 1
        print(f"export OK — {OUT} matches scripts/export_app_api.py")
        return 0

    payload = build_payload(cat)
    write_payload(payload)
    counts = payload["counts"]
    print(f"wrote {OUT}")
    print(
        f"  {counts['entities']} entities · {counts['originals']} originals · "
        f"{counts['scored']} scored · {counts['ai_upload_ok']} AI-eligible"
    )
    print(
        f"  {counts['setlist_ready']} setlist-ready originals "
        f"({counts['setlist_ready_default_import']} default-live repertoire)"
    )
    print(
        f"  StoryBoard default import: {counts['storyboard_default_live']} live / "
        f"{counts['storyboard_default_live_parked_named']} parked-named "
        f"(current artist) / "
        f"{counts['storyboard_parked']} parked / "
        f"{counts['storyboard_not_setlist_ready']} not-ready / "
        f"{counts['storyboard_cover']} cover / "
        f"{counts['storyboard_booker']} booker / "
        f"{counts['storyboard_not_live_band']} not-live-band"
    )
    print("  primary consumer: StoryBoard (same songs[] — no second catalog)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
