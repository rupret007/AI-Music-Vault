#!/usr/bin/env python3
"""
export_app_api.py — publishes a slim, stable-schema feed of the song catalog
for Jeff's other apps (Andrea assistant, Rad Dad Show Night, RadDadSite, WebJam).

The full master_catalog.json is rich and changes shape as the project learns.
This exports the SUBSET that apps should depend on, with a versioned schema so
an app written today keeps working when the catalog gains new fields.

Run:  python3 scripts/export_app_api.py
Out:  data/app_api.json
"""
import json, os, datetime

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


def main():
    cat = json.load(open(CAT))
    songs = []
    for s in cat["songs"]:
        gate = s.get("ai_upload_ok", "") or ""
        songs.append({
            "id": s["song_id"],
            "title": s["canonical_title"],
            "alt_titles": s.get("alt_titles", []),
            "project": s.get("artist_project", ""),
            "is_original": s.get("classification") == "original",
            "writers": s.get("writers", []),
            "key": s.get("key", "") or "",
            "bpm": s.get("bpm", "") or "",
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
        "counts": {
            "entities": len(songs),
            "originals": len(originals),
            "scored": sum(1 for s in songs if s["potential"]),
            "ai_upload_ok": sum(1 for s in songs if s["ai_upload_ok"]),
        },
        "lanes": LANES,
        "songs": songs,
        "setlist_ready": [{"id": s["id"], "title": s["title"], "key": s["key"],
                           "project": s["project"]} for s in setlist_ready],
        "notes": {
            "scores": "potential = how good; readiness = how close to done; "
                      "momentum = how alive in Jeff's hands. Never merge them.",
            "rights": "ai_upload_ok=false means NEVER send this song's audio or "
                      "lyrics to an AI music service. Covers, co-writes and "
                      "collaborators' songs are all false.",
            "audio": "No audio lives in this repo. Masters stay local + Drive.",
        },
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)
    c = payload["counts"]
    print(f"wrote {OUT}")
    print(f"  {c['entities']} entities · {c['originals']} originals · "
          f"{c['scored']} scored · {c['ai_upload_ok']} AI-eligible")
    print(f"  {len(setlist_ready)} setlist-ready originals (have a known key)")


if __name__ == "__main__":
    main()
