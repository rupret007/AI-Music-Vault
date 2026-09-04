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
    r"\([^()]{0,200}\.(?:wav|aiff|aif|logicx|m4a|mp3|flac|band)\)|"
    r"\b[\w./' -]+\.(?:wav|aiff|aif|logicx|m4a|mp3|flac|band)\b|"
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

# Locked hashes of the embedded DATA / TX JSON blobs on main 2ff49baa.
# Prefer unchanged. A real product test may document a fixture-only change.
EMBEDDED_DATA_SHA256 = (
    "1b057c495207674cf7ae5392dc275791dd563b5fe6307a5c6be7259690cc20f4"
)
EMBEDDED_TX_SHA256 = (
    "4d809dc53540f8c5acfe63ffcee94844634405c2a0583b2accddc9178807b467"
)


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
    if re.search(r"\.(wav|aiff|aif|logicx|m4a|mp3|flac|band)\b", low):
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
    )


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
    )
    return all(marker in chrome for marker in required)


def readme_documents_session_click_test(text: str) -> bool:
    """Jeff-facing README must match the real private-session click path."""
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
    )
