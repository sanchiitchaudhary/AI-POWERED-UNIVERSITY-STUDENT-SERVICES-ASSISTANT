"""Validate Annex C CSV files without writing to a persistent database."""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any, Iterator

from pydantic import BaseModel, ConfigDict, Field, ValidationError

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_conn, init_db
from app.results_util import latest_attempts, parse_exam_session
from app.rules import RuleConflict, RuleNotFound, compare_values, load_rules, resolve_parameter
from scripts.load_rules import load_rule_rows
from scripts.load_sources import load_source_rows


class Student(BaseModel):
    model_config = ConfigDict(extra="ignore")
    student_id: str
    full_name: str
    programme: str
    batch_year: int
    current_semester: int = Field(ge=1, le=10)
    cgpa: float = Field(ge=0, le=10)
    active_backlogs: int = Field(ge=0)


class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    course_code: str
    course_name: str
    programme: str
    semester: int
    credits: int


class Attendance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    student_id: str
    course_code: str
    classes_held: int
    classes_attended: int


class Result(BaseModel):
    model_config = ConfigDict(extra="ignore")
    student_id: str
    course_code: str
    exam_session: str
    exam_type: str
    internal_marks: float
    external_marks: float
    total_marks: float
    max_marks: float
    result: str


FILES = {"students": "students.csv", "courses": "courses.csv", "attendance": "attendance.csv", "results": "results.csv"}
MODELS = {"students": Student, "courses": Course, "attendance": Attendance, "results": Result}


def _load(path: Path, kind: str, violations: list[tuple[str, int, str, str]]) -> list[tuple[int, Any]]:
    if not path.exists():
        violations.append((FILES[kind], 0, "file_required", "Required CSV file is missing"))
        return []
    parsed = []
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for rownum, raw in enumerate(reader, 2):
                try:
                    parsed.append((rownum, MODELS[kind].model_validate(raw)))
                except ValidationError as e:
                    for error in e.errors():
                        field = ".".join(str(x) for x in error["loc"])
                        violations.append((FILES[kind], rownum, f"field:{field}", error["msg"]))
    except (OSError, csv.Error) as e:
        violations.append((FILES[kind], 0, "csv_readable", str(e)))
    return parsed


def _thresholds(rules: list[Any]) -> list[tuple[str, float]]:
    out = []
    for rule in rules:
        name = str(rule.parameter or "").lower()
        if any(s in name for s in ("attendance", "cgpa", "pass", "external", "total")):
            try:
                out.append((name, float(rule.value)))
            except (TypeError, ValueError):
                pass
    return out


@contextmanager
def _registry_connection(db_path: str | Path | None, rules_csv: str | Path | None) -> Iterator[sqlite3.Connection]:
    """Open an existing registry read-only in practice, or stage CSVs in memory."""
    if db_path and Path(db_path).exists():
        conn = get_conn(db_path)
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if {"rule_registry", "source_register"}.issubset(tables):
            try:
                yield conn
            finally:
                conn.close()
            return
        conn.close()

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    root = Path(__file__).resolve().parents[2] / "data"
    source_path = root / "source_register.csv"
    rule_path = Path(rules_csv) if rules_csv else root / "rule_registry.csv"
    try:
        if source_path.exists():
            with source_path.open(newline="", encoding="utf-8-sig") as f:
                load_source_rows(list(csv.DictReader(f)), conn)
        if rule_path.exists():
            with rule_path.open(newline="", encoding="utf-8-sig") as f:
                load_rule_rows(list(csv.DictReader(f)), conn)
        yield conn
    finally:
        conn.close()


def validate_dir(directory: str | Path, db_path: str | Path | None = None, *, rules_csv: str | Path | None = None, as_of_date: str | None = None, print_report: bool = True) -> tuple[list[tuple[str, int, str, str]], list[tuple[str, int, str, str]]]:
    """Return (errors, warnings); no database writes are performed."""
    root = Path(directory)
    violations: list[tuple[str, int, str, str]] = []
    students = _load(root / FILES["students"], "students", violations)
    courses = _load(root / FILES["courses"], "courses", violations)
    attendance = _load(root / FILES["attendance"], "attendance", violations)
    results = _load(root / FILES["results"], "results", violations)
    errors: list[tuple[str, int, str, str]] = []
    warnings: list[tuple[str, int, str, str]] = []
    for file, row, rule, msg in violations:
        errors.append((file, row, rule, msg))

    def duplicates(items, key_fn, file: str, rule: str) -> None:
        seen: set[Any] = set()
        for rownum, item in items:
            key = key_fn(item)
            if key in seen:
                errors.append((file, rownum, rule, f"Duplicate key: {key}"))
            seen.add(key)

    duplicates(students, lambda s: s.student_id, FILES["students"], "student_id_unique")
    duplicates(courses, lambda c: c.course_code, FILES["courses"], "course_code_unique")
    duplicates(attendance, lambda a: (a.student_id, a.course_code), FILES["attendance"], "attendance_key_unique")
    duplicates(results, lambda r: (r.student_id, r.course_code, r.exam_session, r.exam_type), FILES["results"], "result_key_unique")

    student_rows = {r.student_id: (n, r) for n, r in students}
    course_rows = {r.course_code: (n, r) for n, r in courses}
    for n, s in students:
        if not re.fullmatch(r"S\d{4}", s.student_id):
            errors.append((FILES["students"], n, "student_id_format", "ID must match S followed by four digits"))
        elif s.student_id[1:] >= "9000":
            errors.append((FILES["students"], n, "reserved_student_id", "S9000-S9999 are reserved"))
    for n, c in courses:
        if c.course_code.startswith("JDG"):
            errors.append((FILES["courses"], n, "reserved_course_code", "JDG course codes are reserved"))

    def fk(file: str, n: int, ident: str, known: dict, what: str) -> bool:
        if ident not in known:
            errors.append((file, n, f"{what}_exists", f"Unknown {what}: {ident}"))
            return False
        return True

    for n, a in attendance:
        s_ok = fk(FILES["attendance"], n, a.student_id, student_rows, "student")
        c_ok = fk(FILES["attendance"], n, a.course_code, course_rows, "course")
        if a.classes_held <= 0:
            errors.append((FILES["attendance"], n, "held_positive", "classes_held must be greater than zero"))
        if a.classes_attended < 0 or a.classes_attended > a.classes_held:
            errors.append((FILES["attendance"], n, "attended_within_held", "classes_attended must be between zero and classes_held"))
        if s_ok and c_ok and student_rows[a.student_id][1].programme != course_rows[a.course_code][1].programme:
            errors.append((FILES["attendance"], n, "programme_match", "Course programme differs from student's programme"))

    evaluation_date = as_of_date or date.today().isoformat()
    parsed_result_rows: list[tuple[int, Result]] = []
    failed_just_below_pass = False
    try:
        with _registry_connection(db_path, rules_csv) as rule_conn:
            registry_rules = load_rules(rule_conn)
            thresholds = _thresholds(registry_rules)
            for n, r in results:
                s_ok = fk(FILES["results"], n, r.student_id, student_rows, "student")
                c_ok = fk(FILES["results"], n, r.course_code, course_rows, "course")
                if s_ok and c_ok and student_rows[r.student_id][1].programme != course_rows[r.course_code][1].programme:
                    errors.append((FILES["results"], n, "programme_match", "Course programme differs from student's programme"))
                if r.exam_type not in {"REGULAR", "SUPPLEMENTARY"}:
                    errors.append((FILES["results"], n, "exam_type_enum", "exam_type must be REGULAR or SUPPLEMENTARY"))
                try:
                    parse_exam_session(r.exam_session)
                except ValueError as e:
                    errors.append((FILES["results"], n, "exam_session_format", str(e)))
                if r.result not in {"PASS", "FAIL", "ABSENT", "DETAINED"}:
                    errors.append((FILES["results"], n, "result_enum", "Invalid result value"))
                marks_ok = 0 <= r.internal_marks <= r.max_marks and 0 <= r.external_marks <= r.max_marks and r.max_marks > 0
                if not marks_ok or r.internal_marks + r.external_marks > r.max_marks:
                    errors.append((FILES["results"], n, "marks_in_range", "Marks must be nonnegative and their sum cannot exceed max_marks"))
                if abs(r.total_marks - r.internal_marks - r.external_marks) > 1e-9:
                    errors.append((FILES["results"], n, "total_matches_components", "total_marks must equal internal_marks + external_marks"))
                if r.result == "ABSENT" and (r.internal_marks != 0 or r.external_marks != 0 or r.total_marks != 0):
                    errors.append((FILES["results"], n, "absent_zero_marks", "ABSENT rows must have zero marks"))
                if r.result in {"PASS", "FAIL"} and s_ok:
                    student = student_rows[r.student_id][1]
                    try:
                        total_rule, _, _ = resolve_parameter("total_marks", student.programme, student.batch_year, evaluation_date, conn=rule_conn)
                        external_rule, _, _ = resolve_parameter("external_marks", student.programme, student.batch_year, evaluation_date, conn=rule_conn)
                    except RuleNotFound:
                        pass
                    except RuleConflict as exc:
                        errors.append((FILES["results"], n, "result_threshold_conflict", str(exc)))
                    else:
                        should_pass = compare_values(r.total_marks, total_rule.operator, total_rule.value) and compare_values(r.external_marks, external_rule.operator, external_rule.value)
                        if should_pass != (r.result == "PASS"):
                            errors.append((FILES["results"], n, "result_matches_marks", f"Result conflicts with registry rules {total_rule.rule_id}/{external_rule.rule_id} for programme {student.programme}"))
                        if r.result == "FAIL" and (r.total_marks == float(total_rule.value) - 1 or r.external_marks == float(external_rule.value) - 1):
                            failed_just_below_pass = True
                parsed_result_rows.append((n, r))
    except (OSError, csv.Error, sqlite3.Error, ValueError) as e:
        errors.append(("rule_registry.csv", 0, "registry_load", str(e)))
        thresholds = []

    fail_counts: dict[str, int] = {}
    if not any(rule in {"exam_session_format", "exam_type_enum"} for _, _, rule, _ in errors):
        try:
            for latest in latest_attempts(r for _, r in parsed_result_rows):
                if latest.result in {"FAIL", "ABSENT", "DETAINED"}:
                    fail_counts[latest.student_id] = fail_counts.get(latest.student_id, 0) + 1
        except ValueError as e:
            # Defensive: validation above reports row-specific parsing failures.
            errors.append((FILES["results"], 0, "exam_session_format", str(e)))
    for n, s in students:
        actual = fail_counts.get(s.student_id, 0)
        if actual != s.active_backlogs:
            warnings.append((FILES["students"], n, "backlog_count", f"active_backlogs={s.active_backlogs}; latest pending courses={actual}"))

    if print_report:
        print("Coverage report:")
        programmes = {s.programme for _, s in students}
        batches = {s.batch_year for _, s in students}
        checks = [("students >= 30", len(students) >= 30), ("programmes >= 2", len(programmes) >= 2), ("batches >= 2", len(batches) >= 2), ("courses >= 6", len(courses) >= 6)]
        for label, ok in checks:
            print(f"  {'PASS' if ok else 'MISSING'} {label}")
        print("  Edge cases:")
        edge = {"attendance exactly at a threshold": False, "attendance one class below a threshold": False, "attendance exactly 65.0%": False,
                "failed with marks just below pass": False, "ABSENT": any(r.result == "ABSENT" for _, r in results),
                "DETAINED": any(r.result == "DETAINED" for _, r in results), "backlogs >= 2": any(s.active_backlogs >= 2 for _, s in students),
                "cgpa exactly at a cutoff": False}
        att_thresholds = [v for name, v in thresholds if "attendance" in name]
        cgpa_thresholds = [v for name, v in thresholds if "cgpa" in name]
        mark_thresholds_available = any("pass" in name or "total" in name for name, _ in thresholds) and any("external" in name for name, _ in thresholds)
        if not att_thresholds or not cgpa_thresholds or not mark_thresholds_available:
            missing = []
            if not att_thresholds: missing.append("attendance")
            if not cgpa_thresholds: missing.append("CGPA")
            if not mark_thresholds_available: missing.append("pass marks")
            print(f"  Note: {', '.join(missing)} edge thresholds require rule_registry entries; unavailable checks were skipped.")
        for _, a in attendance:
            if a.classes_held > 0:
                edge["attendance exactly 65.0%"] |= a.classes_attended * 100 == a.classes_held * 65
                for t in att_thresholds:
                    edge["attendance exactly at a threshold"] |= a.classes_attended * 100 == a.classes_held * t
                    edge["attendance one class below a threshold"] |= (a.classes_attended + 1) * 100 >= a.classes_held * t and a.classes_attended * 100 < a.classes_held * t
        for _, s in students:
            edge["cgpa exactly at a cutoff"] |= s.cgpa in cgpa_thresholds
        edge["failed with marks just below pass"] = failed_just_below_pass
        for label, present in edge.items():
            print(f"    {'YES' if present else 'NO'} {label}")
        for file, row, rule, msg in errors:
            print(f"ERROR ({file}, {row}, {rule}, {msg})")
        for file, row, rule, msg in warnings:
            print(f"WARNING ({file}, {row}, {rule}, {msg})")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--db", help="Optional SQLite database path for rule_registry thresholds")
    parser.add_argument("--rules-csv", help="Optional rule_registry CSV for threshold checks")
    parser.add_argument("--as-of-date", help="Rule evaluation date in YYYY-MM-DD form; defaults to today")
    args = parser.parse_args()
    errors, _ = validate_dir(args.dir, args.db, rules_csv=args.rules_csv, as_of_date=args.as_of_date)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
