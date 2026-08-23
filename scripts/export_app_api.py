#!/usr/bin/env python3
"""
export_app_api.py — the StoryBoard import feed.

Vault (data/master_catalog.json) is the song brain.
StoryBoard is the band-management OS that consumes it.
This script publishes ONE slim, stable-schema file — data/app_api.json —
so StoryBoard does not hand-enter songs and we do not invent a second catalog.

Not StoryDesk. Not StoryOps. No new app in this repo.

Run:  python3 scripts/export_app_api.py
Out:  data/app_api.json
"""
import json, os, re, datetime

SCHEMA_VERSION = 1
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

# StoryBoard Song (prisma): title, durationSeconds?, musicalKey?, bpm?,
# leadVocalist?, genre?, notes?, lyricsUrl?, chartUrl?, active
STORYBOARD = {
    "consumer": "StoryBoard",
    "import_from": "songs",
    "setlist_seed": "setlist_ready",
    "second_catalog": False,
    "not_band_os": ["StoryDesk", "StoryOps"],
    "field_map": {
        "title": "title",
        "musicalKey": "key",
        "bpm": "bpm_int",
        "active": "is_original",
        "notes": "vault_ref",
    },
    "leave_null": ["durationSeconds", "leadVocalist"],
    "why_null": (
        "durationSeconds and leadVocalist are not in the vault. "
        "Do not invent them. Jeff owns feel and set-list."
    ),
    "merge_key": "vault_id",
    "active_lanes": ["flagship", "quick_win", "experimental"],
    "active_lane_cap": 3,
    "protected_opus": "JS-0107",
    # StoryBoard Setlist + ops consume the same feed. Jeff owns order/feel.
    "setlist": {
        "seed_from": "setlist_ready",
        "item_type": "song",
        "link_by": "vault_id",
        "jeff_owns_order": True,
        "do_not_invent": ["breaks", "running_order", "lead_vocalist", "duration"],
    },
    "ops": {
        "write_back": "events/",
        "show_played_songs": "vault_id preferred, title fallback",
        "lanes_are_not_a_setlist": True,
    },
}


def bpm_int(raw):
    """StoryBoard wants Int?. Parse a leading 2–3 digit tempo; else null."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        n = int(raw)
        return n if 20 <= n <= 400 else None
    m = re.match(r"\s*(\d{2,3})\b", str(raw))
    if not m:
        return None
    n = int(m.group(1))
    return n if 20 <= n <= 400 else None


def main():
    cat = json.load(open(CAT))
    songs = []
    for s in cat["songs"]:
        gate = s.get("ai_upload_ok", "") or ""
        sid = s["song_id"]
        songs.append({
            "id": sid,
            "vault_id": sid,
            "vault_ref": f"vault:{sid}",
            "title": s["canonical_title"],
            "alt_titles": s.get("alt_titles", []),
            "project": s.get("artist_project", ""),
            "is_original": s.get("classification") == "original",
            "writers": s.get("writers", []),
            "key": s.get("key", "") or "",
            "bpm": s.get("bpm", "") or "",
            "bpm_int": bpm_int(s.get("bpm")),
            "duration_seconds": None,
            "potential": s.get("potential"),
            "readiness": s.get("readiness"),
            "momentum": s.get("momentum"),
            "last_activity": s.get("last_activity", ""),
            "live_latest": s.get("live_latest", ""),
            "played_live": [f"{e['band']} ({e['date']})"
                            for e in s.get("live_presence", [])],
            "stage": s.get("stage", ""),
            "theme": s.get("theme", ""),
            "hook": s.get("hook", ""),
            "next_action": s.get("next_action", ""),
            # machine-readable rights gate: only True means an AI service is OK,
            # and only for Jeff's SOLO recordings, privately. See README rule 3.
            "ai_upload_ok": gate.startswith("YES"),
            "ai_upload_note": gate,
        })

    originals = [s for s in songs if s["is_original"]]
    setlist_ready = sorted(
        [s for s in originals if s["key"]],
        key=lambda s: -(s["momentum"] or 0))

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated": datetime.date.today().isoformat(),
        "catalog_version": cat.get("version", ""),
        "primary_consumer": "StoryBoard",
        "counts": {
            "entities": len(songs),
            "originals": len(originals),
            "scored": sum(1 for s in songs if s["potential"]),
            "ai_upload_ok": sum(1 for s in songs if s["ai_upload_ok"]),
        },
        "lanes": LANES,
        "storyboard": STORYBOARD,
        "songs": songs,
        "setlist_ready": [{"id": s["id"], "title": s["title"], "key": s["key"],
                           "project": s["project"], "bpm_int": s["bpm_int"],
                           "vault_ref": s["vault_ref"]} for s in setlist_ready],
        "notes": {
            "scores": "potential = how good; readiness = how close to done; "
                      "momentum = how alive in Jeff's hands. Never merge them.",
            "rights": "ai_upload_ok=false means NEVER send this song's audio or "
                      "lyrics to an AI music service. Covers, co-writes and "
                      "collaborators' songs are all false.",
            "audio": "No audio lives in this repo. Masters stay local + Drive.",
            "storyboard_import": (
                "PRIMARY PATH: StoryBoard imports THIS file. Use songs[] "
                "(or setlist_ready for keyed originals). See the storyboard "
                "object for the Song-model field map. Do not create "
                "StoryDesk/StoryOps as a band OS. Do not invent a second "
                "catalog. Three active songs only; Blue Skies Fade is protected."
            ),
        },
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)
    c = payload["counts"]
    print(f"wrote {OUT}")
    print(f"  {c['entities']} entities · {c['originals']} originals · "
          f"{c['scored']} scored · {c['ai_upload_ok']} AI-eligible")
    print(f"  {len(setlist_ready)} setlist-ready originals (have a known key)")
    print("  primary consumer: StoryBoard (same songs[] — no second catalog)")


if __name__ == "__main__":
    main()
