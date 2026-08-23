#!/usr/bin/env python3
"""
validate_catalog.py — fail-closed integrity check for the vault spine.

Checks data/master_catalog.json (IDs, scores, AI-upload gates, next actions,
three-active-song cap) plus the StoryBoard feed (data/app_api.json) when present.

This does NOT listen to audio, score songs, or invent priorities.
Jeff owns the three active lanes; this script only verifies they still exist
and that machine-readable gates match already-recorded rights.

Run:  python3 scripts/validate_catalog.py
Exit: 0 if clean, 1 if any error (CI fails closed).
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT_PATH = os.path.join(HERE, "data", "master_catalog.json")
API_PATH = os.path.join(HERE, "data", "app_api.json")
VM_MATCHES_PATH = os.path.join(
    HERE, "01_source_manifests", "voicememo", "vm_matches.json"
)
PRIORITY_PATH = os.path.join(HERE, "00_control_room", "Priority Queue.md")
DASHBOARD_PATH = os.path.join(HERE, "Jeff Story Song Vault Dashboard.html")

# Jeff-owned WIP cap. Do not expand. on_deck / opus are parked, not a 4th/5th slot.
ACTIVE_LANES = {
    "flagship": "ST-0001",  # Turn Over The Flag
    "quick_win": "ST-0004",  # Manic
    "experimental": "ST-0009",  # Long Long Drive
}
PROTECTED_LANES = {
    "on_deck": "JS-0128",  # It's Alright — next open slot only
    "opus": "JS-0107",  # Blue Skies Fade — Kimberly lane, needs consent
}

ID_RE = re.compile(r"^(ST|SD|JS|UNK)-\d{4}$")
REQUIRED_FIELDS = (
    "song_id",
    "canonical_title",
    "artist_project",
    "classification",
    "writers",
    "rights_confidence",
    "stage",
    "ai_upload_ok",
    "potential",
    "readiness",
    "next_action",
    "key",
    "bpm",
    "alt_titles",
    "sources",
)
AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".aif", ".aiff", ".flac", ".logicx", ".band"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}

YES_GATE = (
    "YES — Jeff-written; SOLO recordings only "
    "(band performances never upload), private, logged"
)

LANE_TITLES = {
    "ST-0001": "Turn Over The Flag",
    "ST-0004": "Manic",
    "ST-0009": "Long Long Drive",
    "JS-0128": "It's Alright",
    "JS-0107": "Blue Skies Fade",
}


def gate_class(value) -> str | None:
    text = str(value or "").strip()
    if text.startswith("YES"):
        return "YES"
    if text.startswith("NO"):
        return "NO"
    if text.startswith("NEEDS"):
        return "NEEDS CONSENT"
    return None


def rights_high(song: dict) -> bool:
    return str(song.get("rights_confidence") or "").lower().startswith("high")


def jeff_solo_original(song: dict) -> bool:
    return (
        song.get("classification") == "original"
        and song.get("writers") == ["Jeff Story"]
    )


def forbidden_yes(song: dict) -> bool:
    cls = str(song.get("classification") or "").lower()
    needles = (
        "cover",
        "dustin",
        "outside composition",
        "paco",
        "sean",
        "collaborator",
        "adaptation",
        "co-write",
        "authorship uncertain",
    )
    return any(n in cls for n in needles)


def score_ok(value) -> bool:
    if value is None or value == "":
        return True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return 0 <= value <= 100


def validate(cat: dict, extras: dict | None = None) -> list[str]:
    """Return a list of error strings. Empty list = pass."""
    extras = extras or {}
    errors: list[str] = []

    songs = cat.get("songs")
    if not isinstance(songs, list) or not songs:
        return ["catalog.songs must be a non-empty list"]

    covers = cat.get("covers")
    if covers is not None and not isinstance(covers, list):
        errors.append("catalog.covers must be a list when present")

    ids: list[str] = []
    titles: list[str] = []
    originals = 0
    gate_counts = {"YES": 0, "NO": 0, "NEEDS CONSENT": 0}

    for i, song in enumerate(songs):
        if not isinstance(song, dict):
            errors.append(f"songs[{i}] is not an object")
            continue
        loc = song.get("song_id") or f"songs[{i}]"

        missing = [f for f in REQUIRED_FIELDS if f not in song]
        if missing:
            errors.append(f"{loc}: missing fields {missing}")

        sid = song.get("song_id")
        if not sid or not isinstance(sid, str):
            errors.append(f"songs[{i}]: song_id missing")
        else:
            ids.append(sid)
            if not ID_RE.match(sid):
                errors.append(f"{sid}: song_id does not match PREFIX-0000")

        title = song.get("canonical_title")
        if not title or not str(title).strip():
            errors.append(f"{loc}: canonical_title is empty")
        else:
            titles.append(str(title))

        writers = song.get("writers")
        if not isinstance(writers, list) or not writers:
            errors.append(f"{loc}: writers must be a non-empty list")
        elif any(not isinstance(w, str) or not w.strip() for w in writers):
            errors.append(f"{loc}: writers must be non-empty strings")

        for list_field in ("alt_titles", "sources", "soundcloud"):
            val = song.get(list_field)
            if val is not None and not isinstance(val, list):
                errors.append(f"{loc}: {list_field} must be a list")

        oq = song.get("open_questions")
        if oq is not None and not isinstance(oq, (str, list)):
            errors.append(f"{loc}: open_questions must be a string or list")

        for field in ("potential", "readiness", "momentum"):
            if field in song and not score_ok(song.get(field)):
                errors.append(
                    f"{loc}: {field}={song.get(field)!r} is not null or 0–100"
                )

        g = gate_class(song.get("ai_upload_ok"))
        if g is None:
            errors.append(
                f"{loc}: ai_upload_ok must start with YES / NO / NEEDS CONSENT"
            )
        else:
            gate_counts[g] += 1

        if song.get("classification") == "original":
            originals += 1
            if not str(song.get("next_action") or "").strip():
                errors.append(f"{loc}: original is missing next_action")

        if jeff_solo_original(song) and rights_high(song) and g != "YES":
            errors.append(
                f"{loc}: Jeff-solo original with high rights must be AI-upload YES "
                f"(got {song.get('ai_upload_ok')!r})"
            )

        if g == "YES" and forbidden_yes(song):
            errors.append(
                f"{loc}: classification {song.get('classification')!r} "
                "must not be AI-upload YES"
            )

        if "co-write" in str(song.get("classification") or "").lower() and g != "NEEDS CONSENT":
            errors.append(f"{loc}: co-write must be NEEDS CONSENT")

        live = song.get("live_presence")
        if live not in (None, []) and not isinstance(live, list):
            errors.append(f"{loc}: live_presence must be a list when present")

    dups = {sid for sid in ids if ids.count(sid) > 1}
    if dups:
        errors.append(f"duplicate song_id values: {sorted(dups)}")

    title_dups = {t for t in titles if titles.count(t) > 1}
    if title_dups:
        errors.append(f"duplicate canonical_title values: {sorted(title_dups)}")

    by_id = {s.get("song_id"): s for s in songs if isinstance(s, dict) and s.get("song_id")}
    for slot, sid in {**ACTIVE_LANES, **PROTECTED_LANES}.items():
        if sid not in by_id:
            errors.append(f"lane {slot}={sid} is missing from the catalog")
        else:
            expected = LANE_TITLES.get(sid)
            actual = by_id[sid].get("canonical_title")
            if expected and expected not in str(actual):
                errors.append(
                    f"lane {slot}={sid} title drifted to {actual!r} "
                    f"(expected to include {expected!r})"
                )

    opus = by_id.get(PROTECTED_LANES["opus"])
    if opus and gate_class(opus.get("ai_upload_ok")) != "NEEDS CONSENT":
        errors.append("JS-0107 Blue Skies Fade must remain NEEDS CONSENT (protected opus)")

    if len(ACTIVE_LANES) != 3:
        errors.append("ACTIVE_LANES must stay exactly three songs")

    if cat.get("original_song_entities") not in (None, originals):
        errors.append(
            f"original_song_entities={cat.get('original_song_entities')} "
            f"but classification==original count is {originals}"
        )
    if covers is not None and cat.get("covers_reference") not in (None, len(covers)):
        errors.append(
            f"covers_reference={cat.get('covers_reference')} "
            f"but covers list length is {len(covers)}"
        )

    vm_matches = extras.get("vm_matches")
    pool = cat.get("voice_memo_pool")
    if isinstance(vm_matches, dict) and isinstance(pool, dict):
        matched = sum(len(v) for v in vm_matches.values() if isinstance(v, list))
        if pool.get("matched") != matched:
            errors.append(
                f"voice_memo_pool.matched={pool.get('matched')} "
                f"but vm_matches has {matched} memos"
            )
        if pool.get("matched_songs") != len(vm_matches):
            errors.append(
                f"voice_memo_pool.matched_songs={pool.get('matched_songs')} "
                f"but vm_matches has {len(vm_matches)} songs"
            )
        unknown = sorted(sid for sid in vm_matches if sid not in by_id)
        if unknown:
            errors.append(f"vm_matches points at unknown song_id values: {unknown}")

    api = extras.get("app_api")
    if isinstance(api, dict):
        api_songs = api.get("songs") or []
        api_ids = [s.get("id") for s in api_songs if isinstance(s, dict)]
        if set(api_ids) != set(ids):
            errors.append("app_api.json song ids do not match master_catalog.json")
        lanes = api.get("lanes") or {}
        expected_lanes = {**ACTIVE_LANES, **PROTECTED_LANES}
        if lanes != expected_lanes:
            errors.append(f"app_api.json lanes drifted: {lanes} != {expected_lanes}")
        if len(lanes) != 5:
            errors.append("app_api.json must expose 3 active lanes + on_deck + opus only")
        extra_active = [k for k in lanes if k not in expected_lanes]
        if extra_active:
            errors.append(f"app_api.json invented extra lanes: {extra_active}")
        if api.get("primary_consumer") != "StoryBoard":
            errors.append("app_api.json primary_consumer must be StoryBoard")
        sb = api.get("storyboard")
        if not isinstance(sb, dict):
            errors.append("app_api.json missing storyboard mapping object")
        else:
            if sb.get("import_from") != "songs":
                errors.append("StoryBoard must import from songs[] — no second catalog")
            if sb.get("second_catalog"):
                errors.append("storyboard.second_catalog must be false")
            if sb.get("active_lane_cap") != 3:
                errors.append("storyboard.active_lane_cap must stay 3")
            if sb.get("protected_opus") != PROTECTED_LANES["opus"]:
                errors.append("storyboard.protected_opus must stay JS-0107")
            sl = sb.get("setlist") or {}
            if sl.get("seed_from") != "setlist_ready":
                errors.append("storyboard.setlist must seed from setlist_ready")
            if sl.get("jeff_owns_order") is not True:
                errors.append("storyboard.setlist must leave running order to Jeff")
            banned = {n.lower() for n in (sb.get("not_band_os") or [])}
            if "storydesk" not in banned or "storyops" not in banned:
                errors.append("storyboard mapping must name StoryDesk/StoryOps as not-band-os")
        dumped = json.dumps(api).lower()
        if '"consumer": "storydesk"' in dumped or '"consumer": "storyops"' in dumped:
            errors.append("app_api.json must not name StoryDesk/StoryOps as a consumer")
        for rec in api_songs:
            if not isinstance(rec, dict):
                continue
            src = by_id.get(rec.get("id"))
            if not src:
                continue
            want = gate_class(src.get("ai_upload_ok")) == "YES"
            if rec.get("ai_upload_ok") is not want:
                errors.append(
                    f"app_api {rec.get('id')}: ai_upload_ok={rec.get('ai_upload_ok')!r} "
                    "does not match catalog gate"
                )

    pq = extras.get("priority_queue")
    if isinstance(pq, str) and pq.strip():
        for sid in ACTIVE_LANES.values():
            if sid not in pq:
                errors.append(f"Priority Queue.md does not mention active lane {sid}")
        if "max 3" not in pq.lower() and "max three" not in pq.lower():
            errors.append("Priority Queue.md lost the max-3 active-song cap")

    dash = extras.get("dashboard_html")
    if isinstance(dash, str) and dash.strip():
        for sid, title in LANE_TITLES.items():
            if sid in ACTIVE_LANES.values() or sid in PROTECTED_LANES.values():
                if title not in dash:
                    errors.append(f"dashboard is missing lane title {title!r}")
        version = str(cat.get("version") or "")
        if version and f"Catalog v{version}" not in dash:
            errors.append(f"dashboard does not advertise Catalog v{version}")

    audio_hits = extras.get("audio_files")
    if audio_hits:
        errors.append(
            "audio masters must not live in this repo "
            f"(found {audio_hits[:5]}{'…' if len(audio_hits) > 5 else ''})"
        )

    return errors


def find_audio_files(root: str) -> list[str]:
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in AUDIO_EXTS:
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                hits.append(rel)
    return hits


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_repo(root: str | None = None) -> tuple[dict, dict]:
    root = root or HERE
    cat = load_json(os.path.join(root, "data", "master_catalog.json"))
    extras = {
        "app_api": None,
        "vm_matches": None,
        "priority_queue": None,
        "dashboard_html": None,
        "audio_files": find_audio_files(root),
    }
    api = os.path.join(root, "data", "app_api.json")
    if os.path.exists(api):
        extras["app_api"] = load_json(api)
    vm = os.path.join(root, "01_source_manifests", "voicememo", "vm_matches.json")
    if os.path.exists(vm):
        extras["vm_matches"] = load_json(vm)
    extras["priority_queue"] = load_text(
        os.path.join(root, "00_control_room", "Priority Queue.md")
    )
    extras["dashboard_html"] = load_text(
        os.path.join(root, "Jeff Story Song Vault Dashboard.html")
    )
    return cat, extras


def main() -> int:
    if not os.path.exists(CAT_PATH):
        print(f"ERROR: missing catalog at {CAT_PATH}", file=sys.stderr)
        return 1
    cat, extras = load_repo(HERE)
    errors = validate(cat, extras)
    songs = cat.get("songs") or []
    originals = sum(1 for s in songs if s.get("classification") == "original")
    if errors:
        print(f"catalog INVALID — {len(errors)} error(s)")
        for err in errors:
            print(f"  • {err}")
        return 1
    print(
        f"catalog OK — {len(songs)} entities · {originals} originals · "
        f"lanes {ACTIVE_LANES['flagship']}/"
        f"{ACTIVE_LANES['quick_win']}/"
        f"{ACTIVE_LANES['experimental']} · opus {PROTECTED_LANES['opus']} protected"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
