"""Validate and load Annex C student CSV files into SQLite."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_conn, init_db
from app.results_util import pending_backlog_counts
from scripts.validate_students import FILES, validate_dir

TABLE_COLUMNS = {
    "students": ("student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"),
    "courses": ("course_code", "course_name", "programme", "semester", "credits"),
    "attendance": ("student_id", "course_code", "classes_held", "classes_attended"),
    "results": ("student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"),
}


def _rows(path: Path, table: str):
    columns = TABLE_COLUMNS[table]
    with path.open(newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            # Unknown columns are deliberately ignored for judges' CSVs.
            yield tuple(raw.get(c) for c in columns)


def pending_backlogs(directory: str | Path) -> dict[str, int]:
    """Return latest-attempt pending-course counts from a validated CSV set."""
    path = Path(directory) / FILES["results"]
    with path.open(newline="", encoding="utf-8-sig") as f:
        return pending_backlog_counts(csv.DictReader(f))


def load_students(directory: str | Path, db_path: str | Path) -> dict[str, int]:
    root = Path(directory)
    errors, _ = validate_dir(root, db_path, print_report=False)
    if errors:
        raise ValueError(f"CSV validation failed with {len(errors)} error(s); database was not modified")
    init_db(db_path)
    counts: dict[str, int] = {}
    with get_conn(db_path) as conn:
        # Clear dependents before REPLACE to avoid FK cascade failures on reload.
        conn.execute("DELETE FROM attendance")
        conn.execute("DELETE FROM results")
        for table in ("students", "courses", "attendance", "results"):
            columns = TABLE_COLUMNS[table]
            sql = f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})"
            rows = list(_rows(root / FILES[table], table))
            conn.executemany(sql, rows)
            counts[table] = len(rows)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--db", default=None)
    args = parser.parse_args()
    db_path = args.db or str(Path(__file__).resolve().parents[1] / "university.db")
    try:
        counts = load_students(args.dir, db_path)
    except (ValueError, OSError) as e:
        print(e, file=sys.stderr)
        return 1
    pending = pending_backlogs(args.dir)
    print("Loaded: " + ", ".join(f"{table}={count}" for table, count in counts.items()))
    print(f"Latest pending backlog courses={sum(pending.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
