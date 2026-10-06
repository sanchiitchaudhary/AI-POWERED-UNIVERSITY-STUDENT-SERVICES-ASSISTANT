"""Backlog lookup based on the shared latest-attempt ordering."""
from __future__ import annotations

import sqlite3

from app.results_util import pending_backlog_counts


def get_backlogs(conn: sqlite3.Connection, student_id: str) -> int:
    """Return pending backlog courses for one already-authorized student ID."""
    rows = conn.execute(
        "SELECT student_id, course_code, exam_session, exam_type, result "
        "FROM results WHERE student_id = ?",
        (student_id,),
    )
    return pending_backlog_counts(rows).get(student_id, 0)
