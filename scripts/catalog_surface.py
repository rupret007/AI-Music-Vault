"""First useful catalog surface — reuse data/app_api.json.

Vault is the catalog brain. StoryBoard consumes the existing export.
Show Night owns official sets. Catalog rows are not the live set.
Do not invent songs, lyrics dumps, or a second catalog.
"""
from __future__ import annotations

import re

SCOPE_SURFACE_LABELS = {
    "default_live": "Vault default-live — catalog, not official set",
    "parked_catalog": "Parked catalog — not a live band",
    "not_live_band": "Not a live band",
    "not_setlist_ready": "Not setlist-ready",
    "cover_not_active": "Cover — not active",
    "travis_books": "Travis books",
}

SURFACE_SUBTITLE = (
    "Catalog brain · StoryBoard consumes data/app_api.json · "
    "Show Night owns official sets · catalog rows are not the live set"
)

ON_DECK_NOTE = "catalog, not the official set"

MEMO_SEARCH_MIN_CHARS = 15
MEMO_SEARCH_MAX_CHARS = 1500

PLAYED_BADGE_PREFIX = "played"
SURFACE_STAGE_REPLACEMENT = "catalog play history — not the official set"

# Longer phrases first so "in the current live set" wins over "in the live set".
STAGE_LIVE_SET_CLAIMS = (
    "in the current live set",
    "in current live set",
    "in the live set",
)

OFFICIAL_SET_SURFACE_CLAIMS = STAGE_LIVE_SET_CLAIMS + (
    "catalog rows are the official set",
    "catalog rows are the live set",
    "default-live is the official set",
    "vault default-live is the official set",
)


def collapse_transcript_text(text) -> str:
    """Trim runaway repeated ASR words without treating a short result as searchable."""
    words = str(text or "").split()
    out: list[str] = []
    for word in words:
        if (
            len(out) >= 2
            and out[-1].lower() == word.lower()
            and out[-2].lower() == word.lower()
        ):
            continue
        out.append(word)
    return " ".join(out)


def build_memo_search_index(transcripts, matches_by_song) -> tuple[list[dict], dict[str, int]]:
    """Return the compact search index and distinct source/searchable counts.

    A transcript can be transcribed and matched while still being too short to
    provide a useful search snippet. Keep that row in the source totals without
    pretending it is present in the browser search index.
    """
    uid_to_song: dict[str, str] = {}
    if isinstance(matches_by_song, dict):
        for song_id, uids in matches_by_song.items():
            for uid in uids or []:
                uid_to_song[str(uid)] = str(song_id)

    prepared: list[dict] = []
    total_matched = 0
    searchable_matched = 0
    for source in transcripts or []:
        row = dict(source)
        uid = str(row.get("uid") or "")
        if uid in uid_to_song:
            row["song_id"] = uid_to_song[uid]
        song_id = str(row.get("song_id") or "")
        if song_id:
            total_matched += 1

        text = collapse_transcript_text(row.get("text"))[:MEMO_SEARCH_MAX_CHARS]
        if len(text) < MEMO_SEARCH_MIN_CHARS:
            continue
        if song_id:
            searchable_matched += 1
        prepared.append(
            {
                "f": row.get("file") or "",
                "n": row.get("title") or "(untitled)",
                "d": row.get("date") or "",
                "u": row.get("dur") or 0,
                "s": song_id,
                "x": text,
            }
        )

    return prepared, {
        "transcribed": len(transcripts or []),
        "matched": total_matched,
        "searchable": len(prepared),
        "searchable_matched": searchable_matched,
    }


def feed_scope_by_id(app_api) -> dict[str, str]:
    """Map export song id → import_scope. Missing feed stays empty."""
    out: dict[str, str] = {}
    if not isinstance(app_api, dict):
        return out
    for song in app_api.get("songs") or []:
        if not isinstance(song, dict):
            continue
        sid = str(song.get("id") or song.get("vault_id") or "").strip()
        scope = str(song.get("import_scope") or "").strip()
        if sid:
            out[sid] = scope
    return out


def scope_surface_label(scope: str) -> str:
    key = str(scope or "").strip()
    return SCOPE_SURFACE_LABELS.get(key, key)


def overlay_feed_scopes(rows: list[dict], app_api) -> list[dict]:
    """Stamp StoryBoard import_scope from the existing export onto surface rows."""
    scopes = feed_scope_by_id(app_api)
    for row in rows:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("id") or "").strip()
        scope = scopes.get(sid, "")
        row["scope"] = scope
        row["scope_label"] = scope_surface_label(scope)
    return rows


def played_badge_label(live_latest) -> str:
    """Catalog play history — not the official live set."""
    stamp = str(live_latest or "").strip()
    if not stamp:
        return ""
    return f"{PLAYED_BADGE_PREFIX} {stamp}"


def catalog_workspace_uses_vault_framing(status: dict) -> bool:
    """StoryBoard #20: Vault songs + official-set setlist stay Vault-framed."""
    if not isinstance(status, dict):
        return False
    source = status.get("source")
    if source in ("none", "vault"):
        return True
    return (
        int(status.get("vaultSongCount") or 0) > 0
        and int(status.get("showNightSongCount") or 0) == 0
        and int(status.get("demoSongCount") or 0) == 0
        and int(status.get("manualSongCount") or 0) == 0
    )


def surface_row_claims_official_set(row) -> bool:
    """A Vault catalog row must not wear the official-set name."""
    if not isinstance(row, dict):
        return False
    label = str(row.get("scope_label") or row.get("label") or "").lower()
    if "not official set" in label or "not the official set" in label:
        return False
    return "official set" in label


def catalog_surface_claims_official_set(text: str) -> bool:
    """First useful surface must not call catalog rows the live / official set."""
    body = (text or "").lower()
    return any(claim in body for claim in OFFICIAL_SET_SURFACE_CLAIMS)


def surface_stage_label(stage) -> str:
    """Display catalog stage without reprinting a live-set claim.

    Spine notes may still say 'IN CURRENT LIVE SET' for play-history
    rows. Do not rewrite the spine. The first useful surface sanitizes.
    """
    text = "" if stage is None else str(stage)
    while True:
        lowered = text.lower()
        hit = None
        for claim in STAGE_LIVE_SET_CLAIMS:
            idx = lowered.find(claim)
            if idx >= 0:
                hit = (idx, len(claim))
                break
        if hit is None:
            return text
        idx, n = hit
        text = text[:idx] + SURFACE_STAGE_REPLACEMENT + text[idx + n :]


def catalog_surface_admits_not_official_set(text: str) -> bool:
    """Dashboard / surface copy must reuse the export and refuse the live-set claim."""
    body = (text or "").lower()
    has_not = (
        "catalog rows are not the official set" in body
        or "catalog rows are not the live set" in body
    )
    return has_not and "app_api.json" in body and "show night" in body


OWNER_AUDIO_OPEN_MARKERS = (
    "<audio",
    "file://",
    "onclick=",
)

OWNER_AUDIO_HREF_RE = re.compile(
    r"""href\s*=\s*['"]([^'"]+)['"]""",
    re.IGNORECASE,
)

OWNER_AUDIO_HREF_SUFFIXES = (
    ".wav",
    ".aiff",
    ".aif",
    ".logicx",
    ".m4a",
    ".mp3",
    ".flac",
    ".band",
)

VAULT_HASH_KINDS = ("memos", "song")


def memo_evidence_by_song(index_rows) -> dict[str, dict]:
    """Searchable matched-memo evidence already in the dashboard index.

    Counts and dates come from existing searchable rows only. Short matched
    transcripts stay out, same as the browser index. This does not invent
    unmatched memos, keys, or WAV paths.
    """
    out: dict[str, dict] = {}
    for row in index_rows or []:
        if not isinstance(row, dict):
            continue
        song_id = str(row.get("s") or row.get("song_id") or "").strip()
        if not song_id:
            continue
        ev = out.setdefault(song_id, {"n": 0, "first": "", "last": ""})
        ev["n"] += 1
        date = str(row.get("d") or row.get("date") or "").strip()
        if not date:
            continue
        if not ev["first"] or date < ev["first"]:
            ev["first"] = date
        if not ev["last"] or date > ev["last"]:
            ev["last"] = date
    return out


def sort_memo_evidence_rows(rows) -> list[dict]:
    """Newest searchable memo first so Jeff can act on the latest take."""
    dated: list[dict] = []
    empty: list[dict] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("d") or "").strip():
            dated.append(row)
        else:
            empty.append(row)
    dated.sort(
        key=lambda row: (str(row.get("d") or ""), str(row.get("f") or "")),
        reverse=True,
    )
    empty.sort(key=lambda row: str(row.get("f") or ""), reverse=True)
    return dated + empty


def parse_vault_hash(raw, names) -> dict | None:
    """Allow only known catalog ids on the local #memos= / #song= hash."""
    text = str(raw or "").lstrip("#")
    if "=" not in text:
        return None
    kind, song_id = text.split("=", 1)
    if kind not in VAULT_HASH_KINDS:
        return None
    if not isinstance(names, dict) or song_id not in names:
        return None
    return {"kind": kind, "id": song_id}


def dashboard_markup_chrome(html: str) -> str:
    """Drop embedded DATA/TX payloads so transcript text cannot trip markup checks."""
    body = html or ""
    body = re.sub(r"const DATA = .*?;\n", "const DATA = [];\n", body, count=1)
    body = re.sub(r"const TX = .*?;\n", "const TX = [];\n", body, count=1)
    return body


def dashboard_opens_owner_audio(html: str) -> bool:
    """Local index must not open Logic keys, WAVs, or audio."""
    chrome = dashboard_markup_chrome(html)
    lowered = chrome.lower()
    if any(marker in lowered for marker in OWNER_AUDIO_OPEN_MARKERS):
        return True
    for match in OWNER_AUDIO_HREF_RE.finditer(chrome):
        href = match.group(1).strip().lower()
        if href.startswith("file:"):
            return True
        path = href.split("?", 1)[0].split("#", 1)[0]
        if any(path.endswith(ext) for ext in OWNER_AUDIO_HREF_SUFFIXES):
            return True
    return False
