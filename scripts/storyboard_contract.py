#!/usr/bin/env python3
"""
StoryBoard import contract — what catalog-import.ts actually does.

Inspected 2026-08-27 from rupret007/StoryBoard main after PR #19
(`packages/shared/src/catalog-import.ts`) and rupret007/rad-dad-show-night
after #3. Vault #7–#19 already lock the schema-3 published slice,
setlist names, catalog counts, import file vs spine, spine-reject,
Show Night-does-not-expand, never_auto_post, local-JSON-only, and
owner-only official-set writes. StoryBoard #16 rejects
`master_catalog.json` at the catalog import boundary. A rejected
Vault payload also blocks a paired Show Night plan. StoryBoard #19
binds a local official-set dump (`songs[]` + `setSlug`) as
Rad Dad — official set. Guest/parked slugs stay opt-in. Public
suggestion dumps are not the official set. Show Night #3 names
Show Night as the live set surface; Vault is the catalog.

`data/app_api.json` is the StoryBoard import. `master_catalog.json`
is the spine and is rejected as an import. StoryLiner is promo only.
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
# Show Night #1/#2: official set writes stay owner-only. Public
# suggestions cannot mutate that set. This feed is not a writer.
SHOW_NIGHT_OFFICIAL_SET_IS_OWNER_ONLY = True
SHOW_NIGHT_OFFICIAL_SET_WRITE = "POST /api/show"
SHOW_NIGHT_OFFICIAL_SET_OWNER_ERROR = "Owner access required."
SHOW_NIGHT_PUBLIC_SUGGESTIONS_CANNOT_MUTATE_SET = True
SHOW_NIGHT_PUBLIC_SUGGESTION_WRITE = "/api/suggestions"
SHOW_NIGHT_ONE_PUBLIC_SUGGESTION_WRITER = True
VAULT_FEED_IS_NOT_A_SHOW_NIGHT_WRITER = True
SHOW_CONTROL_IS_OWNER_ONLY = True
# StoryBoard #19: live GET /api/show dump binds rad-dad only.
# Guest/parked slugs stay opt-in — not a fourth live band.
# Public suggestion dumps are not the official set.
SHOW_NIGHT_BINDS_OFFICIAL_SET_DUMP = True
SHOW_NIGHT_OFFICIAL_SET_DUMP_IS_LOCAL = True
SHOW_NIGHT_OFFICIAL_SET_SLUG = "rad-dad"
SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME = "Rad Dad — official set"
SHOW_NIGHT_GUEST_SETS_STAY_OPT_IN = True
SHOW_NIGHT_GUEST_SET_TITLES = {
    "jeff-story-friends": "Jeff Story & Friends",
    "stalemate": "Stalemate",
}
SHOW_NIGHT_OFFICIAL_SET_IMPORT_ERROR = (
    "Show Night official set is a local show.json or official-set dump; "
    "public suggestions are not the official set."
)
SHOW_NIGHT_FEED_IMPORT_ERROR = (
    "Show Night import requires a local show.json or official-set dump, "
    "not a remote URL or suggestion board."
)
# Show Night #3 surface roles. Vault stays the catalog.
SHOW_NIGHT_ROLE = "live_set_surface"
VAULT_ROLE = "catalog"
RADDAD_SITE_ROLE = "public_site"
# Field names only — not a catalog dump. A public suggestion that
# carries any of these is an official-set mutation attempt.
OFFICIAL_SET_MUTATION_KEYS = (
    "setSlug",
    "set_slug",
    "showSlug",
    "show_slug",
    "showId",
    "show_id",
    "songs",
    "position",
    "order",
    "songKey",
    "song_key",
    "tuning",
    "transition",
    "durationSeconds",
    "duration_seconds",
    "performanceNote",
    "performance_note",
    "rehearsalNotes",
    "rehearsal_notes",
    "youtubeUrl",
    "youtube_url",
    "youtubeVideoId",
    "youtube_video_id",
    "chordsUrl",
    "chords_url",
    "lyricsUrl",
    "lyrics_url",
    "updatedBy",
    "updated_by",
)
VAULT_IMPORT_FILE = "data/app_api.json"
MASTER_CATALOG_IS_NOT_THE_IMPORT = True
MASTER_CATALOG_IS_REJECTED = True
VAULT_SPINE_IMPORT_ERROR = (
    "master_catalog.json is the Vault spine, not the StoryBoard import feed; "
    "export data/app_api.json."
)
VAULT_FEED_IMPORT_ERROR = (
    "Vault import requires the data/app_api.json StoryBoard feed."
)
SPINE_SONG_KEYS = (
    "song_id",
    "canonical_title",
    "artist_project",
    "classification",
)
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


def _is_record(value) -> bool:
    return isinstance(value, dict)


def _song_looks_like_spine(song) -> bool:
    """Match StoryBoard vaultPayloadLooksLikeSpine() song keys after #16."""
    return _is_record(song) and any(key in song for key in SPINE_SONG_KEYS)


def vault_payload_looks_like_spine(payload) -> bool:
    """Match StoryBoard vaultPayloadLooksLikeSpine() after #16.

    A spine payload is rejected. Do not plan songs from it.
    """
    if isinstance(payload, list):
        return any(_song_looks_like_spine(song) for song in payload)
    if not _is_record(payload):
        return False
    if "version" in payload and "schema_version" not in payload:
        return True
    songs = payload.get("songs")
    if not isinstance(songs, list):
        return False
    return any(_song_looks_like_spine(song) for song in songs)


def _looks_like_app_api_feed(payload) -> bool:
    """Enough of StoryBoard vaultAppApiSchema to tell feed from reject."""
    if not _is_record(payload):
        return False
    songs = payload.get("songs")
    if not isinstance(songs, list):
        return False
    for song in songs:
        if not _is_record(song):
            return False
        if not str(song.get("id") or "").strip():
            return False
        if not str(song.get("title") or "").strip():
            return False
    return True


def vault_payload_validation_error(payload):
    """Match StoryBoard vaultPayloadValidationError() after #16."""
    if vault_payload_looks_like_spine(payload):
        return VAULT_SPINE_IMPORT_ERROR
    if not _looks_like_app_api_feed(payload):
        return VAULT_FEED_IMPORT_ERROR
    return None


def spine_default_plan_ids(_catalog_songs: list[dict]) -> list[str]:
    """StoryBoard #16 rejects the spine. No songs are planned."""
    return []


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


def public_suggestion_has_official_set_mutation(payload) -> bool:
    """Match Show Night publicSuggestionHasOfficialSetMutationAttempt().

    Field names only. A public suggestion that carries official-set
    keys is a mutation attempt and must be refused.
    """
    if not isinstance(payload, dict):
        return False
    return any(key in payload for key in OFFICIAL_SET_MUTATION_KEYS)


def official_set_write_allowed(method, route, *, owner: bool) -> bool:
    """Show Night official-set writes stay on owner-only POST /api/show."""
    if str(method or "").upper() != "POST":
        return False
    if str(route or "").strip() != "/api/show":
        return False
    return bool(owner)


def public_suggestion_writer_is_canonical(route) -> bool:
    """Show Night #2 keeps one public suggestion writer."""
    return str(route or "").strip() == SHOW_NIGHT_PUBLIC_SUGGESTION_WRITE


def official_set_song_title(song):
    """Match StoryBoard officialSetSongTitle() after #19."""
    if not _is_record(song):
        return None
    return as_text(song.get("title")) or as_text(song.get("song"))


def official_set_slug(song):
    """Match StoryBoard officialSetSlug() after #19."""
    if not _is_record(song):
        return None
    return as_text(song.get("setSlug"))


def looks_like_official_set_song(song) -> bool:
    return bool(official_set_song_title(song) and official_set_slug(song))


def show_night_payload_looks_like_official_set_dump(payload) -> bool:
    """Match StoryBoard showNightPayloadLooksLikeOfficialSetDump() after #19.

    Live official set is local songs[] + setSlug, not radDadSet.
    """
    if not _is_record(payload) or isinstance(payload.get("radDadSet"), list):
        return False
    songs = payload.get("songs")
    if not isinstance(songs, list):
        return False
    if any(looks_like_official_set_song(song) for song in songs):
        return True
    return len(songs) == 0 and (
        _is_record(payload.get("show")) or isinstance(payload.get("sets"), list)
    )


def looks_like_suggestion_entry(value) -> bool:
    """Match StoryBoard looksLikeSuggestionEntry() after #19."""
    if not _is_record(value):
        return False
    if official_set_slug(value) or as_text(value.get("song")):
        return False
    return bool(
        as_text(value.get("title"))
        and (
            as_text(value.get("artist"))
            or as_text(value.get("submitter"))
            or as_text(value.get("notes"))
        )
    )


def show_night_payload_looks_like_suggestion(payload) -> bool:
    """Match StoryBoard showNightPayloadLooksLikeSuggestion() after #19.

    Public suggestion-board / Google Form rows are not the official set.
    """
    if isinstance(payload, list):
        return any(looks_like_suggestion_entry(item) for item in payload)
    if not _is_record(payload):
        return False
    if show_night_payload_looks_like_official_set_dump(payload) or isinstance(
        payload.get("radDadSet"), list
    ):
        return False
    if isinstance(payload.get("suggestions"), list) or isinstance(
        payload.get("entries"), list
    ):
        return True
    if (
        as_text(payload.get("formAction"))
        or as_text(payload.get("googleForm"))
        or "entry.200" in payload
    ):
        return True
    return looks_like_suggestion_entry(payload)


def _looks_like_legacy_show_json(payload) -> bool:
    """Old radDadSet show.json still works after StoryBoard #19."""
    if not _is_record(payload):
        return False
    rad_dad_set = payload.get("radDadSet")
    if not isinstance(rad_dad_set, list):
        return False
    for row in rad_dad_set:
        if not _is_record(row):
            return False
        if not as_text(row.get("song")):
            return False
    return True


def show_night_catalog_payload_error(payload):
    """Match StoryBoard showNightCatalogPayloadError() after #19."""
    if show_night_payload_looks_like_suggestion(payload):
        return SHOW_NIGHT_OFFICIAL_SET_IMPORT_ERROR
    if vault_payload_looks_like_spine(payload):
        return VAULT_SPINE_IMPORT_ERROR
    if show_night_payload_looks_like_official_set_dump(payload):
        return None
    if _looks_like_legacy_show_json(payload):
        return None
    return SHOW_NIGHT_FEED_IMPORT_ERROR


def official_set_position(value) -> int:
    """Match StoryBoard officialSetPosition() after #19."""
    if not _is_record(value):
        return 2**53 - 1
    position = value.get("position")
    if isinstance(position, int) and not isinstance(position, bool):
        return position
    if isinstance(position, float) and position == position and position.is_integer():
        return int(position)
    number = value.get("number")
    if isinstance(number, int) and not isinstance(number, bool):
        return number
    if isinstance(number, float) and number == number and number.is_integer():
        return int(number)
    return 2**53 - 1


def show_night_row_from_unknown(song):
    """Match StoryBoard showNightRowFromUnknown() after #19."""
    title = official_set_song_title(song)
    if not title:
        return None
    row = {"song": title}
    if _is_record(song):
        cue = as_text(song.get("performanceNote")) or as_text(song.get("cue"))
        if cue:
            row["cue"] = cue
        if song.get("transition") is True:
            row["transition"] = True
        if song.get("special") is True:
            row["special"] = True
        if isinstance(song.get("isOriginal"), bool):
            row["isOriginal"] = song.get("isOriginal")
    return row


def read_show_night_running_order(payload):
    """Match StoryBoard readShowNightRunningOrder() after #19.

    Official slug is rad-dad. Other slugs stay guest/parked.
    """
    payload_error = show_night_catalog_payload_error(payload)
    if payload_error:
        return {"ok": False, "message": payload_error}
    if show_night_payload_looks_like_official_set_dump(payload) and _is_record(
        payload
    ):
        songs = list(payload.get("songs") or [])
        songs.sort(key=official_set_position)
        official = [
            row
            for row in (
                show_night_row_from_unknown(song)
                for song in songs
                if official_set_slug(song) == SHOW_NIGHT_OFFICIAL_SET_SLUG
            )
            if row is not None
        ]
        guests_by_slug: dict[str, list] = {}
        for song in songs:
            set_slug = official_set_slug(song)
            if not set_slug or set_slug == SHOW_NIGHT_OFFICIAL_SET_SLUG:
                continue
            row = show_night_row_from_unknown(song)
            if not row:
                continue
            guests_by_slug.setdefault(set_slug, []).append(row)
        set_titles: dict[str, str] = {}
        if isinstance(payload.get("sets"), list):
            for item in payload.get("sets") or []:
                if not _is_record(item):
                    continue
                slug_value = as_text(item.get("slug"))
                title = as_text(item.get("title"))
                if slug_value and title:
                    set_titles[slug_value] = title
        guests = [
            {
                "name": set_titles.get(slug, SHOW_NIGHT_GUEST_SET_TITLES.get(slug, slug)),
                "songs": guest_songs,
            }
            for slug, guest_songs in guests_by_slug.items()
        ]
        return {
            "ok": True,
            "order": {
                "official": official,
                "guests": guests,
            },
        }
    official = []
    for row in payload.get("radDadSet") or []:
        mapped = show_night_row_from_unknown(row)
        if mapped:
            official.append(mapped)
    guests = []
    for guest in payload.get("guestSets") or []:
        if not _is_record(guest):
            continue
        name = as_text(guest.get("name"))
        if not name:
            continue
        guest_songs = []
        for row in guest.get("songs") or []:
            mapped = show_night_row_from_unknown(row)
            if mapped:
                guest_songs.append(mapped)
        guests.append({"name": name, "songs": guest_songs})
    return {
        "ok": True,
        "order": {
            "official": official,
            "guests": guests,
        },
    }


def bind_official_set_dump(
    payload,
    planned_titles=None,
    skip_by_title=None,
    *,
    include_guest_sets: bool = False,
) -> dict:
    """StoryBoard #19 official-set dump bind.

    Show Night-only dumps plan official titles. When a Vault plan is
    present, only planned titles bind. Guest/parked slugs stay opt-in.
    Suggestion dumps do not plan an official set. Fixture titles only.
    """
    running = read_show_night_running_order(payload)
    if not running.get("ok"):
        return {
            "ok": False,
            "error": running.get("message"),
            "official_name": None,
            "official_titles": [],
            "guests": [],
            "skipped": [],
        }
    order = running["order"]
    skip = skip_by_title or {}
    official_titles: list[str] = []
    skipped: list[dict] = []
    vault_present = planned_titles is not None
    for row in order["official"]:
        title = clean_title(row.get("song") or "")
        if not title:
            continue
        if vault_present:
            action, detail = show_night_bind_title(title, planned_titles, skip)
            if action == "bind":
                official_titles.append(title)
            else:
                skipped.append(
                    {"title": title, "reason": detail, "source": "show_night"}
                )
        else:
            official_titles.append(title)
    guests = []
    for guest in order["guests"]:
        name = guest.get("name")
        if not include_guest_sets:
            skipped.append({"title": name, "reason": "guest_set_skipped"})
            continue
        guests.append(guest)
    return {
        "ok": True,
        "error": None,
        "official_name": SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME,
        "official_titles": official_titles,
        "guests": guests,
        "skipped": skipped,
    }


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
        "inspected": (
            "2026-08-27 after StoryBoard #19 "
            "(StoryBoard #12 local JSON; StoryBoard #16 spine rejected; "
            "Show Night #1/#2 official set owner-only; "
            "official-set dump binds Rad Dad — official set; "
            "Show Night #3 live set surface)"
        ),
        "policy_version": CATALOG_IMPORT_POLICY_VERSION,
        "import_from": "songs",
        "import_file": VAULT_IMPORT_FILE,
        "master_catalog_is_not_the_import": MASTER_CATALOG_IS_NOT_THE_IMPORT,
        "master_catalog_is_rejected": MASTER_CATALOG_IS_REJECTED,
        "vault_spine_import_error": VAULT_SPINE_IMPORT_ERROR,
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
        "show_night_official_set_is_owner_only": (
            SHOW_NIGHT_OFFICIAL_SET_IS_OWNER_ONLY
        ),
        "show_night_official_set_write": SHOW_NIGHT_OFFICIAL_SET_WRITE,
        "show_night_official_set_owner_error": SHOW_NIGHT_OFFICIAL_SET_OWNER_ERROR,
        "show_night_public_suggestions_cannot_mutate_set": (
            SHOW_NIGHT_PUBLIC_SUGGESTIONS_CANNOT_MUTATE_SET
        ),
        "show_night_public_suggestion_write": SHOW_NIGHT_PUBLIC_SUGGESTION_WRITE,
        "show_night_one_public_suggestion_writer": (
            SHOW_NIGHT_ONE_PUBLIC_SUGGESTION_WRITER
        ),
        "vault_feed_is_not_a_show_night_writer": (
            VAULT_FEED_IS_NOT_A_SHOW_NIGHT_WRITER
        ),
        "show_control_is_owner_only": SHOW_CONTROL_IS_OWNER_ONLY,
        "show_night_binds_official_set_dump": SHOW_NIGHT_BINDS_OFFICIAL_SET_DUMP,
        "show_night_official_set_dump_is_local": (
            SHOW_NIGHT_OFFICIAL_SET_DUMP_IS_LOCAL
        ),
        "show_night_official_set_slug": SHOW_NIGHT_OFFICIAL_SET_SLUG,
        "show_night_official_set_setlist_name": (
            SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME
        ),
        "show_night_guest_sets_stay_opt_in": SHOW_NIGHT_GUEST_SETS_STAY_OPT_IN,
        "show_night_official_set_import_error": (
            SHOW_NIGHT_OFFICIAL_SET_IMPORT_ERROR
        ),
        "show_night_role": SHOW_NIGHT_ROLE,
        "vault_role": VAULT_ROLE,
        "raddad_site_role": RADDAD_SITE_ROLE,
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
            "spine and is rejected as an import. StoryBoard #16 fails closed "
            "on that spine. StoryBoard #12 accepts this file only as local "
            "JSON (Band operations → Music & setlists). Remote catalog URLs "
            "are rejected. This private catalog is not a public fetch. "
            "Published setlist_ready_default_import is the default plan "
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
            "excluded rows or fill an empty published slice. A rejected Vault "
            "payload also blocks a paired Show Night plan. Show Night official "
            "set writes stay owner-only (POST /api/show). Public suggestions "
            "cannot mutate that set. This feed is not a public Show Night "
            "writer. StoryBoard #19 binds a local official-set dump "
            "(songs[] + setSlug) as 'Rad Dad — official set'. Guest/parked "
            "slugs stay opt-in — not a fourth live band. Public suggestion "
            "dumps are not the official set. Show Night is the live set "
            "surface; Vault is the catalog. Nothing auto-posts. "
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
            "master_catalog_is_rejected": True,
            "band_operations_import": BAND_OPERATIONS_IMPORT,
            "never_auto_post": True,
            "show_night_does_not_expand_vault": True,
            "show_night_official_set_is_owner_only": True,
            "show_night_public_suggestions_cannot_mutate_set": True,
            "vault_feed_is_not_a_show_night_writer": True,
            "show_night_official_set_write": SHOW_NIGHT_OFFICIAL_SET_WRITE,
            "show_night_public_suggestion_write": SHOW_NIGHT_PUBLIC_SUGGESTION_WRITE,
            "show_night_binds_official_set_dump": True,
            "show_night_official_set_dump_is_local": True,
            "show_night_guest_sets_stay_opt_in": True,
            "show_night_official_set_setlist_name": (
                SHOW_NIGHT_OFFICIAL_SET_SETLIST_NAME
            ),
            "show_night_role": SHOW_NIGHT_ROLE,
            "jeff_owns_catalog_calls": True,
        },
    }
