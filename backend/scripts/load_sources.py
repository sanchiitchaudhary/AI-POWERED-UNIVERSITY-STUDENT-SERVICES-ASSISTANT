"""Validate and idempotently load Annex B source-register CSV rows."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_conn, init_db

SOURCE_COLUMNS = (
    "doc_id", "title", "issuer", "authority_level", "doc_type", "version",
    "effective_from", "effective_to", "supersedes", "scope_programmes",
    "scope_batches", "provenance", "retrieved_on", "synthetic",
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _valid_date(value: str, label: str, *, optional: bool = False) -> None:
    if optional and value == "":
        return
    if not DATE_RE.fullmatch(value):
        raise ValueError(f"{label} must use YYYY-MM-DD format")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid YYYY-MM-DD date") from exc


def validate_source_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return normalized source rows or fail before any database writes."""
    normalized = []
    seen = set()
    for line, row in enumerate(rows, 2):
        missing = [column for column in SOURCE_COLUMNS if column not in row]
        if missing:
            raise ValueError(f"Source CSV row {line}: missing columns: {', '.join(missing)}")
        current = {column: str(row.get(column, "") or "").strip() for column in SOURCE_COLUMNS}
        if not current["doc_id"]:
            raise ValueError(f"Source CSV row {line}: doc_id is required")
        if current["doc_id"] in seen:
            raise ValueError(f"Source CSV row {line}: duplicate doc_id {current['doc_id']!r}")
        seen.add(current["doc_id"])
        try:
            authority = int(current["authority_level"])
        except ValueError as exc:
            raise ValueError(f"Source CSV row {line}, {current['doc_id']}: authority_level must be an integer from 1 to 5") from exc
        if authority not in {1, 2, 3, 4, 5}:
            raise ValueError(f"Source CSV row {line}, {current['doc_id']}: authority_level must be from 1 to 5")
        current["authority_level"] = authority
        _valid_date(current["effective_from"], f"Source CSV row {line}, {current['doc_id']} effective_from")
        _valid_date(current["effective_to"], f"Source CSV row {line}, {current['doc_id']} effective_to", optional=True)
        if current["synthetic"] not in {"Y", "N"}:
            raise ValueError(f"Source CSV row {line}, {current['doc_id']}: synthetic must be Y or N")
        current["synthetic"] = int(current["synthetic"] == "Y")
        normalized.append(current)
    return normalized


def load_source_rows(rows: Iterable[dict[str, Any]], conn) -> int:
    """Upsert validated source rows using the supplied SQLite connection."""
    normalized = validate_source_rows(rows)
    placeholders = ",".join("?" for _ in SOURCE_COLUMNS)
    updates = ",".join(f"{column}=excluded.{column}" for column in SOURCE_COLUMNS if column != "doc_id")
    sql = f"INSERT INTO source_register ({','.join(SOURCE_COLUMNS)}) VALUES ({placeholders}) ON CONFLICT(doc_id) DO UPDATE SET {updates}"
    values = [tuple(row[column] for column in SOURCE_COLUMNS) for row in normalized]
    with conn:
        conn.executemany(sql, values)
    return len(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--db", default=None)
    args = parser.parse_args()
    try:
        with Path(args.csv).open(newline="", encoding="utf-8-sig") as file:
            rows = list(csv.DictReader(file))
        init_db(args.db)
        with get_conn(args.db) as conn:
            count = load_source_rows(rows, conn)
    except (OSError, csv.Error, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Loaded {count} source register row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
