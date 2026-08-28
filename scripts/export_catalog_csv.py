#!/usr/bin/env python3
"""
export_catalog_csv.py — derived tabular view of the spine.

Vault (data/master_catalog.json) is the song brain.
data/master_catalog.csv is the same songs[], not a second catalog.
This script projects the committed spine into the existing CSV columns
so the table cannot silently stay 11 rows behind.

Do not invent songs. Do not rewrite feel. Catalog rows are not the
official live set. Show Night owns official sets.

Run:  python3 scripts/export_catalog_csv.py
Check: python3 scripts/export_catalog_csv.py --check
Out:  data/master_catalog.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(HERE, "data", "master_catalog.json")
OUT = os.path.join(HERE, "data", "master_catalog.csv")

CSV_FIELDS = (
    "song_id",
    "canonical_title",
    "artist_project",
    "classification",
    "alt_titles",
    "writers",
    "rights_confidence",
    "stage",
    "key",
    "bpm",
    "potential",
    "readiness",
    "confidence",
    "lyric_status",
    "audio_status",
    "theme",
    "hook",
    "sources",
    "soundcloud",
    "best_source",
    "next_action",
    "open_questions",
    "notes",
)

COVER_CSV_FIELDS = ("title", "original_artist", "context")

LIST_FIELDS = ("alt_titles", "writers", "sources", "soundcloud")


def _join_list(value) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if str(item).strip())
    return str(value)


def _cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def csv_row_from_song(song: dict) -> dict[str, str]:
    row: dict[str, str] = {}
    for field in CSV_FIELDS:
        value = song.get(field)
        if field in LIST_FIELDS:
            row[field] = _join_list(value)
        else:
            row[field] = _cell(value)
    return row


def csv_rows_from_catalog(cat: dict) -> list[dict[str, str]]:
    songs = cat.get("songs") or []
    return [csv_row_from_song(song) for song in songs if isinstance(song, dict)]


def covers_rows_from_catalog(cat: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for cover in cat.get("covers") or []:
        if not isinstance(cover, dict):
            continue
        rows.append(
            {
                "title": _cell(cover.get("title")),
                "original_artist": _cell(cover.get("original_artist")),
                "context": _cell(cover.get("context")),
            }
        )
    return rows


def comparable_csv(rows: list[dict]) -> list[tuple[str, ...]]:
    out: list[tuple[str, ...]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append(tuple(str(row.get(field) or "") for field in CSV_FIELDS))
    return out


def comparable_covers(rows: list[dict]) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append(
            (
                str(row.get("title") or ""),
                str(row.get("original_artist") or ""),
                str(row.get("context") or ""),
            )
        )
    return out


def write_catalog_csv(cat: dict, path: str = OUT) -> None:
    rows = csv_rows_from_catalog(cat)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def check_committed(cat: dict, path: str = OUT) -> list[str]:
    if not os.path.exists(path):
        return [f"missing derived catalog CSV at {path}"]
    with open(path, encoding="utf-8", newline="") as handle:
        committed = list(csv.DictReader(handle))
    expected = csv_rows_from_catalog(cat)
    if comparable_csv(committed) == comparable_csv(expected):
        return []
    return [
        "data/master_catalog.csv is stale vs data/master_catalog.json — "
        "re-run python3 scripts/export_catalog_csv.py"
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export the derived catalog CSV from the spine"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if data/master_catalog.csv does not match the spine",
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
        print(f"export OK — {OUT} matches data/master_catalog.json")
        return 0

    write_catalog_csv(cat)
    rows = csv_rows_from_catalog(cat)
    print(f"wrote {OUT}")
    print(f"  {len(rows)} rows · derived from the spine · not a second catalog")
    print("  catalog rows are not the official set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
