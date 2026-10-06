import csv

import pytest

from app.db import get_conn
from scripts.load_students import load_students
from scripts.seed_to_csv import ROOT, seed_to_csv
from scripts.validate_students import validate_dir


def write_csv(folder, name, headers, rows):
    with (folder / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


@pytest.fixture
def csv_dir(tmp_path):
    write_csv(tmp_path, "students.csv", ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"], [["S1001", "Student One", "BTech IT", 2023, 3, 8.1, 0]])
    write_csv(tmp_path, "courses.csv", ["course_code", "course_name", "programme", "semester", "credits"], [["IT101", "Foundations", "BTech IT", 1, 4]])
    write_csv(tmp_path, "attendance.csv", ["student_id", "course_code", "classes_held", "classes_attended"], [["S1001", "IT101", 10, 8]])
    write_csv(tmp_path, "results.csv", ["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"], [["S1001", "IT101", "2025-MAY", "REGULAR", 20, 30, 50, 100, "PASS"]])
    return tmp_path


def test_valid_load_and_idempotent_reload(csv_dir, tmp_path):
    db = tmp_path / "students.sqlite"
    assert load_students(csv_dir, db) == {"students": 1, "courses": 1, "attendance": 1, "results": 1}
    load_students(csv_dir, db)
    with get_conn(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM results").fetchone()[0] == 1


def test_bad_id_rejected(csv_dir, tmp_path):
    write_csv(csv_dir, "students.csv", ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"], [["2023UIT2684", "Student One", "BTech IT", 2023, 3, 8.1, 0]])
    errors, _ = validate_dir(csv_dir, print_report=False)
    assert any(rule == "student_id_format" for _, _, rule, _ in errors)
    with pytest.raises(ValueError):
        load_students(csv_dir, tmp_path / "bad.sqlite")


def test_attended_over_held_rejected(csv_dir):
    write_csv(csv_dir, "attendance.csv", ["student_id", "course_code", "classes_held", "classes_attended"], [["S1001", "IT101", 2, 3]])
    errors, _ = validate_dir(csv_dir, print_report=False)
    assert any(rule == "attended_within_held" for _, _, rule, _ in errors)


def test_total_mismatch_rejected(csv_dir):
    write_csv(csv_dir, "results.csv", ["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"], [["S1001", "IT101", "2025-MAY", "REGULAR", 20, 30, 52, 100, "PASS"]])
    errors, _ = validate_dir(csv_dir, print_report=False)
    assert any(rule == "total_matches_components" for _, _, rule, _ in errors)


def test_unparseable_exam_session_rejected(csv_dir):
    write_csv(csv_dir, "results.csv", ["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"], [["S1001", "IT101", "2025-REG", "REGULAR", 20, 30, 50, 100, "PASS"]])
    errors, _ = validate_dir(csv_dir, print_report=False)
    assert any(rule == "exam_session_format" and "YYYY-MON" in message for _, _, rule, message in errors)


def validate_programme_marks(tmp_path, programme, total, external, result):
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    write_csv(csv_dir, "students.csv", ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"], [["S1001", "Student One", programme, 2024, 1, 7.0, 0]])
    write_csv(csv_dir, "courses.csv", ["course_code", "course_name", "programme", "semester", "credits"], [["CS101", "Course", programme, 1, 4]])
    write_csv(csv_dir, "attendance.csv", ["student_id", "course_code", "classes_held", "classes_attended"], [])
    write_csv(csv_dir, "results.csv", ["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"], [["S1001", "CS101", "2026-MAY", "REGULAR", total - external, external, total, 100, result]])
    rules_path = tmp_path / "rule_registry.csv"
    write_csv(tmp_path, "rule_registry.csv", ["rule_id", "description", "parameter", "operator", "value", "scope_programmes", "scope_batches", "effective_from", "effective_to", "source_doc_id", "source_section"], [
        ["BTECH-PASS", "B.Tech pass total", "total_marks", ">=", 40, "B.Tech", "ALL", "2025-01-01", "", "DOC-TEST", "1"],
        ["BTECH-EXT", "B.Tech external minimum", "external_marks", ">=", 24, "B.Tech", "ALL", "2025-01-01", "", "DOC-TEST", "2"],
        ["MTECH-PASS", "M.Tech pass total", "total_marks", ">=", 50, "M.Tech", "ALL", "2025-01-01", "", "DOC-TEST", "3"],
        ["MTECH-EXT", "M.Tech external minimum", "external_marks", ">=", 30, "M.Tech", "ALL", "2025-01-01", "", "DOC-TEST", "4"],
    ])
    return validate_dir(csv_dir, rules_csv=rules_path, print_report=False)[0]


@pytest.mark.parametrize(
    "programme,total,external,result,expected_error",
    [
        ("B.Tech CSE", 40, 24, "PASS", False),
        ("B.Tech CSE", 40, 23, "PASS", True),
        ("B.Tech CSE", 39, 24, "PASS", True),
        ("M.Tech AI", 50, 30, "PASS", False),
        ("M.Tech AI", 49, 30, "PASS", True),
        ("M.Tech AI", 50, 29, "PASS", True),
        ("B.Tech CSE", 45, 26, "FAIL", True),
    ],
)
def test_result_thresholds_use_programme_scoped_registry(tmp_path, programme, total, external, result, expected_error):
    errors = validate_programme_marks(tmp_path, programme, total, external, result)
    mark_errors = [error for error in errors if error[2] == "result_matches_marks"]
    assert bool(mark_errors) is expected_error


def test_real_seed_exports_and_validates_without_errors(tmp_path):
    seed = ROOT / "data" / "seed.sql"
    rules = ROOT / "data" / "rule_registry.csv"
    assert seed.is_file()
    errors, warnings = seed_to_csv(seed, tmp_path / "students_csv", rules)
    assert errors == []
    assert warnings == []
