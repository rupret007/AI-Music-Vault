#!/usr/bin/env python3
"""
StoryBoard import contract — fields the StoryBoard importer actually reads.

Inspected 2026-08-23 from rupret007/StoryBoard
`packages/shared/src/catalog-import.ts` (main + vault-import-honesty draft).

Vault remains the catalog. StoryBoard remains the band OS.
StoryLiner is promo only. Do not invent a fourth live band.
"""
from __future__ import annotations

import re

# StoryBoard CATALOG_IMPORT_POLICY_VERSION
CATALOG_IMPORT_POLICY_VERSION = "catalog_import_v1"

# StoryBoard LIVE_CATALOG_PROJECTS / PARKED_CATALOG_PROJECTS (normalized).
# Default import is Rad Dad only. Parked catalogs stay parked unless Jeff
# opts in on the StoryBoard side. Hybrid labels (e.g. "Stalemate / Rad Dad")
# do not become a live band — StoryBoard treats them as not_live_band.
LIVE_CATALOG_PROJECTS = ("rad dad",)
PARKED_CATALOG_PROJECTS = ("stalemate", "trailer swift", "something dirty")

IMPORTER_READS = ("id", "title", "project", "is_original", "key", "bpm")
IMPORTER_DOES_NOT_READ = (
    "bpm_int",
    "bpm_raw",
    "vault_ref",
    "vault_id",
    "source_key",
    "potential",
    "readiness",
    "momentum",
    "ai_upload_ok",
    "ai_upload_note",
    "duration_seconds",
    "leadVocalist",
    "theme",
    "hook",
    "next_action",
    "stage",
    "writers",
    "import_scope",
)

# Prisma Song fields StoryBoard has but does not take from this feed.
LEAVE_NULL = ("durationSeconds", "leadVocalist", "genre", "lyricsUrl", "chartUrl")

# StoryBoard songCreateSchema / vaultSongSchema limits.
MAX_ID_LEN = 80
MAX_TITLE_LEN = 240
MAX_KEY_LEN = 30
MAX_WRITERS = 20
MAX_NOTES_LEN = 2000
BPM_MIN = 20
BPM_MAX = 400

SCOPE_DEFAULT_LIVE = "default_live"
SCOPE_PARKED = "parked_catalog"
SCOPE_NOT_LIVE = "not_live_band"


def normalize_project(value) -> str:
    """Match StoryBoard normalizeProject()."""
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def import_scope(project) -> str:
    """What StoryBoard's default import does with this artist_project."""
    normalized = normalize_project(project)
    if normalized in LIVE_CATALOG_PROJECTS:
        return SCOPE_DEFAULT_LIVE
    if normalized in PARKED_CATALOG_PROJECTS:
        return SCOPE_PARKED
    return SCOPE_NOT_LIVE


def source_key(song_id: str) -> str:
    """StoryBoard constructs this; it does not read it from the JSON."""
    return f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{song_id}"


def bpm_int(raw):
    """Leading 2–3 digit tempo for the StoryBoard `bpm` field. Else null.

    StoryBoard parseBpm only accepts a clean integer / integer-string.
    Annotated catalog values like "214 (cut)" would import as null unless
    we pre-parse them into `bpm` and keep the annotation on `bpm_raw`.
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        n = int(raw)
        return n if BPM_MIN <= n <= BPM_MAX else None
    m = re.match(r"\s*(\d{2,3})\b", str(raw))
    if not m:
        return None
    n = int(m.group(1))
    return n if BPM_MIN <= n <= BPM_MAX else None


def storyboard_parse_bpm(value):
    """Exact StoryBoard parseBpm() behavior (catalog-import.ts)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if BPM_MIN <= value <= BPM_MAX else None
    if isinstance(value, float):
        if value.is_integer() and BPM_MIN <= int(value) <= BPM_MAX:
            return int(value)
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = float(text)
        except ValueError:
            return None
        if parsed.is_integer() and BPM_MIN <= int(parsed) <= BPM_MAX:
            return int(parsed)
    return None


def bpm_raw_string(raw) -> str:
    if raw is None or raw == "":
        return ""
    if isinstance(raw, bool):
        return ""
    if isinstance(raw, int):
        return str(raw)
    if isinstance(raw, float):
        return str(int(raw)) if raw.is_integer() else str(raw)
    return str(raw)


def storyboard_parse_key(value) -> str | None:
    """StoryBoard parseKey(): trim, empty → null, else first 30 chars."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:MAX_KEY_LEN]


def constructed_notes(song_id: str, project, is_original) -> str:
    """Notes StoryBoard writes — not vault_ref."""
    parts = [f"source {song_id}"]
    if project:
        parts.append(str(project))
    if is_original is True:
        parts.append("original")
    elif is_original is False:
        parts.append("not original")
    return " · ".join(parts)[:MAX_NOTES_LEN]


def storyboard_mapping() -> dict:
    """Honest mapping object published on app_api.json → storyboard."""
    return {
        "consumer": "StoryBoard",
        "importer": "rupret007/StoryBoard packages/shared/src/catalog-import.ts",
        "policy_version": CATALOG_IMPORT_POLICY_VERSION,
        "import_from": "songs",
        "setlist_seed": "setlist_ready",
        "second_catalog": False,
        "not_band_os": ["StoryDesk", "StoryOps"],
        "not_catalog_consumer": ["StoryLiner", "Andrea-Assistant", "StoryDesk", "StoryOps"],
        "storyliner_role": "promo only",
        "no_fourth_live_band": True,
        "do_not_invent_live_band": True,
        "reads": list(IMPORTER_READS),
        "does_not_read": list(IMPORTER_DOES_NOT_READ),
        "field_map": {
            "title": "title",
            "musicalKey": "key",
            "bpm": "bpm",
            "sourceKey": f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{{id}}",
            "notes": "constructed: source {id} · {project} · original|not original",
            "active": "always true on import — not is_original",
        },
        "leave_null": list(LEAVE_NULL),
        "why_null": (
            "durationSeconds, leadVocalist, genre, lyricsUrl, and chartUrl "
            "are not in the vault. Do not invent them. Jeff owns feel and set-list."
        ),
        "merge_key": f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{{id}}",
        "bpm_note": (
            "StoryBoard parseBpm accepts only a clean integer 20–400. "
            "`bpm` is pre-parsed (leading tempo). `bpm_raw` keeps catalog text "
            "such as '214 (cut)'. `bpm_int` is a compat alias; the importer "
            "does not read it."
        ),
        "live_catalog_projects": ["Rad Dad"],
        "parked_catalog_projects": ["Stalemate", "Trailer Swift", "Something Dirty"],
        "default_import": (
            "Rad Dad rows only. This vault currently labels no song "
            "artist_project as Rad Dad — live_presence is not artist_project. "
            "Do not invent Rad Dad catalog rows. Jeff opts in with "
            "includeParked / includeAllProjects on the StoryBoard side."
        ),
        "active_lanes": ["flagship", "quick_win", "experimental"],
        "active_lane_cap": 3,
        "protected_opus": "JS-0107",
        "setlist": {
            "seed_from": "setlist_ready",
            "default_import_from": "setlist_ready_default_import",
            "item_type": "song",
            "link_by": f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{{id}}",
            "jeff_owns_order": True,
            "do_not_invent": ["breaks", "running_order", "lead_vocalist", "duration"],
        },
        "ops": {
            "write_back": "events/",
            "show_played_songs": "vault_id preferred, title fallback",
            "lanes_are_not_a_setlist": True,
            "remote_catalog_urls": False,
        },
    }
