from typing import Dict, Any, Optional
from backend.database import get_db_connection
from backend.rule_precedence import get_applicable_rules, eval_operator_condition

def get_student_profile(student_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_attendance(student_id: str, course_code: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.student_id, a.course_code, a.attendance_pct, c.title
        FROM attendance a
        LEFT JOIN courses c ON a.course_code = c.course_code
        WHERE a.student_id = ? AND a.course_code = ?
    ''', (student_id, course_code))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def simulate_result(
    student_id: str,
    course_code: str,
    assumed_result: str,
    as_of_date: str = "2026-10-06"
) -> Dict[str, Any]:
    """
    Deterministic tool simulation (R6 What-if).
    Runs rule evaluation over a copy of student data without mutating the database.
    """
    student = get_student_profile(student_id)
    if not student:
        return {
            "status": "error",
            "message": f"Student ID '{student_id}' not found in records."
        }

    # Fetch applicable passing threshold rule
    rule, has_conflict, _ = get_applicable_rules(
        parameter="min_pass_marks",
        as_of_date=as_of_date,
        programme=student['programme'],
        batch=student['batch']
    )

    pass_threshold = float(rule['value']) if rule else 40.0

    # Parse assumed result
    assumed_is_pass = False
    try:
        val = float(assumed_result)
        assumed_is_pass = val >= pass_threshold
    except ValueError:
        assumed_is_pass = assumed_result.upper() in ['PASS', 'A', 'B', 'C', 'P', 'EXCELLENT']

    simulated_gpa = student['gpa']
    if assumed_is_pass:
        simulated_gpa = round(min(student['gpa'] + 0.05, 4.0), 2)

    return {
        "status": "simulated",
        "student_id": student_id,
        "course_code": course_code,
        "assumed_result": assumed_result,
        "is_pass": assumed_is_pass,
        "pass_threshold_applied": f">={pass_threshold}",
        "rule_code_applied": rule['rule_code'] if rule else "DEFAULT-PASS-01",
        "current_gpa": student['gpa'],
        "simulated_gpa": simulated_gpa,
        "note": f"Simulation executed for course {course_code} under assumption '{assumed_result}'. Database state remains unmodified."
    }
