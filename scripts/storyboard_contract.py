#!/usr/bin/env python3
"""
StoryBoard import contract — what catalog-import.ts actually does.

Inspected 2026-08-26 from rupret007/StoryBoard main after PR #12
(`packages/shared/src/catalog-import.ts`). Vault #7–#11 already lock
the schema-3 published slice, setlist names, catalog counts,
import file vs spine, Show Night-does-not-expand, and never_auto_post.
StoryBoard #12 makes this feed usable from Band operations only as
local JSON: remote catalog URLs are rejected, and a payload that
looks like a locator is not imported.

`data/app_api.json` is the StoryBoard import. `master_catalog.json`
is the spine, not a substitute feed. StoryLiner is promo only.
Nothing auto-posts. Jeff owns feel, set-list, and catalog calls.
Parked catalogs are not a fourth live band. This private catalog
is not a public fetch.
"""
from __future__ import annotations

import json
import re
from typing import NamedTuple

# StoryBoard CATALOG_IMPORT_POLICY_VERSION
CATALOG_IMPORT_POLICY_VERSION = "catalog_import_v1"

# StoryBoard LIVE_CATALOG_PROJECTS / PARKED / BOOKER (normalized).
# When setlist_ready_default_import is present, that published id list is
# the default plan (empty published slice stays empty). Fallback when the
# array is absent: Rad Dad, Jeff Story, or a recorded Rad Dad play — and,
# when setlist_ready is present, only those ids. Parked catalogs that are
# NOT in the published slice stay parked unless Jeff opts in. Phrase
# match: "Something Dirty / Stalemate / Rad Dad" is live (has rad dad)
# and also parked-named — current artist, not a new band.
LIVE_CATALOG_PROJECTS = ("rad dad", "jeff story")
PARKED_CATALOG_PROJECTS = ("stalemate", "trailer swift", "something dirty")
BOOKER_CATALOG_PROJECTS = ("travis", "travis story")
CATALOG_BOOKER_POLICY = "travis_books"

# StoryBoard vaultSetlistIdentity() after #6 (unchanged through #12).
VAULT_DEFAULT_LIVE_SETLIST_NAME = "Vault default-live"
VAULT_SETLIST_READY_SETLIST_NAME = "Vault setlist-ready"
PARKED_NAMED_IN_DEFAULT_LIVE_WARNING = (
    "Published default-live includes songs whose Vault project is a parked "
    "catalog name. They stay on the current artist — not a fourth live band."
)

# StoryBoard #9: Vault payload present → Show Night does not mint a second catalog.
SHOW_NIGHT_NOT_IN_VAULT = "show_night_not_in_vault"
SHOW_NIGHT_DOES_NOT_EXPAND_VAULT = True
VAULT_IMPORT_FILE = "data/app_api.json"
MASTER_CATALOG_IS_NOT_THE_IMPORT = True
NEVER_AUTO_POST = True
# StoryBoard #12: Band operations preview/apply is local JSON only.
LOCAL_JSON_ONLY = True
REMOTE_CATALOG_URLS = False
BAND_OPERATIONS_IMPORT = "Band operations → Music & setlists"
REMOTE_LOCATOR_KEYS = ("url", "href", "sourceUrl", "catalogUrl", "fetch")
DEFAULT_LIVE_SETLIST_NOTES = (
    "Published Vault setlist_ready_default_import / default_live slice. "
    "Current artist only — not a fourth live band. Not a booking pitch. "
    "Lanes are not a setlist. Jeff owns running order."
)
SETLIST_READY_SETLIST_NOTES = (
    "Playable Vault originals already selected for the live band. "
    "Not a booking pitch. Lanes are not a setlist. Jeff owns running order."
)

# StoryBoard CATALOG_IMPORT_SCOPES + travis_books (RECOGNIZED_IMPORT_SCOPES).
CATALOG_IMPORT_SCOPES = (
    "default_live",
    "parked_catalog",
    "not_live_band",
    "not_setlist_ready",
    "cover_not_active",
)
RECOGNIZED_IMPORT_SCOPES = CATALOG_IMPORT_SCOPES + (CATALOG_BOOKER_POLICY,)

# Fields StoryBoard normalizeVaultSong + vaultSongDraft + decideVaultSong read.
# StoryBoard #5 also reads import_scope (publishedDefaultIds / declared scopes).
IMPORTER_READS = (
    "id",
    "title",
    "project",
    "is_original",
    "key",
    "bpm",
    "bpm_int",
    "vault_id",
    "vault_ref",
    "played_live",
    "import_scope",
)
IMPORTER_DOES_NOT_READ = (
    "bpm_raw",
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
    "alt_titles",
)
# Top-level keys planCatalogImport consults on a schema-3 feed.
IMPORTER_CATALOG_READS = (
    "songs",
    "setlist_ready",
    "setlist_ready_default_import",
    "storyboard.field_map",
    "lanes",
)

# Live StoryBoard VAULT_STORYBOARD_FIELD_MAP (schema 3 honesty).
VAULT_STORYBOARD_FIELD_MAP = {
    "title": "title",
    "musicalKey": "key",
    "bpm": "bpm_int",
    "sourceKey": f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{{vault_id ?? id}}",
    "notes": "vault_ref",
    "active": "is_original !== false",
}

# Prisma Song fields StoryBoard has but does not take from this feed.
LEAVE_NULL = ("durationSeconds", "leadVocalist", "genre", "lyricsUrl", "chartUrl")

# StoryBoard vaultSongSchema / vaultSetlistReadySchema limits.
MAX_ID_LEN = 80
MAX_TITLE_LEN = 240
MAX_KEY_LEN = 30
MAX_WRITERS = 20
MAX_NOTES_LEN = 2000
MAX_VAULT_REF_LEN = 120
MAX_PLAYED_LIVE = 50
MAX_SONGS = 2000
MAX_IMPORT_SCOPE_LEN = 40
BPM_MIN = 20
BPM_MAX = 400

SCOPE_DEFAULT_LIVE = "default_live"
SCOPE_PARKED = "parked_catalog"
SCOPE_NOT_LIVE = "not_live_band"
SCOPE_NOT_READY = "not_setlist_ready"
SCOPE_BOOKER = "travis_books"
SCOPE_COVER = "cover_not_active"

SKIP_REASON_TO_COUNT = {
    SCOPE_PARKED: "storyboard_parked",
    SCOPE_NOT_LIVE: "storyboard_not_live_band",
    SCOPE_NOT_READY: "storyboard_not_setlist_ready",
    SCOPE_BOOKER: "storyboard_booker",
    SCOPE_COVER: "storyboard_cover",
}


class Decision(NamedTuple):
    include: bool
    reason: str


def normalize_project(value) -> str:
    """Match StoryBoard normalizeProject()."""
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def project_tokens(value) -> set[str]:
    """Match StoryBoard projectTokens()."""
    return {part for part in normalize_project(value).split(" ") if part}


def has_phrase(tokens: set[str], phrase: str) -> bool:
    """Match StoryBoard hasPhrase()."""
    return all(part in tokens for part in phrase.split(" ") if part)


def is_live_project(project) -> bool:
    """Match StoryBoard isLiveProject() — exact or phrase (rad dad / jeff story)."""
    normalized = normalize_project(project)
    if normalized in LIVE_CATALOG_PROJECTS:
        return True
    tokens = project_tokens(project)
    return has_phrase(tokens, "rad dad") or has_phrase(tokens, "jeff story")


def as_text(value):
    """Match StoryBoard asText() — non-empty trim, or finite number."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float) and value == value and value not in (
        float("inf"),
        float("-inf"),
    ):
        return str(int(value)) if value.is_integer() else str(value)
    return None


def catalog_locator_looks_remote(value) -> bool:
    """Match StoryBoard catalogLocatorLooksRemote() after #12.

    A string with a scheme:// or protocol-relative // is remote.
    A record is remote when url / href / sourceUrl / catalogUrl / fetch
    is itself a remote locator. StoryBoard then refuses the payload.
    """
    if isinstance(value, str):
        trimmed = value.strip()
        return bool(re.match(r"^[a-z][a-z0-9+.-]*://", trimmed, re.I)) or (
            trimmed.startswith("//")
        )
    if isinstance(value, dict):
        return any(
            catalog_locator_looks_remote(value.get(key)) for key in REMOTE_LOCATOR_KEYS
        )
    return False


def parse_local_catalog_json(text, label: str = "catalog"):
    """Match StoryBoard parseLocalCatalogJson() after #12.

    Empty text → None. A URL string or a JSON object that looks like a
    remote locator raises ValueError. Valid local JSON is returned.
    """
    trimmed = str(text or "").strip()
    if not trimmed:
        return None
    if catalog_locator_looks_remote(trimmed):
        raise ValueError(f"{label} must be local JSON, not a URL")
    try:
        parsed = json.loads(trimmed)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be valid JSON") from exc
    if catalog_locator_looks_remote(parsed):
        raise ValueError(f"{label} must be local JSON, not a URL")
    return parsed


def recognized_import_scope(declared=None) -> str | None:
    """Match StoryBoard recognizedImportScope()."""
    text = as_text(declared)
    if not text:
        return None
    normalized = re.sub(r"[^a-z0-9]+", "_", text.lower())
    if normalized in RECOGNIZED_IMPORT_SCOPES:
        return normalized
    return None


def catalog_import_scope(project, declared=None) -> str:
    """Match StoryBoard catalogImportScope() — project + declared, no played_live."""
    if is_booker_project(project):
        return CATALOG_BOOKER_POLICY
    declared_scope = recognized_import_scope(declared)
    if declared_scope:
        return declared_scope
    if is_live_project(project):
        return SCOPE_DEFAULT_LIVE
    if is_parked_project(project):
        return SCOPE_PARKED
    return SCOPE_NOT_LIVE


def project_name_looks_parked(project) -> bool:
    """Match StoryBoard projectNameLooksParked() — name only, not declared scope."""
    normalized = normalize_project(project)
    if normalized in PARKED_CATALOG_PROJECTS:
        return True
    tokens = project_tokens(project)
    return (
        "stalemate" in tokens
        or has_phrase(tokens, "trailer swift")
        or has_phrase(tokens, "something dirty")
    )


def is_parked_project(project, declared=None) -> bool:
    """Match StoryBoard isParkedProject() — declared parked_catalog wins."""
    if recognized_import_scope(declared) == SCOPE_PARKED:
        return True
    return project_name_looks_parked(project)


def vault_setlist_identity(used_published_default: bool) -> dict:
    """Match StoryBoard vaultSetlistIdentity() after #6."""
    if used_published_default:
        return {
            "name": VAULT_DEFAULT_LIVE_SETLIST_NAME,
            "notes": clip_notes(DEFAULT_LIVE_SETLIST_NOTES),
        }
    return {
        "name": VAULT_SETLIST_READY_SETLIST_NAME,
        "notes": clip_notes(SETLIST_READY_SETLIST_NOTES),
    }


def parked_named_default_live_ids(songs: list[dict], published_ids) -> list[str]:
    """Published-slice ids whose Vault project name looks parked (StoryBoard #6)."""
    by_id = {song.get("id"): song for song in songs if isinstance(song, dict)}
    out: list[str] = []
    for sid in published_ids:
        rec = by_id.get(sid)
        if rec and project_name_looks_parked(rec.get("project")):
            out.append(sid)
    return out


def normalize_spine_song(src: dict) -> dict:
    """Match StoryBoard normalizeVaultCatalog() on a master_catalog row.

    The spine is not the StoryBoard feed: `live_presence` is not remapped
    to `played_live`, and there is no published slice / import_scope.
    """
    sid = as_text(src.get("id")) or as_text(src.get("song_id")) or as_text(
        src.get("vault_id")
    )
    title = as_text(src.get("title")) or as_text(src.get("canonical_title"))
    project = as_text(src.get("project")) or as_text(src.get("artist_project"))
    vault_id = as_text(src.get("vault_id")) or sid
    rec = dict(src)
    if sid:
        rec["id"] = sid
    if title:
        rec["title"] = title
    if project:
        rec["project"] = project
    if vault_id:
        rec["vault_id"] = vault_id
        rec["vault_ref"] = as_text(src.get("vault_ref")) or vault_ref_for(vault_id)
    is_original = src.get("is_original")
    if not isinstance(is_original, bool):
        classification = (as_text(src.get("classification")) or "").lower()
        if classification == "original":
            is_original = True
        elif classification == "cover":
            is_original = False
        else:
            is_original = None
    if isinstance(is_original, bool):
        rec["is_original"] = is_original
    elif "is_original" in rec:
        rec.pop("is_original", None)
    # StoryBoard does not remap catalog live_presence → played_live.
    rec.pop("played_live", None)
    rec.pop("import_scope", None)
    return rec


def spine_default_plan_ids(catalog_songs: list[dict]) -> list[str]:
    """What StoryBoard would keep if pointed at master_catalog.json."""
    songs = [normalize_spine_song(src) for src in catalog_songs if isinstance(src, dict)]
    out: list[str] = []
    for song, decision in default_decisions(songs, set()):
        if decision.include and song.get("id"):
            out.append(song["id"])
    return out


def vault_skip_by_title(
    songs: list[dict],
    ready_ids: set[str],
    published_default_ids: set[str] | None,
) -> dict[str, str]:
    """StoryBoard #9 vaultSkipByTitle — skip reason keyed by cleaned title."""
    skip: dict[str, str] = {}
    for song, decision in live_default_decisions(
        songs, ready_ids, published_default_ids
    ):
        if decision.include:
            continue
        title = clean_title(song.get("title") or "")
        if title:
            skip[title.lower()] = decision.reason
    return skip


def planned_vault_titles(
    songs: list[dict],
    ready_ids: set[str],
    published_default_ids: set[str] | None,
) -> dict[str, str]:
    """Cleaned title → vault id for songs StoryBoard #9 would keep."""
    planned: dict[str, str] = {}
    for song, decision in live_default_decisions(
        songs, ready_ids, published_default_ids
    ):
        if not decision.include:
            continue
        title = clean_title(song.get("title") or "")
        sid = song.get("id")
        if title and sid:
            planned[title.lower()] = sid
    return planned


def show_night_bind_title(
    title,
    planned_titles: dict[str, str],
    skip_by_title: dict[str, str],
    *,
    vault_catalog_resolved: bool = True,
) -> tuple[str, str]:
    """Match StoryBoard #9 showNightSongSourceKey() when a Vault payload is present.

    Returns (action, detail):
      bind + vault id when the cleaned title is already planned
      skip + Vault reason (or show_night_not_in_vault) otherwise

    Show Night-only imports (no Vault file) are unchanged and out of scope.
    """
    cleaned = clean_title(title)
    key = cleaned.lower()
    if not vault_catalog_resolved:
        return ("mint_show_night", cleaned)
    if key in planned_titles:
        return ("bind", planned_titles[key])
    return ("skip", skip_by_title.get(key, SHOW_NIGHT_NOT_IN_VAULT))


def is_booker_project(project) -> bool:
    """Match StoryBoard isBookerProject() — Travis books, never auto-pitch."""
    normalized = normalize_project(project)
    if normalized in BOOKER_CATALOG_PROJECTS:
        return True
    return "travis" in project_tokens(project)


def played_live_from_presence(events) -> list[str]:
    """Catalog live_presence → StoryBoard played_live strings."""
    if not isinstance(events, list):
        return []
    out: list[str] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        band = event.get("band")
        date = event.get("date")
        if band and date:
            out.append(f"{band} ({date})")
    return out


def played_live_by_rad_dad(played_live) -> bool:
    """Match StoryBoard playedLiveByRadDad()."""
    if not isinstance(played_live, list):
        return False
    return any(re.search(r"rad\s*dad", str(row), re.I) for row in played_live)


def is_live_repertoire(project, played_live=None) -> bool:
    return is_live_project(project) or played_live_by_rad_dad(played_live)


def import_scope(project, played_live=None, *, is_original=True, in_ready_set=False,
                 has_ready_list=False) -> str:
    """Default-import decision reason (includeParked/includeAllProjects off)."""
    decision = decide_vault_song(
        {
            "project": project,
            "played_live": played_live or [],
            "is_original": is_original,
        },
        has_ready_list=has_ready_list,
        in_ready_set=in_ready_set,
    )
    return SCOPE_DEFAULT_LIVE if decision.include else decision.reason


def decide_vault_song(
    song: dict,
    *,
    include_parked: bool = False,
    include_all_projects: bool = False,
    has_ready_list: bool = False,
    in_ready_set: bool = False,
    published_default_ids: set[str] | None = None,
    has_declared_scopes: bool = False,
) -> Decision:
    """Match StoryBoard decideVaultSong() after #5.

    Export computes the slice with published_default_ids=None and
    has_declared_scopes=False (the #4 fallback). Live StoryBoard prefers
    the published setlist_ready_default_import id set when that array is
    present — including when it is empty.
    """
    project = song.get("project")
    declared = recognized_import_scope(song.get("import_scope"))
    if is_booker_project(project) or declared == CATALOG_BOOKER_POLICY:
        return Decision(False, SCOPE_BOOKER)
    if not include_all_projects and (
        song.get("is_original") is False or declared == SCOPE_COVER
    ):
        return Decision(False, SCOPE_COVER)
    if include_all_projects:
        return Decision(True, "include_all")

    parked = is_parked_project(project, song.get("import_scope"))
    live = is_live_repertoire(project, song.get("played_live"))

    if published_default_ids is not None:
        if song.get("id") in published_default_ids:
            return Decision(True, SCOPE_DEFAULT_LIVE)
        if include_parked and parked:
            return Decision(True, "include_parked")
        if declared and declared != SCOPE_DEFAULT_LIVE:
            return Decision(False, declared)
        if parked:
            return Decision(False, SCOPE_PARKED)
        reason = (
            SCOPE_NOT_READY
            if has_ready_list or len(published_default_ids) == 0
            else SCOPE_NOT_LIVE
        )
        return Decision(False, reason)

    if has_declared_scopes:
        scope = catalog_import_scope(project, song.get("import_scope"))
        if scope == SCOPE_DEFAULT_LIVE:
            return Decision(True, SCOPE_DEFAULT_LIVE)
        if scope == SCOPE_PARKED:
            if include_parked:
                return Decision(True, "include_parked")
            return Decision(False, SCOPE_PARKED)
        return Decision(False, scope)

    if has_ready_list and in_ready_set:
        if parked and not live and not include_parked:
            return Decision(False, SCOPE_PARKED)
        if not live and not parked:
            return Decision(False, SCOPE_NOT_LIVE)
        return Decision(True, SCOPE_DEFAULT_LIVE)

    if has_ready_list and not in_ready_set:
        if include_parked and parked:
            return Decision(True, "include_parked")
        return Decision(False, SCOPE_NOT_READY)

    if parked and not live and not include_parked:
        return Decision(False, SCOPE_PARKED)
    if not live and not parked:
        return Decision(False, SCOPE_NOT_LIVE)
    return Decision(True, SCOPE_DEFAULT_LIVE)


def default_decisions(songs: list[dict], ready_ids: set[str]) -> list[tuple[dict, Decision]]:
    """Fallback plan used to *compute* the published slice (no published ids)."""
    has_ready = bool(ready_ids)
    out: list[tuple[dict, Decision]] = []
    for song in songs:
        sid = song.get("id")
        out.append(
            (
                song,
                decide_vault_song(
                    song,
                    has_ready_list=has_ready,
                    in_ready_set=sid in ready_ids,
                ),
            )
        )
    return out


def live_default_decisions(
    songs: list[dict],
    ready_ids: set[str],
    published_default_ids: set[str] | None,
) -> list[tuple[dict, Decision]]:
    """Live StoryBoard #5 default plan (includeParked/includeAllProjects false).

    published_default_ids is None when setlist_ready_default_import is absent.
    An empty set means the array is present and empty — import stays empty.
    """
    has_ready = bool(ready_ids)
    has_declared = any(recognized_import_scope(s.get("import_scope")) for s in songs)
    out: list[tuple[dict, Decision]] = []
    for song in songs:
        sid = song.get("id")
        out.append(
            (
                song,
                decide_vault_song(
                    song,
                    has_ready_list=has_ready,
                    in_ready_set=sid in ready_ids,
                    published_default_ids=published_default_ids,
                    has_declared_scopes=has_declared,
                ),
            )
        )
    return out


def source_key(song_id: str) -> str:
    """StoryBoard constructs this from vault_id ?? id."""
    return f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{song_id}"


def vault_ref_for(song_id: str) -> str:
    return f"vault:{song_id}"


def _js_integer(value):
    """JS typeof === 'number' && Number.isInteger(value). Python bool is not a number."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def bpm_int(raw):
    """Leading 2–3 digit tempo for export `bpm` / `bpm_int`. Else null.

    StoryBoard parseBpm prefers a clean `bpm_int`, then a clean `bpm`
    integer, then a leading 2–3 digit tempo on a `bpm` string.
    Annotated catalog values like "214 (cut)" are stored on `bpm_raw`.
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return None
    parsed = _js_integer(raw)
    if parsed is not None:
        return parsed if BPM_MIN <= parsed <= BPM_MAX else None
    m = re.match(r"\s*(\d{2,3})\b", str(raw))
    if not m:
        return None
    n = int(m.group(1))
    return n if BPM_MIN <= n <= BPM_MAX else None


def parse_bpm(song: dict):
    """Exact StoryBoard parseBpm(song): bpm_int first, then bpm, never guess."""
    bpm_int_value = _js_integer(song.get("bpm_int"))
    if bpm_int_value is not None and BPM_MIN <= bpm_int_value <= BPM_MAX:
        return bpm_int_value
    bpm_value = song.get("bpm")
    parsed = _js_integer(bpm_value)
    if parsed is not None and BPM_MIN <= parsed <= BPM_MAX:
        return parsed
    if isinstance(bpm_value, str):
        match = re.match(r"^(\d{2,3})\b", bpm_value.strip())
        if not match:
            return None
        n = int(match.group(1))
        if BPM_MIN <= n <= BPM_MAX:
            return n
    return None


def storyboard_parse_bpm(value):
    """parseBpm against a lone bpm field (no bpm_int)."""
    return parse_bpm({"bpm": value})


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


def clean_title(value) -> str:
    """Match StoryBoard cleanTitle() — strip arrows, collapse space."""
    return re.sub(r"\s+", " ", str(value or "").replace("→", "")).strip()


def clip_notes(value: str) -> str:
    return value[:MAX_NOTES_LEN]


def imported_notes(vault_ref, song_id: str) -> str:
    """Notes StoryBoard writes: vault_ref ?? vault:{id}."""
    text = str(vault_ref).strip() if vault_ref else ""
    return clip_notes(text or vault_ref_for(song_id))


def imported_active(is_original) -> bool:
    """StoryBoard: active = is_original !== false."""
    return is_original is not False


def storyboard_mapping(default_live_parked_named_ids=None) -> dict:
    """Honest mapping object published on app_api.json → storyboard."""
    parked_named_ids = list(default_live_parked_named_ids or [])
    return {
        "consumer": "StoryBoard",
        "importer": "rupret007/StoryBoard packages/shared/src/catalog-import.ts",
        "inspected": "2026-08-26 after StoryBoard #12",
        "policy_version": CATALOG_IMPORT_POLICY_VERSION,
        "import_from": "songs",
        "import_file": VAULT_IMPORT_FILE,
        "master_catalog_is_not_the_import": MASTER_CATALOG_IS_NOT_THE_IMPORT,
        "local_json_only": LOCAL_JSON_ONLY,
        "remote_catalog_urls": REMOTE_CATALOG_URLS,
        "band_operations_import": BAND_OPERATIONS_IMPORT,
        "setlist_seed": "setlist_ready",
        "second_catalog": False,
        "not_band_os": ["StoryDesk", "StoryOps"],
        "not_catalog_consumer": ["StoryLiner", "Andrea-Assistant", "StoryDesk", "StoryOps"],
        "storyliner_role": "promo only",
        "no_fourth_live_band": True,
        "do_not_invent_live_band": True,
        "never_auto_post": NEVER_AUTO_POST,
        "show_night_does_not_expand_vault": SHOW_NIGHT_DOES_NOT_EXPAND_VAULT,
        "show_night_binds_planned_vault_titles_only": True,
        "booker_policy": CATALOG_BOOKER_POLICY,
        "prefers_published_default_import": True,
        "empty_published_slice_stays_empty": True,
        "parked_named_in_default_live_stay_current_artist": True,
        "default_live_setlist_name": VAULT_DEFAULT_LIVE_SETLIST_NAME,
        "setlist_ready_setlist_name": VAULT_SETLIST_READY_SETLIST_NAME,
        "default_live_setlist_notes": vault_setlist_identity(True)["notes"],
        "setlist_ready_setlist_notes": vault_setlist_identity(False)["notes"],
        "parked_named_in_default_live_warning": PARKED_NAMED_IN_DEFAULT_LIVE_WARNING,
        "default_live_parked_named_ids": parked_named_ids,
        "reads": list(IMPORTER_READS),
        "does_not_read": list(IMPORTER_DOES_NOT_READ),
        "catalog_reads": list(IMPORTER_CATALOG_READS),
        "field_map": dict(VAULT_STORYBOARD_FIELD_MAP),
        "leave_null": list(LEAVE_NULL),
        "why_null": (
            "durationSeconds, leadVocalist, genre, lyricsUrl, and chartUrl "
            "are not in the vault. Do not invent them. Jeff owns feel, "
            "set-list, and catalog calls."
        ),
        "merge_key": f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{{vault_id ?? id}}",
        "bpm_note": (
            "StoryBoard parseBpm prefers songs[].bpm_int (clean integer 20–400), "
            "then songs[].bpm as an integer, then a leading 2–3 digit tempo. "
            "`bpm` and `bpm_int` are the same pre-parsed integer. `bpm_raw` "
            "keeps catalog text such as '214 (cut)'."
        ),
        "live_catalog_projects": ["Rad Dad", "Jeff Story"],
        "parked_catalog_projects": ["Stalemate", "Trailer Swift", "Something Dirty"],
        "booker_catalog_projects": ["Travis", "Travis Story"],
        "default_import": (
            "THE import file is data/app_api.json — master_catalog.json is the "
            "spine, not a StoryBoard feed. StoryBoard #12 accepts this file "
            "only as local JSON (Band operations → Music & setlists). Remote "
            "catalog URLs are rejected. This private catalog is not a public "
            "fetch. Published setlist_ready_default_import is the default plan "
            "when present (empty published slice stays empty — StoryBoard will "
            "not recompute a live band). StoryBoard names that draft setlist "
            "'Vault default-live'. Songs whose Vault project is a parked "
            "catalog name stay on the current artist — not a fourth live band. "
            "Fallback when that array is absent: live repertoire (Rad Dad / "
            "Jeff Story / recorded Rad Dad plays) gated by setlist_ready; that "
            "draft is 'Vault setlist-ready'. Parked catalogs that are not in "
            "the published slice stay parked unless Jeff passes includeParked "
            "/ includeAllProjects. Covers stay out. Travis rows are "
            "travis_books — never auto-pitch. When a Vault payload is present, "
            "Show Night only binds planned Vault titles and does not mint "
            "excluded rows or fill an empty published slice. Nothing auto-posts. "
            "Jeff owns feel, set-list, and catalog calls. Do not invent Rad "
            "Dad catalog rows or a fourth live band."
        ),
        "active_lanes": ["flagship", "quick_win", "experimental"],
        "active_lane_cap": 3,
        "protected_opus": "JS-0107",
        "setlist": {
            "seed_from": "setlist_ready",
            "default_import_from": "setlist_ready_default_import",
            "prefers_default_import_from": True,
            "default_import_name": VAULT_DEFAULT_LIVE_SETLIST_NAME,
            "opt_in_name": VAULT_SETLIST_READY_SETLIST_NAME,
            "item_type": "song",
            "link_by": f"vault:{CATALOG_IMPORT_POLICY_VERSION}:{{vault_id ?? id}}",
            "jeff_owns_order": True,
            "do_not_invent": ["breaks", "running_order", "lead_vocalist", "duration"],
        },
        "ops": {
            "write_back": "events/",
            "show_played_songs": "vault_id preferred, title fallback",
            "lanes_are_not_a_setlist": True,
            "remote_catalog_urls": False,
            "local_json_only": True,
            "band_operations_import": BAND_OPERATIONS_IMPORT,
            "never_auto_post": True,
            "show_night_does_not_expand_vault": True,
            "jeff_owns_catalog_calls": True,
        },
    }
