"""Export the project seed through the declared SQLite schema, then validate it."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_conn, init_db
from scripts.validate_students import FILES, validate_dir

ROOT = Path(__file__).resolve().parents[2]
EXPORT_COLUMNS = {
    "students": ("student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"),
    "courses": ("course_code", "course_name", "programme", "semester", "credits"),
    "attendance": ("student_id", "course_code", "classes_held", "classes_attended"),
    "results": ("student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"),
}
RULE_COLUMNS = ("rule_id", "description", "parameter", "operator", "value", "scope_programmes", "scope_batches", "effective_from", "effective_to", "source_doc_id", "source_section")


def seed_to_csv(seed_path: str | Path | None = None, output_dir: str | Path | None = None, rules_csv: str | Path | None = None):
    """Create CSVs from seed SQL in a fresh in-memory DB and return validation errors."""
    seed = Path(seed_path) if seed_path is not None else ROOT / "data" / "seed.sql"
    out = Path(output_dir) if output_dir is not None else ROOT / "data" / "students_csv"
    rules = Path(rules_csv) if rules_csv is not None else ROOT / "data" / "rule_registry.csv"
    conn = get_conn(":memory:")
    try:
        init_db(conn)
        conn.executescript(seed.read_text(encoding="utf-8"))
        if rules.exists():
            with rules.open(newline="", encoding="utf-8-sig") as f:
                rows = csv.DictReader(f)
                sql = f"INSERT OR REPLACE INTO rule_registry ({','.join(RULE_COLUMNS)}) VALUES ({','.join('?' for _ in RULE_COLUMNS)})"
                conn.executemany(sql, [tuple(row.get(col) for col in RULE_COLUMNS) for row in rows])
        out.mkdir(parents=True, exist_ok=True)
        for table, columns in EXPORT_COLUMNS.items():
            records = conn.execute(f"SELECT {','.join(columns)} FROM {table}").fetchall()
            with (out / FILES[table]).open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(records)
    finally:
        conn.close()
    errors, warnings = validate_dir(out, rules_csv=rules if rules.exists() else None, print_report=True)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--rules", default=None)
    args = parser.parse_args()
    errors, _ = seed_to_csv(args.seed, args.out, args.rules)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
