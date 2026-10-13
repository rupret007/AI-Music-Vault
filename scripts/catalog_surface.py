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
UNSAFE_MEMO_INTAKE_SUFFIXES = (
    ".wav",
    ".aiff",
    ".aif",
    ".logicx",
    ".mid",
    ".midi",
)

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


def sanitize_intake_name(value) -> str:
    """Keep only a copy-safe memo intake basename (no directories/URI parts)."""
    name = str(value or "").strip()
    if not name:
        return ""
    normalized = (
        name.replace("\\", "/").split("?", 1)[0].split("#", 1)[0]
    )
    if normalized.lower().startswith("file://"):
        normalized = normalized[7:]
    basename = normalized.rsplit("/", 1)[-1].strip()
    if basename in {"", ".", ".."}:
        return ""
    collapsed = re.sub(r"\s{2,}", " ", basename)
    lowered = collapsed.lower()
    if lowered in {"(unknown intake)", "unknown intake"}:
        return ""
    if lowered.endswith(UNSAFE_MEMO_INTAKE_SUFFIXES):
        return ""
    return collapsed


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
                "f": sanitize_intake_name(row.get("file")),
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


def duplicate_memo_uids(vm_matches) -> list[str]:
    """Memo UIDs listed more than once in vm_matches (same song or across songs)."""
    counts: dict[str, int] = {}
    if not isinstance(vm_matches, dict):
        return []
    for uids in vm_matches.values():
        if not isinstance(uids, list):
            continue
        for uid in uids:
            key = str(uid or "").strip()
            if not key:
                continue
            counts[key] = counts.get(key, 0) + 1
    return sorted(uid for uid, n in counts.items() if n > 1)


def duplicate_memo_files(index_rows) -> list[str]:
    """Search-index filenames that appear more than once."""
    counts: dict[str, int] = {}
    for row in index_rows or []:
        if not isinstance(row, dict):
            continue
        name = str(row.get("f") or row.get("file") or "").strip().lower()
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    return sorted(name for name, n in counts.items() if n > 1)


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


RECOVERED_STAGE_MARK = "recovered"


def catalog_cover_count(catalog) -> int:
    """Cover-book size from the spine covers table, not a hardcoded 93."""
    if not isinstance(catalog, dict):
        return 0
    covers = catalog.get("covers")
    if isinstance(covers, list):
        return len(covers)
    ref = catalog.get("covers_reference")
    try:
        return int(ref)
    except (TypeError, ValueError):
        return 0


def catalog_recovered_count(catalog) -> int:
    """Songs recovered from memos, from existing catalog text, not a hardcoded 9.

    Stage usually carries 'recovered'. JS-0131 is the exception: its stage was
    rewritten to the Oct 2025 writing receipt, so lyric_status still names the
    memo recovery. Do not count later lyric reconstruction of already-known
    songs (Blue Skies Fade, It's Alright).
    """
    if not isinstance(catalog, dict):
        return 0
    n = 0
    for song in catalog.get("songs") or []:
        if not isinstance(song, dict):
            continue
        stage = str(song.get("stage") or "").lower()
        lyric = str(song.get("lyric_status") or "").lower()
        if RECOVERED_STAGE_MARK in stage or "recovered from memo" in lyric:
            n += 1
    return n


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
    ".mid",
    ".midi",
    ".m4a",
    ".mp3",
    ".flac",
    ".band",
)

VAULT_HASH_KINDS = ("memos", "song", "work")
WORK_HASH_KINDS = (
    "write",
    "produce",
    "listen",
    "rest",
    "inventory",
    "decide",
)


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
    """Allow known catalog ids on #memos= / #song=, or a work-kind on #work=."""
    text = str(raw or "").lstrip("#")
    if "=" not in text:
        return None
    kind, value = text.split("=", 1)
    if kind == "work":
        if value in WORK_HASH_KINDS:
            return {"kind": kind, "id": value}
        return None
    if kind not in ("memos", "song"):
        return None
    if not isinstance(names, dict) or value not in names:
        return None
    return {"kind": kind, "id": value}


def latest_memo_for_song(song_id, index_rows) -> dict | None:
    """Newest searchable memo for a catalog id — sit-down listen/write target."""
    sid = str(song_id or "").strip()
    if not sid:
        return None
    hits = [
        row
        for row in (index_rows or [])
        if isinstance(row, dict) and str(row.get("s") or row.get("song_id") or "").strip() == sid
    ]
    if not hits:
        return None
    return sort_memo_evidence_rows(hits)[0]


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


SONG_WORK_KINDS = (
    "write",
    "produce",
    "listen",
    "rest",
    "inventory",
    "decide",
    "unknown",
)

# Already-visible catalog next_action text. First match wins. Do not invent
# energy levels or a second score.
_WRITE_MARKS = (
    "chorus lines",
    "transcribe",
    "read lyric",
    "locate/transcribe",
    "hum 30",
    "has lyric",
    "lyric rethink",
    "confirm the 2",
    "catch the real chorus",
)
_PRODUCE_MARKS = (
    "overdub",
    "bounce mix",
    "track background",
    "record lead guitar",
    "record bridge",
    "add rhythm guitar",
    "full-band arrangement",
    "arrangement built",
)
_OWNER_AUDIO_IN_TEXT_RE = re.compile(
    r"\([^()]{0,200}\.(?:wav|aiff|aif|logicx|mid|midi|m4a|mp3|flac|band)\)|"
    r"\b[\w./' -]+\.(?:wav|aiff|aif|logicx|mid|midi|m4a|mp3|flac|band)\b|"
    r"file://\S+",
    re.IGNORECASE,
)
# Home-address fragments already present in a few gem next_actions.
# Copy must not put them on the clipboard. Do not match song titles like
# "Candi Lane".
_PRIVATE_STREET_RE = re.compile(
    r"\b(?:Maxwell Dr|Crescent Dr|Eagle Mountain Dr)\b[^,.;]*",
    re.IGNORECASE,
)
_PRIVATE_STREET_NAMES = (
    "maxwell dr",
    "crescent dr",
    "eagle mountain dr",
)

# TX stays locked unless transcripts change. DATA may change when the
# private surface projects already-on-spine aliases, a sanitized
# Logic-ready cluster id, or the per-song Logic-native asset tag list
# (Logic Pro project / WAV/AIFF / Stems / Recorded take / Key on file —
# words only, never a filename or path). Do not invent keys or paths.
EMBEDDED_DATA_SHA256 = (
    "995da4a223b6ffec8ff4cdb231f8baa8aab313be5c25a977ea6b6d93a63355c8"
)
EMBEDDED_TX_SHA256 = (
    "4d809dc53540f8c5acfe63ffcee94844634405c2a0583b2accddc9178807b467"
)

# Same clusters as the 2026-08-28 song-analysis walk. Productized as a
# readout of existing spine + version-chain evidence — not a new score.
LOGIC_READY_CLUSTERS = (
    "closest_logic_dropin",
    "logic_project_plus_key",
    "logic_project_no_key",
    "audio_plus_key_no_logic",
    "audio_only",
    "key_only",
    "empty_logic_ready",
)
LOGIC_READY_LABELS = {
    "closest_logic_dropin": "Closest Logic Pro drop-in",
    "logic_project_plus_key": "Logic Pro project + key",
    "logic_project_no_key": "Logic Pro project · missing key",
    "audio_plus_key_no_logic": "Keyed audio · no Logic Pro project",
    "audio_only": "Audio named · missing key",
    "key_only": "Key only · no Logic Pro project",
    "empty_logic_ready": "Empty Logic-ready",
}
LOGIC_READY_PILLS = {
    "closest_logic_dropin": "Logic Pro drop-in",
    "logic_project_plus_key": "Logic Pro + key",
    "logic_project_no_key": "Logic Pro · no key",
    "audio_plus_key_no_logic": "Keyed audio",
    "audio_only": "Audio · no key",
    "key_only": "Key only",
    "empty_logic_ready": "Empty Logic-ready",
}
# Wording stays fail-closed-safe: never a literal ".logicx"/".wav" extension
# (that trips work_card_leaks_private_locators on purpose) and never a
# specific format claim (WAV vs AIFF vs stems vs a version-chain take) for
# clusters where the underlying evidence can be any of those — the per-song
# song_logic_ready_evidence_tags() readout carries that specific, real detail.
# Canned next steps name owner-only Mac work. They never claim an export,
# bounce, render, or upload already happened.
LOGIC_READY_NEXT = {
    "closest_logic_dropin": (
        "Open the existing Logic Pro project on your Mac — it already has "
        "audio (WAV/AIFF or stems) and a key. This page does not open audio."
    ),
    "logic_project_plus_key": (
        "Open the existing Logic Pro project on your Mac. "
        "This page does not open audio."
    ),
    "logic_project_no_key": (
        "Fill the missing key on your Mac inside the existing Logic Pro "
        "project. Do not invent one here."
    ),
    "audio_plus_key_no_logic": (
        "Start or locate the Logic Pro project on your Mac using the "
        "existing audio and key. This page does not open audio."
    ),
    "audio_only": (
        "Fill the missing key on your Mac after you hear the existing "
        "audio. Do not invent one here."
    ),
    "key_only": (
        "Start the Logic Pro project on your Mac from the known key. If a "
        "memo melody exists, Basic Pitch can turn it into MIDI for Logic."
    ),
    "empty_logic_ready": (
        "No Logic-ready evidence on the catalog. Recover the key or audio "
        "from Drive or the Mac — do not invent a key. Basic Pitch can turn "
        "a recovered memo melody into MIDI for Logic."
    ),
}
LOGIC_READY_RANK = {
    "closest_logic_dropin": 0,
    "logic_project_plus_key": 1,
    "logic_project_no_key": 2,
    "audio_plus_key_no_logic": 3,
    "audio_only": 4,
    "key_only": 5,
    "empty_logic_ready": 6,
}
_LOGICX_RE = re.compile(r"\.logicx\b", re.IGNORECASE)
_WAV_RE = re.compile(
    r"\.(?:wav|aiff|aif)\b|\bwav\b|\baiff\b|\baif\b",
    re.IGNORECASE,
)
_STEMS_RE = re.compile(r"\bstems\b", re.IGNORECASE)
MEMO_LYRIC_QUERY_MIN = 3
_APOS_RE = re.compile(r"['’`]")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def song_work_kind(next_action) -> str:
    """Classify an existing next_action for write / produce scanning.

    This is a readout of catalog text, not a new score and not a lane change.
    Empty next_action stays unknown. Protected-opus / collaborator blanks
    stay unknown. Do not invent keys or overdubs.
    """
    text = str(next_action or "").strip()
    if not text:
        return "unknown"
    low = text.lower()

    if (
        low.startswith("released")
        or "archive-with-honor" in low
        or "not a development priority" in low
        or "rests unless" in low
    ):
        return "rest"
    if (
        "inventory pass" in low
        or "no dated source" in low
        or "voice memo intake" in low
        or "connector limit" in low
    ):
        return "inventory"
    if any(mark in low for mark in _WRITE_MARKS):
        return "write"
    if any(mark in low for mark in _PRODUCE_MARKS):
        return "produce"
    if (
        low.startswith("listen")
        or "listen:" in low
        or "listen first" in low
        or "listen + verdict" in low
    ):
        return "listen"
    if (
        low.startswith("decide")
        or low.startswith("hold for")
        or "candidate for next-ep" in low
    ):
        return "decide"
    return "unknown"


def flatten_work_field(value) -> str:
    """Turn catalog open_questions lists into one copyable line."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _logic_ready_field_text(row, *keys) -> list[str]:
    parts: list[str] = []
    if not isinstance(row, dict):
        return parts
    for key in keys:
        value = row.get(key)
        if isinstance(value, (list, tuple)):
            parts.extend(str(item) for item in value if str(item).strip())
        elif value:
            parts.append(str(value))
    return parts


def logic_ready_evidence_text(row, chain=None) -> str:
    """Join existing catalog + version-chain titles for Logic-ready readout.

    Uses titles and kinds only. Folder paths and Drive ids stay out.
    Notes that say 'system' or future MIDI horns are not stems or MIDI files.
    """
    parts = _logic_ready_field_text(
        row,
        "sources",
        "src",
        "notes",
        "audio_status",
        "au",
        "best_source_resolved",
        "bs",
        "stage",
        "st",
    )
    if isinstance(chain, dict):
        for item in chain.get("files") or []:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            kind = str(item.get("kind") or "").strip()
            if title:
                parts.append(title)
            if kind:
                parts.append(kind)
    return "\n".join(parts)


def parseable_catalog_key(row) -> str:
    """Existing key field only. Do not invent a key from notes or analysis."""
    if not isinstance(row, dict):
        return ""
    return flatten_work_field(row.get("key"))


def _logic_ready_signals(row, chain=None) -> dict:
    """Raw evidence booleans shared by classification and the asset readout.

    A lone mp3/m4a on sources is not enough — version-chain files, a wav
    word, or real stems are. 'system' is not stems. MIDI horns are not MIDI
    files. Computed once so the cluster and the per-song tag list can never
    disagree on what evidence actually exists.
    """
    if not isinstance(row, dict):
        row = {}
    text = logic_ready_evidence_text(row, chain)
    low = text.lower()
    has_wav = bool(_WAV_RE.search(text))
    has_stems = bool(_STEMS_RE.search(text))
    has_chain = bool(isinstance(chain, dict) and (chain.get("files") or []))
    return {
        "has_key": bool(parseable_catalog_key(row)),
        "has_logicx": bool(_LOGICX_RE.search(text) or "logic-project" in low),
        "has_wav": has_wav,
        "has_stems": has_stems,
        "has_chain": has_chain,
        "has_wav_stems": has_wav or has_stems,
        "has_audio_or_chain": has_wav or has_stems or has_chain,
    }


def song_logic_ready_cluster(row, chain=None) -> str:
    """Classify one row using the 2026-08-28 Logic-ready walk rules.

    This is a readout, not a new score and not a lane change.
    """
    if not isinstance(row, dict):
        return "empty_logic_ready"
    signals = _logic_ready_signals(row, chain)
    has_key = signals["has_key"]
    has_logicx = signals["has_logicx"]
    has_wav_stems = signals["has_wav_stems"]
    has_audio_or_chain = signals["has_audio_or_chain"]
    if has_logicx and has_wav_stems and has_key:
        return "closest_logic_dropin"
    if has_logicx and has_key:
        return "logic_project_plus_key"
    if has_logicx:
        return "logic_project_no_key"
    if has_audio_or_chain and has_key:
        return "audio_plus_key_no_logic"
    if has_audio_or_chain:
        return "audio_only"
    if has_key:
        return "key_only"
    return "empty_logic_ready"


LOGIC_READY_TAG_PROJECT = "Logic Pro project"
LOGIC_READY_TAG_WAV = "WAV/AIFF"
LOGIC_READY_TAG_STEMS = "Stems"
LOGIC_READY_TAG_TAKE = "Recorded take"
LOGIC_READY_TAG_KEY = "Key on file"


def song_logic_ready_evidence_tags(row, chain=None) -> list[str]:
    """Per-song readout of which real Logic-native asset types are on file.

    Literal text evidence only — titles, kinds, and the key field. No
    filenames, no folder paths, no invented formats, no ".logicx"/".wav"
    extensions (that stays fail-closed on purpose). A version-chain audio
    file with no literal wav/aiff/stems word reads as a recorded take, not
    a specific format guess. Tags never mean an export already happened.
    """
    if not isinstance(row, dict):
        return []
    signals = _logic_ready_signals(row, chain)
    tags: list[str] = []
    if signals["has_logicx"]:
        tags.append(LOGIC_READY_TAG_PROJECT)
    if signals["has_wav"]:
        tags.append(LOGIC_READY_TAG_WAV)
    if signals["has_stems"]:
        tags.append(LOGIC_READY_TAG_STEMS)
    if signals["has_chain"] and not signals["has_wav_stems"]:
        tags.append(LOGIC_READY_TAG_TAKE)
    if signals["has_key"]:
        tags.append(LOGIC_READY_TAG_KEY)
    return tags


def song_logic_ready_evidence_label(row, chain=None) -> str:
    """One copy-safe line of Logic-native asset tags, or empty if none."""
    return " · ".join(song_logic_ready_evidence_tags(row, chain))


def song_logic_ready_label(cluster) -> str:
    return LOGIC_READY_LABELS.get(str(cluster or "").strip(), "")


def song_logic_ready_pill(cluster) -> str:
    return LOGIC_READY_PILLS.get(str(cluster or "").strip(), "")


def song_logic_ready_next(cluster) -> str:
    """Owner-only Mac step for a known cluster. Fail closed on locators."""
    text = LOGIC_READY_NEXT.get(str(cluster or "").strip(), "")
    if not text or work_card_leaks_private_locators(text):
        return ""
    return text


def song_logic_ready_rank(cluster) -> int:
    return int(LOGIC_READY_RANK.get(str(cluster or "").strip(), 99))


def logic_ready_maps() -> dict:
    """Browser maps for labels, pills, next steps, and sort rank."""
    return {
        "labels": dict(LOGIC_READY_LABELS),
        "pills": dict(LOGIC_READY_PILLS),
        "next": dict(LOGIC_READY_NEXT),
        "rank": dict(LOGIC_READY_RANK),
    }


def logic_ready_next_leaks_private_locators() -> bool:
    """Fail closed if a canned Logic-ready next step ships a locator."""
    return any(
        work_card_leaks_private_locators(text)
        for text in LOGIC_READY_NEXT.values()
    )


def normalize_search_text(text) -> str:
    """Fold case, apostrophes, and punctuation so Jeff can type the name he remembers."""
    folded = _APOS_RE.sub("", str(text or "").casefold())
    return " ".join(_NON_ALNUM_RE.sub(" ", folded).split())


def song_aliases(row) -> list[str]:
    """Existing alt_titles only. Do not invent names or mint IDs."""
    if not isinstance(row, dict):
        return []
    canonical = str(row.get("canonical_title") or row.get("t") or "").strip()
    raw = row.get("alt_titles")
    if raw is None:
        raw = row.get("aka") or []
    if not isinstance(raw, (list, tuple)):
        return []
    out: list[str] = []
    seen: set[str] = set()
    canon_norm = normalize_search_text(canonical)
    for item in raw:
        name = str(item or "").strip()
        if not name:
            continue
        key = normalize_search_text(name)
        if not key or key in seen:
            continue
        if canon_norm and key == canon_norm:
            continue
        seen.add(key)
        out.append(name)
    return out


def memo_lyric_norm_by_song(index_rows) -> dict[str, str]:
    """Index searchable matched memo *text* only — never titles or filenames."""
    parts: dict[str, list[str]] = {}
    for row in index_rows or []:
        if not isinstance(row, dict):
            continue
        song_id = str(row.get("s") or row.get("song_id") or "").strip()
        text = str(row.get("x") or "")
        if not song_id or not text:
            continue
        parts.setdefault(song_id, []).append(text)
    return {
        song_id: normalize_search_text(" ".join(chunks))
        for song_id, chunks in parts.items()
    }


def _song_search_names(row) -> list[str]:
    names: list[str] = []
    song_id = str(row.get("id") or row.get("song_id") or "").strip()
    title = str(row.get("t") or row.get("canonical_title") or "").strip()
    if song_id:
        names.append(normalize_search_text(song_id))
    if title:
        names.append(normalize_search_text(title))
    for alias in song_aliases(row):
        names.append(normalize_search_text(alias))
    return [name for name in names if name]


def _song_search_field_hay(row) -> str:
    audio = flatten_work_field(row.get("au") or row.get("audio_status"))
    if "—" in audio:
        audio = audio.split("—", 1)[0].strip()
    writers = row.get("wr")
    if writers is None:
        writers = row.get("writers")
    return normalize_search_text(
        " ".join(
            [
                flatten_work_field(row.get("th") or row.get("theme")),
                flatten_work_field(row.get("hk") or row.get("hook")),
                flatten_work_field(row.get("c") or row.get("classification")),
                flatten_work_field(row.get("st") or row.get("stage")),
                flatten_work_field(writers),
                strip_private_locators(
                    flatten_work_field(row.get("nx") or row.get("next_action"))
                ),
                flatten_work_field(row.get("oq") or row.get("open_questions")),
                flatten_work_field(row.get("gate") or row.get("ai_upload_ok")),
                flatten_work_field(row.get("scope_label")),
                flatten_work_field(row.get("ly") or row.get("lyric_status")),
                audio,
                flatten_work_field(row.get("key")),
                song_logic_ready_label(
                    flatten_work_field(row.get("lr"))
                    or song_logic_ready_cluster(row)
                ),
            ]
        )
    )


def song_search_hit(row, term, memo_norm_by_song=None) -> dict:
    """Rank a catalog row for the Songs search box.

    Name / alias / id beat theme and next-action text. A long enough query
    may also hit searchable matched memo lyrics. Memo titles stay out.
    """
    if not isinstance(row, dict):
        return {"hit": False, "rank": 99, "via": ""}
    norm = normalize_search_text(term)
    if not norm:
        return {"hit": True, "rank": 99, "via": ""}
    names = _song_search_names(row)
    query_tokens = [part for part in norm.split() if part]

    def name_tokens(name: str) -> list[str]:
        return [part for part in name.split() if part]

    if any(name == norm for name in names):
        return {"hit": True, "rank": 0, "via": "name"}
    if query_tokens and any(
        name_tokens(name)[: len(query_tokens)] == query_tokens for name in names
    ):
        return {"hit": True, "rank": 0, "via": "name"}
    if any(name.startswith(norm) for name in names):
        return {"hit": True, "rank": 1, "via": "name"}
    if any(norm in name for name in names):
        return {"hit": True, "rank": 2, "via": "name"}
    if norm in _song_search_field_hay(row):
        return {"hit": True, "rank": 3, "via": "field"}
    song_id = str(row.get("id") or row.get("song_id") or "").strip()
    memo_map = memo_norm_by_song if isinstance(memo_norm_by_song, dict) else {}
    memo = memo_map.get(song_id, "")
    if len(norm) >= MEMO_LYRIC_QUERY_MIN and memo and norm in memo:
        return {"hit": True, "rank": 4, "via": "memo"}
    return {"hit": False, "rank": 99, "via": ""}


def strip_private_locators(text) -> str:
    """Drop owner-audio filenames and known street fragments from copy text."""
    cleaned = _OWNER_AUDIO_IN_TEXT_RE.sub("", str(text or ""))
    cleaned = _PRIVATE_STREET_RE.sub("", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.;:])", r"\1", cleaned)
    return cleaned.strip(" -")


def work_card_leaks_private_locators(text) -> bool:
    """Fail closed if a work card still carries Logic/WAV/address locators."""
    low = str(text or "").lower()
    if "file://" in low:
        return True
    if re.search(r"\.(wav|aiff|aif|logicx|mid|midi|m4a|mp3|flac|band)\b", low):
        return True
    return any(name in low for name in _PRIVATE_STREET_NAMES)


INCOMPLETE_NEXT_STEPS = frozenset(
    {
        "open",
        "play",
        "listen",
        "listen to latest",
        "listen: play",
    }
)


def next_step_is_incomplete(text) -> bool:
    """True when sanitizing left only a leftover verb, not a usable action."""
    return str(text or "").lower().rstrip(" .:") in INCOMPLETE_NEXT_STEPS


def safe_song_next_step(row) -> str:
    """Return one copy-safe catalog next step or fail closed.

    Resume, sit-down, memo scope, and Copy next step must share this path.
    An audio filename or owner location must never become clipboard text.
    Empty, non-dict, and leftover-verb rows intentionally produce no action.
    """
    if not isinstance(row, dict):
        return ""
    next_action = flatten_work_field(row.get("nx") or row.get("next_action"))
    cleaned = strip_private_locators(next_action)
    if (
        not cleaned
        or next_step_is_incomplete(cleaned)
        or work_card_leaks_private_locators(cleaned)
    ):
        return ""
    return cleaned


def song_work_card(row, evidence=None) -> str:
    """Copyable write/produce/listen card from already-visible catalog fields.

    Includes title, work kind, next action, hook, theme, open questions,
    lyric/audio status, key, BPM, gate class, and optional searchable-memo
    count/date. Omits sources, best_source, writers, memo titles, and
    intake filenames. Returns empty if the sanitized card still leaks a
    private locator.
    """
    if not isinstance(row, dict):
        return ""
    title = flatten_work_field(row.get("t") or row.get("canonical_title"))
    song_id = flatten_work_field(row.get("id") or row.get("song_id"))
    next_action = flatten_work_field(row.get("nx") or row.get("next_action"))
    kind = song_work_kind(next_action)
    hook = flatten_work_field(row.get("hk") or row.get("hook"))
    theme = flatten_work_field(row.get("th") or row.get("theme"))
    questions = flatten_work_field(row.get("oq") or row.get("open_questions"))
    lyrics = flatten_work_field(row.get("ly") or row.get("lyric_status"))
    audio = flatten_work_field(row.get("au") or row.get("audio_status"))
    if "—" in audio:
        audio = audio.split("—", 1)[0].strip()
    key = flatten_work_field(row.get("key"))
    bpm = flatten_work_field(row.get("bpm"))
    gate = flatten_work_field(row.get("gate") or row.get("ai_upload_ok"))
    if "—" in gate:
        gate = gate.split("—", 1)[0].strip()
    ev = evidence if isinstance(evidence, dict) else row.get("memo_evidence")

    lines = []
    heading = title
    if song_id:
        heading = f"{title} ({song_id})" if title else song_id
    if heading:
        lines.append(heading)
    aliases = song_aliases(row)
    if aliases:
        lines.append("Also known as: " + "; ".join(aliases))
    lines.append(f"Work: {kind}")
    nxt = safe_song_next_step(row)
    if nxt:
        lines.append(f"Next: {nxt}")
    if hook:
        lines.append(f"Hook: {strip_private_locators(hook)}")
    if theme:
        lines.append(f"Theme: {strip_private_locators(theme)}")
    if questions:
        lines.append(f"Open questions: {strip_private_locators(questions)}")
    if lyrics:
        lines.append(f"Lyrics: {strip_private_locators(lyrics)}")
    if audio:
        lines.append(f"Audio: {strip_private_locators(audio)}")
    if key:
        lines.append(f"Key: {key}")
    if bpm:
        lines.append(f"BPM: {bpm}")
    if gate:
        lines.append(f"Gate: {gate}")
    cluster = flatten_work_field(row.get("lr")) or song_logic_ready_cluster(row)
    label = song_logic_ready_label(cluster)
    logic_next = song_logic_ready_next(cluster)
    if label:
        lines.append(f"Logic-ready: {label}")
    if "lrf" in row:
        asset_tags = [str(t) for t in (row.get("lrf") or []) if str(t).strip()]
    else:
        asset_tags = song_logic_ready_evidence_tags(row)
    if asset_tags:
        lines.append(f"Assets on file: {' · '.join(asset_tags)}")
    if logic_next:
        lines.append(f"Logic next: {logic_next}")
    if isinstance(ev, dict):
        try:
            memo_n = int(ev.get("n") or 0)
        except (TypeError, ValueError):
            memo_n = 0
        last = str(ev.get("last") or "").strip()
        if memo_n:
            memo_line = f"Memos: {memo_n} searchable"
            if last:
                memo_line += f" · latest {last}"
            lines.append(memo_line)
    card = "\n".join(line for line in lines if line)
    if work_card_leaks_private_locators(card):
        return ""
    return card


def embedded_dashboard_payloads(html: str) -> dict[str, str]:
    """Return the raw DATA and TX JSON blobs embedded in the dashboard."""
    body = html or ""
    out = {"DATA": "", "TX": ""}
    for name in ("DATA", "TX"):
        match = re.search(rf"const {name} = (.*?);\n", body, flags=re.S)
        if match:
            out[name] = match.group(1)
    return out


OWNER_AUDIO_INDEX_MARKERS = (
    "Latest source (auto-resolved)",
    "<h4>Known assets</h4>",
    "${esc(d.bs)}",
    "${esc(d.nx)}",
)


def dashboard_displays_owner_audio_index(html: str) -> bool:
    """Sit-down chrome must not reprint Logic/WAV/best_source locators."""
    chrome = dashboard_markup_chrome(html)
    if any(marker in chrome for marker in OWNER_AUDIO_INDEX_MARKERS):
        return True
    if "d.src.map" in chrome or "d.src&&d.src" in chrome:
        return True
    return False


def dashboard_exposes_song_work(html: str) -> bool:
    """First useful surface must let Jeff sit down to write/produce/listen."""
    chrome = dashboard_markup_chrome(html)
    return (
        'id="work"' in chrome
        and "Copy work card" in chrome
        and "function songWorkKind(" in chrome
        and "function buildSongWorkCard(" in chrome
        and "data-copy-work" in chrome
        and 'data-open-song="ST-0001"' in chrome
        and 'id="workSession"' in chrome
        and 'id="workStarts"' in chrome
        and 'id="advancedFilters"' in chrome
        and "function openWork(" in chrome
        and "function updateWorkSessionState(" in chrome
        and "function safeWorkNextStep(" in chrome
        and "function copyCurrentWorkNext(" in chrome
        and "function reviewCurrentWorkEvidence(" in chrome
        and "function allowedExactWorkSongId(" in chrome
        and "function copyExactSongNextStep(" in chrome
        and "safeWorkNextStep(d)" in chrome
        and 'id="workSessionNext"' in chrome
        and 'id="copyWorkNext"' in chrome
        and 'id="openWorkEvidence"' in chrome
        and "function latestMemoForSong(" in chrome
        and "data-open-work=" in chrome
        and "Start a work session" in chrome
        and "More filters" in chrome
        and "Sit-down" in chrome
        and "sit-down-actions" in chrome
        and "data-sit-next" in chrome
        and "data-copy-sit-next" in chrome
        and "function updateSitDownCatalogNext(" in chrome
        and "function sessionShowsSongNext(" in chrome
        and "function copySitDownNextStep(" in chrome
    )


SIT_DOWN_INLINE_COPY_MARKERS = (
    "Next: ${esc(nxt)}",
    "Next: <span>${esc(nxt)}</span>",
    "Logic-ready next: ${esc(lrNext)} <button",
    'data-copy-file="${esc(latestIntake.copy)}">Copy intake name</button>`:''}<div class="memo-next">',
    "Catalog next step: see",
)
SIT_DOWN_ACTIONS_ROW = '<div class="sit-down-actions">'
SIT_DOWN_ACTIONS_FLEX = ".sit-down-actions{display:flex"
SIT_DOWN_ACTIONS_PHONE = "@media(max-width:390px){.sit-down-actions{display:flex"
SIT_DOWN_FOOTER_HONESTY = (
    "open in Logic (export honesty: WAVs/AIFF/MIDI preference, no Ableton-first) "
    "— this page does not open audio"
)


def dashboard_sit_down_copy_actions_on_own_row(html: str) -> bool:
    """Sit-down next is song-bound; copy controls sit on their own flex row."""
    chrome = dashboard_markup_chrome(html)
    if SIT_DOWN_ACTIONS_ROW not in chrome:
        return False
    if SIT_DOWN_ACTIONS_FLEX not in chrome:
        return False
    if SIT_DOWN_ACTIONS_PHONE not in chrome:
        return False
    if re.search(r"\.sit-down-actions\{[^}]*display:\s*inline\b", chrome):
        return False
    if any(marker in chrome for marker in SIT_DOWN_INLINE_COPY_MARKERS):
        return False
    if "export honesty, WAVs/AIFF/MIDI preference, no Ableton-first" in chrome:
        return False
    lowered = chrome.lower()
    if lowered.count(SIT_DOWN_FOOTER_HONESTY.lower()) != 1:
        return False
    if "wavs/aiff/midi" not in lowered:
        return False
    if "data-sit-next" not in chrome:
        return False
    if "function updateSitDownCatalogNext(" not in chrome:
        return False
    if "function sessionShowsSongNext(" not in chrome:
        return False
    if "function copySitDownNextStep(" not in chrome:
        return False
    sit_at = chrome.find('<div class="sit-down">')
    if sit_at < 0:
        return False
    work_copy_at = chrome.find('<div class="work-copy">', sit_at)
    sit = chrome[sit_at:work_copy_at if work_copy_at > sit_at else sit_at + 5000]
    actions_at = sit.find(SIT_DOWN_ACTIONS_ROW)
    if actions_at < 0:
        return False
    for marker in ("data-copy-sit-next", "data-copy-logic", "data-copy-file"):
        mark_at = sit.find(marker)
        if mark_at < 0 or mark_at < actions_at:
            return False
    return True


def dashboard_resumes_song_work_privately(html: str) -> bool:
    """Resume must persist only a validated catalog id and work kind."""
    chrome = dashboard_markup_chrome(html)
    required = (
        'id="resumeWork"',
        'id="resumeWorkButton"',
        'id="forgetWorkSession"',
        'id="resumeWorkHint"',
        'id="resumeWorkStatus"',
        'aria-live="polite"',
        "const WORK_SESSION_KEY='vault:last-work:v1'",
        "function parseStoredWorkSession(",
        "function readStoredWorkSession(",
        "function storeWorkSession(",
        "function clearStoredWorkSession(",
        "function resumeLastWorkSession(",
        "function applyWorkHash(",
        "function forgetWorkSessionResult(",
        "function announceWorkSession(",
        "writeVaultHash('','')",
        "Object.keys(value).sort().join('|')!=='id|kind|v'",
        "JSON.stringify(parsed)",
        "Forgot this browser record.",
        "Could not clear this browser record.",
        'id="resumeWorkNext"',
        'id="copyResumeNext"',
        "function copyResumeWorkNext(",
        "function updateResumeWork(",
        'id="catalogOverview"',
        'id="catalogOverviewSummary"',
        'class="resume-actions"',
        "function workKindLabel(",
        "has-resume",
    )
    if not all(marker in chrome for marker in required):
        return False
    resume_at = chrome.find('id="resumeWork"')
    overview_at = chrome.find('id="catalogOverview"')
    starts_at = chrome.find('id="workStarts"')
    button_at = chrome.find('id="resumeWorkButton"')
    next_at = chrome.find('id="resumeWorkNext"')
    copy_at = chrome.find('id="copyResumeNext"')
    forget_at = chrome.find('id="forgetWorkSession"')
    return (
        0 <= resume_at < starts_at < overview_at
        and 0 <= button_at < next_at < copy_at < forget_at
    )


def dashboard_finds_remembered_song_names(html: str) -> bool:
    """Songs search must find existing aliases and rank the closest name first."""
    chrome = dashboard_markup_chrome(html)
    required = (
        "function normalizeSearch(",
        "function songAliases(",
        "function songSearchHit(",
        "function markNormalized(",
        "function focusFoundSong(",
        "function handleSongSearchKey(",
        "closest name first",
        "titles, aliases, hooks",
        "memo lyric",
        "aka ",
    )
    return all(marker in chrome for marker in required)


_MEMO_ESCAPE_SCOPED_ONLY_RE = re.compile(
    r"paneM&&!paneM\.hidden&&activeMemoSong\)"
)


def dashboard_escape_clears_memo_search(html: str) -> bool:
    """Escape on Memo Search must clear a typed query, not only a song scope."""
    chrome = dashboard_markup_chrome(html)
    collapsed = re.sub(r"\s+", "", chrome)
    if _MEMO_ESCAPE_SCOPED_ONLY_RE.search(collapsed):
        return False
    return (
        "function handleVaultKey(" in chrome
        and "activeMemoSong||" in chrome
        and "mq.value||''" in chrome
    )


def dashboard_empty_memo_search_honest(html: str) -> bool:
    """Zero memo hits must not tell the user to clear a song filter that is not set."""
    chrome = dashboard_markup_chrome(html)
    if "clear the song filter or try a different word" in chrome:
        return False
    required = (
        "function emptyMemosCopy(",
        "press Escape or Show all memos",
        "try a different word",
    )
    return all(marker in chrome for marker in required)


def dashboard_memo_query_ranks_catalog_matches(html: str) -> bool:
    """Memo queries rank catalog matches (or a Songs named jump) above unmatched hits."""
    chrome = dashboard_markup_chrome(html)
    if chrome.count("Whisper mishears sung words") != 1:
        return False
    required = (
        "function memoIsCatalogMatched(",
        "function namedSongsForMemoQuery(",
        "function memoResultsStatus(",
        "function memoIntakeLine(",
        "Songs named",
        "catalog matches first",
        'id="memoWhisper"',
        "Whisper mishears sung words",
        'class="intake-loc"',
        ".intake-loc{white-space:nowrap}",
        "Voice&nbsp;Memo&nbsp;Intake",
        "MEMO_VISIBLE_CAP=80",
        "slice(0,MEMO_VISIBLE_CAP)",
        "hit.via==='name'",
    )
    return all(marker in chrome for marker in required)


_MEMO_RAW_INCLUDES_RE = re.compile(
    r"String\(m\.x\|\|''\)\.toLowerCase\(\)\.includes\(term\)"
)
_MEMO_RAW_SNIPPET_RE = re.compile(r"lx\s*=\s*m\.x\.toLowerCase\(\)")
_MEMO_EMPTY_FOLD_SONG_TRUE_RE = re.compile(r"if\(!needle\)return !!songId;")


def dashboard_memo_search_folds_punctuation(html: str) -> bool:
    """Memo Search must fold apostrophes and punctuation the same way Songs does.

    Raw toLowerCase includes miss curly-apostrophe titles such as It's Alright
    when Jeff types the README-taught query without apostrophes. An empty
    folded query in song scope must fail closed — !!songId alone treats !!!
    as show-every-memo.
    """
    chrome = dashboard_markup_chrome(html)
    if _MEMO_RAW_INCLUDES_RE.search(chrome):
        return False
    if _MEMO_RAW_SNIPPET_RE.search(chrome):
        return False
    if _MEMO_EMPTY_FOLD_SONG_TRUE_RE.search(chrome):
        return False
    required = (
        "function memoMatches(",
        "function normalizeSearch(",
        "function normalizedMatchRange(",
        "function memoSnippet(",
        "normalizeSearch(term)",
        "normalizeSearch(field)",
        "function markHay(",
        "markNormalized(text,term)",
        "try: its alright",
        "!String(term||'').trim()&&!!songId",
    )
    return all(marker in chrome for marker in required)


_DISHONEST_TERM_STATUS_RE = re.compile(r"textContent\s*=\s*term\s*\?")


def dashboard_empty_search_honest(html: str) -> bool:
    """Zero song hits must not claim closest-name ranking or a filter that is not set."""
    chrome = dashboard_markup_chrome(html)
    if "clear a filter?" in chrome:
        return False
    if _DISHONEST_TERM_STATUS_RE.search(chrome):
        return False
    required = (
        "function songResultsStatus(",
        "function emptySongsCopy(",
        "press Escape or Clear filters",
        "closest name first",
    )
    return all(marker in chrome for marker in required)


def dashboard_exposes_logic_ready(html: str) -> bool:
    """First useful surface must name a sanitized Logic-ready next action."""
    chrome = dashboard_markup_chrome(html)
    required = (
        'id="logicReady"',
        "Sort: Logic-ready",
        "Any Logic-ready",
        "function logicReadyNext(",
        "function logicReadyLabel(",
        "Copy Logic-ready next",
        'id="workSessionLogic"',
        'id="copyWorkLogic"',
        'id="resumeWorkLogic"',
        'id="copyResumeLogic"',
        "sit-logic",
        "function copyExactSongLogicNext(",
        "function copyCurrentWorkLogic(",
        "function copyResumeLogicNext(",
        "function copySongLogicNext(",
        "LOGIC_READY",
        "Do not invent one here",
        "This page does not open audio",
        "function logicReadyFormats(",
        "Assets on file",
    )
    if not all(marker in chrome for marker in required):
        return False
    return not logic_ready_next_leaks_private_locators()


# 390×844 (iPhone CSS width) must hit phone padding / 2-up stats. 375px-only misses it.
PHONE_LAYOUT_MAX_WIDTH_PX = 640
PHONE_LAYOUT_MIN_COVER_PX = 400
PHONE_BODY_PADDING_VALUE = "12px"
PHONE_STAT_FLEX_BASIS = "calc(50% - 10px)"
PHONE_BODY_PADDING_CSS = f"body{{padding:{PHONE_BODY_PADDING_VALUE}"
PHONE_TWO_UP_STATS_CSS = f".stat{{min-width:0;flex-basis:{PHONE_STAT_FLEX_BASIS}}}"
PHONE_LAYOUT_MEDIA = f"@media(max-width:{PHONE_LAYOUT_MAX_WIDTH_PX}px)"
_PHONE_MAX_WIDTH_MQ_RE = re.compile(r"@media\(max-width:(\d+)px\)\{")
_STYLE_BLOCK_RE = re.compile(r"<style>(.*?)</style>", re.I | re.S)
_WIDTH_MEDIA_RE = re.compile(
    r"@media\s*\(\s*(min|max)-width\s*:\s*(\d+)px\s*\)",
    re.I,
)


def _css_rule_block_at(text: str, start: int) -> str:
    """Return the CSS inside a `{...}` block that starts at `start` (after `{`)."""
    depth = 1
    index = start
    while index < len(text) and depth:
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    if depth != 0:
        return ""
    return text[start : index - 1]


def _css_declarations(block: str) -> dict[str, str]:
    return {
        key.strip(): value.strip()
        for key, value in re.findall(r"([\w-]+)\s*:\s*([^;{}]+)", block)
    }


def _css_sources_for_layout(html: str) -> list[str]:
    """Prefer `<style>` text so script braces cannot masquerade as CSS."""
    chrome = dashboard_markup_chrome(html)
    blocks = [block.strip() for block in _STYLE_BLOCK_RE.findall(chrome) if block.strip()]
    return blocks or [chrome]


def _apply_computed_home_layout(text: str, width_px: int, layout: dict[str, str | None]) -> None:
    """Walk rules in source order and keep the last matching body/.stat values."""
    index = 0
    while True:
        brace = text.find("{", index)
        if brace < 0:
            return
        prefix_at = brace
        while prefix_at > 0 and text[prefix_at - 1] not in "{}":
            prefix_at -= 1
        prefix = text[prefix_at:brace].strip()
        block = _css_rule_block_at(text, brace + 1)
        next_index = brace + 1 + len(block) + 1
        if prefix.startswith("@media"):
            match = _WIDTH_MEDIA_RE.fullmatch(prefix)
            applies = False
            if match:
                kind, bound = match.group(1).lower(), int(match.group(2))
                applies = (
                    (kind == "max" and width_px <= bound)
                    or (kind == "min" and width_px >= bound)
                )
            if applies:
                _apply_computed_home_layout(block, width_px, layout)
        elif prefix == "body":
            padding = _css_declarations(block).get("padding")
            if padding is not None:
                layout["padding"] = padding
        elif prefix == ".stat":
            flex_basis = _css_declarations(block).get("flex-basis")
            if flex_basis is not None:
                layout["stat_flex_basis"] = flex_basis
        index = next_index


def dashboard_computed_home_layout(html: str, width_px: int = 390) -> dict[str, str | None]:
    """Winning `body` padding and `.stat` flex-basis after matching width queries.

    Later declarations win, so a 640px phone block does not count if an unscoped
    `body{padding:20px}` follows it. A 375px-only query never applies at 390.
    """
    layout: dict[str, str | None] = {"padding": None, "stat_flex_basis": None}
    for source in _css_sources_for_layout(html):
        _apply_computed_home_layout(source, width_px, layout)
    return layout


def dashboard_phone_layout_covers(html: str, width_px: int = 390) -> bool:
    """True when tighter padding and 2-up stats apply at `width_px`.

    A 375px-only query never covers 390. The live breakpoint is 640px
    (must be at least 400px) so a 390×844 home view gets the phone tweaks.
    """
    chrome = dashboard_markup_chrome(html)
    for match in _PHONE_MAX_WIDTH_MQ_RE.finditer(chrome):
        max_width = int(match.group(1))
        if max_width < PHONE_LAYOUT_MIN_COVER_PX or width_px > max_width:
            continue
        block = _css_rule_block_at(chrome, match.end())
        if PHONE_BODY_PADDING_CSS in block and PHONE_TWO_UP_STATS_CSS in block:
            return True
    return False


def dashboard_phone_and_a11y_ready(html: str) -> bool:
    """Phone sit-down at 640px (covers 390px) plus landmarks, names, contrast, and focus."""
    chrome = dashboard_markup_chrome(html)
    phone = dashboard_computed_home_layout(chrome, 390)
    required = (
        'class="skip-link"',
        'href="#workNowTitle"',
        '<h2 id="workNowTitle" tabindex="-1">',
        "<header>",
        '<main id="main"',
        "<footer",
        'role="tablist"',
        'aria-label="Sort songs"',
        'aria-label="Search memo transcripts"',
        PHONE_LAYOUT_MEDIA,
        PHONE_BODY_PADDING_CSS,
        PHONE_TWO_UP_STATS_CSS,
        "min-height:44px",
        "overflow-x:hidden",
        ":focus-visible",
        'class="score-lab"',
        'class="row-heading"',
        'aria-controls="song-detail-',
        "--ink3:#a8a79c",
        "--ink3:#5c5b54",
    )
    return (
        all(marker in chrome for marker in required)
        and 'role="columnheader"' not in chrome
        and dashboard_phone_layout_covers(chrome, 390)
        and phone["padding"] == PHONE_BODY_PADDING_VALUE
        and phone["stat_flex_basis"] == PHONE_STAT_FLEX_BASIS
    )


def dashboard_search_results_keyboard_ready(html: str) -> bool:
    """Songs/Memo search results use arrow keys, Enter, and a visible dark-theme focus."""
    chrome = dashboard_markup_chrome(html)
    required = (
        "function nextSearchCursor(",
        "function searchActivateId(",
        "function searchActivateMemoSong(",
        "function paintSearchFocus(",
        "function handleSongSearchKey(",
        "function handleMemoSearchKey(",
        "ArrowDown",
        "ArrowUp",
        "aria-activedescendant",
        "search-focus",
        ".rhead.search-focus,.mopt.search-focus",
        "outline:2px solid var(--pot)",
        "if(!term&&!(cursor>=0))return false",
        "paintSearchFocus(list,'.rhead',cur,'search-focus')",
        'id="list" role="listbox"',
        'id="mlist" role="listbox"',
        'class="rhead" role="option"',
        'class="mopt" role="option"',
    )
    return (
        all(marker in chrome for marker in required)
        and 'class="row" role="option"' not in chrome
        and 'class="mrow" role="option"' not in chrome
    )


def dashboard_tablist_keyboard_ready(html: str) -> bool:
    """Songs/Memo tabs follow APG: roving tabindex plus arrow/Home/End keys."""
    chrome = dashboard_markup_chrome(html)
    required = (
        'role="tablist"',
        'aria-orientation="horizontal"',
        'id="tabS" role="tab" aria-controls="paneS" aria-selected="true" tabindex="0"',
        'id="tabM" role="tab" aria-controls="paneM" aria-selected="false" tabindex="-1"',
        "function nextVaultTab(",
        "function activateVaultTab(",
        "function handleVaultTabKey(",
        "ArrowRight",
        "ArrowLeft",
        "tabS.tabIndex=",
        "tabM.tabIndex=",
    )
    return all(marker in chrome for marker in required)


def _html_id_at(html: str, value: str) -> int:
    """Index of an exact id attribute, not a longer id that starts with the same letters."""
    needle = f'id="{value}"'
    start = 0
    while True:
        at = html.find(needle, start)
        if at < 0:
            return -1
        end = at + len(needle)
        if end >= len(html) or html[end] in " >\n\t'":
            return at
        start = end


def dashboard_first_paint_ready(html: str) -> bool:
    """First paint keeps H1, one honesty sentence, and Write/Produce/Listen above the fold."""
    chrome = dashboard_markup_chrome(html)
    lowered = chrome.lower()
    if "no audio in this repo" not in lowered:
        return False
    if "catalog rows are not the live set" not in lowered:
        return False
    required = (
        'id="workStarts"',
        'id="statsFold"',
        'id="statsLine"',
        "const COVER_COUNT",
        "const RECOVERED_COUNT",
        "<details",
        "data-open-work=",
    )
    if not all(marker in chrome for marker in required):
        return False
    work_at = _html_id_at(chrome, "workStarts")
    fold_at = _html_id_at(chrome, "statsFold")
    stats_at = _html_id_at(chrome, "stats")
    resume_at = _html_id_at(chrome, "resumeWork")
    if min(work_at, fold_at, stats_at) < 0:
        return False
    if resume_at >= 0 and resume_at > work_at:
        return False
    return work_at < fold_at < stats_at


def dashboard_catalog_overview_starts_collapsed(html: str) -> bool:
    """First paint must not auto-open catalog subtitle/counts; summary stays visible."""
    chrome = dashboard_markup_chrome(html)
    if 'id="catalogOverview"' not in chrome:
        return False
    if 'id="catalogOverviewSummary"' not in chrome:
        return False
    overview = re.search(r"<details[^>]*id=\"catalogOverview\"[^>]*>", chrome)
    if overview and re.search(r"\bopen\b", overview.group(0)):
        return False
    if "id=\"catalogOverview\" open" in chrome or "open id=\"catalogOverview\"" in chrome:
        return False
    summary = re.search(r"<summary[^>]*id=\"catalogOverviewSummary\"[^>]*>", chrome)
    if summary and re.search(r"\bhidden\b", summary.group(0)):
        return False
    if (
        "id=\"catalogOverviewSummary\" hidden" in chrome
        or "hidden id=\"catalogOverviewSummary\"" in chrome
    ):
        return False
    if "catalogOverviewSummary.hidden=false" not in chrome:
        return False
    if "catalogOverview.open=!saved" in chrome:
        return False
    return True


def dashboard_start_copy_omits_resume_preview(html: str) -> bool:
    """Cold-start copy names Write/Produce/Listen and Refresh, not Resume/Forget."""
    chrome = dashboard_markup_chrome(html)
    match = re.search(r'<p class="work-now-copy">(.*?)</p>', chrome, re.S)
    if not match:
        return False
    copy = match.group(1).lower()
    if "resume" in copy or "forget" in copy:
        return False
    return (
        "write" in copy
        and "produce" in copy
        and "listen" in copy
        and "highest-momentum" in copy
        and "refresh" in copy
    )


def dashboard_resume_leads_first_paint(html: str) -> bool:
    """A stored session must lead with Resume, Do this now, Copy, and Forget."""
    chrome = dashboard_markup_chrome(html)
    required = (
        'id="resumeWork"',
        'id="resumeWorkButton"',
        'id="resumeWorkNext"',
        'id="copyResumeNext"',
        'id="forgetWorkSession"',
        "Resume ",
        "Do this now",
        "Copy next step",
        "Forget",
        "has-resume",
        "Object.keys(value).sort().join('|')!=='id|kind|v'",
    )
    if not all(marker in chrome for marker in required):
        return False
    resume_at = _html_id_at(chrome, "resumeWork")
    next_at = _html_id_at(chrome, "resumeWorkNext")
    copy_at = _html_id_at(chrome, "copyResumeNext")
    forget_at = _html_id_at(chrome, "forgetWorkSession")
    work_at = _html_id_at(chrome, "workStarts")
    if min(resume_at, next_at, copy_at, forget_at, work_at) < 0:
        return False
    return resume_at < next_at < copy_at < forget_at < work_at


def dashboard_work_next_stays_in_view(html: str) -> bool:
    """Work-session next step must stay on screen while the song expands."""
    chrome = dashboard_markup_chrome(html)
    return (
        "scrollIntoView({block:'nearest'})" in chrome
        and 'id="workSession"' in chrome
        and "#workSession{position:sticky" in chrome
        and "overflow-x:clip" in chrome
        and "function focusWorkSong(" in chrome
        and "toggleSong(head,true)" in chrome
        and "sessionEl.scrollIntoView({block:'nearest'})" in chrome
    )


def dashboard_listen_is_not_playback(html: str) -> bool:
    """Listen is a Logic sit-down, not in-page audio playback."""
    chrome = dashboard_markup_chrome(html)
    lowered = chrome.lower()
    return (
        "Listen in Logic" in chrome
        and "function workKindLabel(" in chrome
        and "this page does not open audio" in lowered
        and "<audio" not in lowered
        and (
            'data-open-work="listen"' in chrome
            or 'data-open-work="${kind}"' in chrome
        )
    )


def dashboard_work_starts_name_the_action(html: str) -> bool:
    """Write / Produce / Listen must start one highest-momentum match.

    Visible counts are queue size, not an instruction to write N songs.
    The accessible name must say Start and highest-momentum match.
    """
    chrome = dashboard_markup_chrome(html or "")
    if "${workCounts[kind]} songs" in chrome:
        return False
    required = (
        "function workStartLabel(",
        "function workKindLabel(",
        "highest-momentum match",
        "in queue",
        "${workCounts[kind]} in queue",
        'aria-label="${workStartLabel(kind,workCounts[kind])}"',
        'data-open-work="${kind}"',
    )
    return all(marker in chrome for marker in required)


# WCAG 2 relative-luminance threshold for sRGB (not the older 0.03928 form).
_SRGB_LINEAR_CUTOFF = 0.04045
WCAG_AA_NORMAL_TEXT = 4.5
_CSS_ROOT_RE = re.compile(r":root\{([^}]+)\}")
_CSS_TOKEN_RE = re.compile(r"--([a-z0-9]+):#([0-9a-fA-F]{6})")
_LIGHT_SCHEME_MQ_RE = re.compile(
    r"@media\s*\(\s*prefers-color-scheme\s*:\s*light\s*\)",
    re.IGNORECASE,
)
_LIGHT_SCHEME_ROOT_RE = re.compile(
    r"@media\s*\(\s*prefers-color-scheme\s*:\s*light\s*\)\s*\{:root\{([^}]+)\}\}",
    re.IGNORECASE,
)
_PRODUCE_PILL_COLOR_RE = re.compile(
    r"\.pill\.wk-produce\s*\{\s*color\s*:\s*var\(\s*--rdy\s*\)",
)
_LISTEN_PILL_COLOR_RE = re.compile(
    r"\.pill\.wk-listen\s*\{\s*color\s*:\s*var\(\s*--listen\s*\)",
)
_QUICK_WIN_COLOR_RE = re.compile(
    r"\.tag\.q\s*\{\s*color\s*:\s*var\(\s*--good\s*\)",
)
_WRITE_PILL_COLOR_RE = re.compile(
    r"\.pill\.wk-write\s*\{\s*color\s*:\s*var\(\s*--write\s*\)",
)
_LINK_WRITE_COLOR_RE = re.compile(
    r"\.memo-link,\s*\.song-link\s*\{[^}]*color\s*:\s*var\(\s*--write\s*\)",
)
_FLAGSHIP_WRITE_COLOR_RE = re.compile(
    r"\.tag\.f\s*\{\s*color\s*:\s*var\(\s*--write\s*\)",
)
_BAR_NUMBER_INK_RE = re.compile(
    r"\.bar-n\s*\{\s*color\s*:\s*var\(\s*--ink\s*\)",
)
_OLD_LISTEN_ON_MOM_RE = re.compile(
    r"\.pill\.wk-listen\s*\{\s*color\s*:\s*var\(\s*--mom\s*\)"
)


_OLD_WRITE_ON_POT_RE = re.compile(
    r"(?:\.pill\.wk-write|\.memo-link,\s*\.song-link|\.tag\.f)\s*\{[^}]*color\s*:\s*var\(\s*--pot\s*\)"
)


def hex_srgb_luminance(color: str) -> float:
    """WCAG 2 relative luminance for a #RRGGBB token."""
    raw = str(color or "").strip().lstrip("#")
    if len(raw) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in raw):
        raise ValueError(f"expected #RRGGBB, got {color!r}")
    channels = (int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16))

    def linear(channel: int) -> float:
        srgb = channel / 255.0
        if srgb <= _SRGB_LINEAR_CUTOFF:
            return srgb / 12.92
        return ((srgb + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    """WCAG 2 contrast ratio between two #RRGGBB colors."""
    lighter, darker = sorted(
        (hex_srgb_luminance(foreground), hex_srgb_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def _css_root_tokens(block: str) -> dict[str, str]:
    return {
        name: f"#{value.lower()}" for name, value in _CSS_TOKEN_RE.findall(block or "")
    }


def dashboard_theme_tokens(html: str) -> tuple[dict[str, str], dict[str, str]]:
    """Default (dark) :root tokens, then the light-scheme :root override."""
    chrome = dashboard_markup_chrome(html or "")
    light_match = _LIGHT_SCHEME_ROOT_RE.search(chrome)
    light = _css_root_tokens(light_match.group(1) if light_match else "")
    without_light = _LIGHT_SCHEME_ROOT_RE.sub("", chrome)
    dark_match = _CSS_ROOT_RE.search(without_light)
    dark = _css_root_tokens(dark_match.group(1) if dark_match else "")
    return dark, light


_DARK_HTML_THEME_RE = re.compile(
    r"<html\b[^>]*\bdata-theme\s*=\s*(['\"])dark\1",
    re.IGNORECASE,
)
_COLOR_SCHEME_META_RE = re.compile(
    r"<meta\b[^>]*\bname\s*=\s*['\"]color-scheme['\"][^>]*\bcontent\s*=\s*['\"]dark['\"]"
    r"|<meta\b[^>]*\bcontent\s*=\s*['\"]dark['\"][^>]*\bname\s*=\s*['\"]color-scheme['\"]",
    re.IGNORECASE,
)
_DARK_LOCK_RE = re.compile(
    r"html\[data-theme=(['\"])dark\1\]\s*\{([^}]+)\}",
    re.IGNORECASE,
)
_COLOR_SCHEME_DARK_DECL_RE = re.compile(r"color-scheme\s*:\s*dark\b", re.IGNORECASE)
_DARK_BG_MAX_LUMINANCE = 0.05
_DARK_INK_MIN_LUMINANCE = 0.80
_HARSH_BLACK = "#000000"
_REQUIRED_DARK_LOCK_TOKENS = (
    "bg",
    "card",
    "card2",
    "ink",
    "ink2",
    "ink3",
    "line",
    "pot",
    "write",
    "rdy",
    "mom",
    "listen",
    "good",
)


def dashboard_dark_theme_default(html: str) -> bool:
    """Jeff's dashboard paints dark by default; OS light must not win.

    :root stays the dark token source. The light-scheme palette remains for
    AA gates. html[data-theme=dark] after that query re-asserts the same
    tokens so a light OS cannot flip the page. #000 is rejected as harsh.
    """
    chrome = dashboard_markup_chrome(html or "")
    if not _DARK_HTML_THEME_RE.search(chrome):
        return False
    if not _COLOR_SCHEME_META_RE.search(chrome):
        return False
    if not _COLOR_SCHEME_DARK_DECL_RE.search(chrome):
        return False
    if not _LIGHT_SCHEME_MQ_RE.search(chrome):
        return False
    dark, _light = dashboard_theme_tokens(chrome)
    for name in _REQUIRED_DARK_LOCK_TOKENS:
        if not dark.get(name):
            return False
    if dark["bg"] == _HARSH_BLACK:
        return False
    try:
        if hex_srgb_luminance(dark["bg"]) > _DARK_BG_MAX_LUMINANCE:
            return False
        if hex_srgb_luminance(dark["ink"]) < _DARK_INK_MIN_LUMINANCE:
            return False
    except ValueError:
        return False
    lock = _DARK_LOCK_RE.search(chrome)
    if not lock:
        return False
    locked = _css_root_tokens(lock.group(2))
    for name in _REQUIRED_DARK_LOCK_TOKENS:
        if locked.get(name) != dark.get(name):
            return False
    collapsed_lock = re.sub(r"\s+", "", lock.group(2).lower())
    if "color-scheme:dark" not in collapsed_lock:
        return False
    light_at = chrome.lower().find("@media (prefers-color-scheme: light)")
    lock_at = chrome.lower().find("html[data-theme=")
    if light_at < 0 or lock_at < 0 or lock_at < light_at:
        return False
    for fg_name, bg_name in (
        ("ink", "bg"),
        ("ink", "card"),
        ("ink", "card2"),
        ("ink2", "bg"),
        ("ink2", "card"),
        ("ink2", "card2"),
        ("ink3", "bg"),
        ("ink3", "card"),
        ("ink3", "card2"),
        ("write", "bg"),
        ("write", "card"),
        ("write", "card2"),
        ("rdy", "bg"),
        ("rdy", "card"),
        ("listen", "bg"),
        ("listen", "card"),
        ("good", "bg"),
        ("good", "card"),
    ):
        fg, bg = dark.get(fg_name), dark.get(bg_name)
        if not fg or not bg:
            return False
        if contrast_ratio(fg, bg) < WCAG_AA_NORMAL_TEXT:
            return False
    return contrast_ratio(dark["bg"], dark["ink"]) >= WCAG_AA_NORMAL_TEXT


def dashboard_listen_contrast_ready(html: str) -> bool:
    """Listen pills and Quick-win/Copied/--good text meet WCAG AA 4.5:1.

    Momentum bar fills may keep --mom. Listen text uses --listen. Quick win,
    Copied, and YES-gate text keep --good, retuned to the same AA greens.
    """
    chrome = dashboard_markup_chrome(html or "")
    if not _LIGHT_SCHEME_MQ_RE.search(chrome):
        return False
    if not _LISTEN_PILL_COLOR_RE.search(chrome):
        return False
    if not _QUICK_WIN_COLOR_RE.search(chrome):
        return False
    if _OLD_LISTEN_ON_MOM_RE.search(chrome):
        return False
    dark, light = dashboard_theme_tokens(chrome)
    for theme in (dark, light):
        listen = theme.get("listen")
        good = theme.get("good")
        background = theme.get("bg")
        card = theme.get("card")
        card2 = theme.get("card2")
        if not listen or not good or not background or not card or not card2:
            return False
        for token in (listen, good):
            if contrast_ratio(token, background) < WCAG_AA_NORMAL_TEXT:
                return False
            if contrast_ratio(token, card) < WCAG_AA_NORMAL_TEXT:
                return False
            if contrast_ratio(token, card2) < WCAG_AA_NORMAL_TEXT:
                return False
    return True


def dashboard_write_contrast_ready(html: str) -> bool:
    """Write pills, flagship tag, and song/memo links meet WCAG AA 4.5:1.

    Bar fills, skip-link, and search marks may keep --pot. Text uses --write
    so those fills are not forced into the same token. Light-scheme stays.
    """
    chrome = dashboard_markup_chrome(html or "")
    if not _LIGHT_SCHEME_MQ_RE.search(chrome):
        return False
    if not _WRITE_PILL_COLOR_RE.search(chrome):
        return False
    if not _LINK_WRITE_COLOR_RE.search(chrome):
        return False
    if not _FLAGSHIP_WRITE_COLOR_RE.search(chrome):
        return False
    if _OLD_WRITE_ON_POT_RE.search(chrome):
        return False
    dark, light = dashboard_theme_tokens(chrome)
    for theme in (dark, light):
        write = theme.get("write")
        background = theme.get("bg")
        card = theme.get("card")
        card2 = theme.get("card2")
        if not write or not background or not card or not card2:
            return False
        if contrast_ratio(write, background) < WCAG_AA_NORMAL_TEXT:
            return False
        if contrast_ratio(write, card) < WCAG_AA_NORMAL_TEXT:
            return False
        if contrast_ratio(write, card2) < WCAG_AA_NORMAL_TEXT:
            return False
    return True


def dashboard_rdy_contrast_ready(html: str) -> bool:
    """Produce/readiness text meets WCAG AA 4.5:1 on --bg and --card.

    Bar fills may stay colorful. Numeric labels must use --ink. The
    light-scheme media query must stay. Produce pills keep --rdy.
    """
    chrome = dashboard_markup_chrome(html or "")
    if not _LIGHT_SCHEME_MQ_RE.search(chrome):
        return False
    if not _PRODUCE_PILL_COLOR_RE.search(chrome):
        return False
    if not _BAR_NUMBER_INK_RE.search(chrome):
        return False
    if 'class="bar-n"' not in chrome:
        return False
    dark, light = dashboard_theme_tokens(chrome)
    for theme in (dark, light):
        ready = theme.get("rdy")
        background = theme.get("bg")
        card = theme.get("card")
        if not ready or not background or not card:
            return False
        if contrast_ratio(ready, background) < WCAG_AA_NORMAL_TEXT:
            return False
        if contrast_ratio(ready, card) < WCAG_AA_NORMAL_TEXT:
            return False
    return True


_SKIP_LINK_RULE_RE = re.compile(r"\.skip-link\s*\{([^}]*)\}", re.IGNORECASE)
_SEARCH_MARK_RULE_RE = re.compile(
    r"\.msnip\s+mark\s*,\s*\.rtitle\s+mark\s*,\s*\.aka-hit\s+mark\s*\{([^}]*)\}",
    re.IGNORECASE,
)
_CSS_DECL_RE = re.compile(r"([a-z-]+)\s*:\s*([^;]+)", re.IGNORECASE)
_CSS_VAR_RE = re.compile(r"^var\(\s*--([a-z0-9]+)\s*\)$", re.IGNORECASE)


def _css_declarations(block: str) -> dict[str, str]:
    return {
        name.lower(): value.strip()
        for name, value in _CSS_DECL_RE.findall(block or "")
    }


def _resolve_theme_color(value: str, theme: dict[str, str]) -> str | None:
    raw = (value or "").strip()
    if raw.startswith("#"):
        hex_value = raw.lower()
        if len(hex_value) == 4 and all(ch in "0123456789abcdef#" for ch in hex_value):
            return "#" + "".join(ch * 2 for ch in hex_value[1:])
        if len(hex_value) == 7:
            return hex_value
        return None
    match = _CSS_VAR_RE.fullmatch(raw)
    if not match:
        return None
    return theme.get(match.group(1).lower())


def dashboard_skip_link_contrast_ready(html: str) -> bool:
    """Skip link text must meet WCAG AA 4.5:1 on dark and light themes.

    White-on-`--pot` fails AA. Use `--ink` on `--bg` (or another pair that
    actually meets 4.5:1) so the first keyboard control stays readable.
    """
    chrome = dashboard_markup_chrome(html or "")
    if not _LIGHT_SCHEME_MQ_RE.search(chrome):
        return False
    rule = _SKIP_LINK_RULE_RE.search(chrome)
    if not rule:
        return False
    decls = _css_declarations(rule.group(1))
    background = decls.get("background") or decls.get("background-color")
    foreground = decls.get("color")
    if not background or not foreground:
        return False
    collapsed = re.sub(r"\s+", "", rule.group(1).lower())
    if "background:var(--pot)" in collapsed and (
        "color:#fff" in collapsed or "color:#ffffff" in collapsed
    ):
        return False
    dark, light = dashboard_theme_tokens(chrome)
    for theme in (dark, light):
        fg = _resolve_theme_color(foreground, theme)
        bg = _resolve_theme_color(background, theme)
        if not fg or not bg:
            return False
        if contrast_ratio(fg, bg) < WCAG_AA_NORMAL_TEXT:
            return False
    return True


def dashboard_search_mark_contrast_ready(html: str) -> bool:
    """Search-hit marks must meet WCAG AA 4.5:1 on dark and light themes.

    White-on-`--pot` fails AA at 14px. Use `--ink` on `--bg` (or another
    pair that actually meets 4.5:1) so title, alias, and memo hits stay
    readable.
    """
    chrome = dashboard_markup_chrome(html or "")
    if not _LIGHT_SCHEME_MQ_RE.search(chrome):
        return False
    rule = _SEARCH_MARK_RULE_RE.search(chrome)
    if not rule:
        return False
    decls = _css_declarations(rule.group(1))
    background = decls.get("background") or decls.get("background-color")
    foreground = decls.get("color")
    if not background or not foreground:
        return False
    collapsed = re.sub(r"\s+", "", rule.group(1).lower())
    if "background:var(--pot)" in collapsed and (
        "color:#fff" in collapsed or "color:#ffffff" in collapsed
    ):
        return False
    dark, light = dashboard_theme_tokens(chrome)
    for theme in (dark, light):
        fg = _resolve_theme_color(foreground, theme)
        bg = _resolve_theme_color(background, theme)
        if not fg or not bg:
            return False
        if contrast_ratio(fg, bg) < WCAG_AA_NORMAL_TEXT:
            return False
    return True


def _readme_h2_headings(text: str) -> list[str]:
    return [
        line.strip()
        for line in (text or "").splitlines()
        if line.startswith("## ")
    ]


def readme_click_test_does_not_claim_private(text: str) -> bool:
    """Public README must not title the click-test as a private session."""
    return not any(
        heading.lower() == "## click-test the private session"
        for heading in _readme_h2_headings(text)
    )


def readme_click_test_uses_browser_local_heading(text: str) -> bool:
    """If a Click-test heading is present, it must say browser-local."""
    click_headings = [
        heading
        for heading in _readme_h2_headings(text)
        if heading.lower().startswith("## click-test")
    ]
    if not click_headings:
        return True
    return all("browser-local" in heading.lower() for heading in click_headings)


def readme_documents_session_click_test(text: str) -> bool:
    """Jeff-facing README must match the real browser-local session click path."""
    body = (text or "").lower()
    return (
        "click write, produce, or listen" in body
        and "refresh" in body
        and "resume" in body
        and "forget" in body
        and "work kind" in body
        and "catalog id" in body
        and "copy next step" in body
        and "do this now" in body
        and "session log" in body
        and "sit-down" in body
        and "logic" in body
        and "export honesty" in body
        and "wavs/aiff/midi" in body
        and "no ableton-first" in body
        and "logic-ready next" in body
        and "copy logic-ready next" in body
    )
