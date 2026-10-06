"""Validate and idempotently load Annex C rule-registry CSV rows."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_conn, init_db

RULE_COLUMNS = (
    "rule_id", "description", "parameter", "operator", "value",
    "scope_programmes", "scope_batches", "effective_from", "effective_to",
    "source_doc_id", "source_section",
)


def load_rule_rows(rows: Iterable[dict[str, Any]], conn) -> int:
    """Upsert rules after confirming every source document exists.

    All input and source-reference checks happen before the first write, so an
    orphan source reference cannot leave a partially loaded registry.
    """
    normalized = []
    for line, row in enumerate(rows, 2):
        missing_columns = [column for column in RULE_COLUMNS if column not in row]
        if missing_columns:
            raise ValueError(f"Rule CSV row {line}: missing columns: {', '.join(missing_columns)}")
        current = {column: str(row.get(column, "") or "").strip() for column in RULE_COLUMNS}
        if not current["rule_id"]:
            raise ValueError(f"Rule CSV row {line}: rule_id is required")
        doc_id = current["source_doc_id"]
        exists = conn.execute("SELECT 1 FROM source_register WHERE doc_id = ?", (doc_id,)).fetchone()
        if not exists:
            raise ValueError(f"Cannot load rule {current['rule_id']!r}: source_doc_id {doc_id!r} is missing from source_register")
        normalized.append(current)

    placeholders = ",".join("?" for _ in RULE_COLUMNS)
    updates = ",".join(f"{column}=excluded.{column}" for column in RULE_COLUMNS if column != "rule_id")
    sql = f"INSERT INTO rule_registry ({','.join(RULE_COLUMNS)}) VALUES ({placeholders}) ON CONFLICT(rule_id) DO UPDATE SET {updates}"
    values = [tuple(row[column] for column in RULE_COLUMNS) for row in normalized]
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
            count = load_rule_rows(rows, conn)
    except (OSError, csv.Error, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Loaded {count} rule registry row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
