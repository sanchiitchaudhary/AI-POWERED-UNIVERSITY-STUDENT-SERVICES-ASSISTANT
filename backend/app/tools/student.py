"""Student-scoped profile, attendance, result, backlog, and course lookups."""
from __future__ import annotations

from app.safety import RequestContext
from app.results_util import latest_attempts
from app.tools.common import course_attendance, require_identity, run_tool, student_row


def get_profile(ctx: RequestContext):
    return run_tool("get_profile", {}, lambda: (student_row(ctx), []))


def get_attendance(ctx: RequestContext, course_code: str):
    return run_tool("get_attendance", {"course_code": course_code}, lambda: (course_attendance(ctx, course_code), []))


def get_attendance_all(ctx: RequestContext):
    def action():
        student_id = require_identity(ctx)
        rows = ctx.conn.execute(
            "SELECT a.course_code, a.classes_held, a.classes_attended FROM attendance a "
            "JOIN courses c ON c.course_code = a.course_code "
            "JOIN students s ON s.student_id = a.student_id "
            "WHERE a.student_id = ? AND c.programme = s.programme ORDER BY a.course_code",
            (student_id,),
        ).fetchall()
        records = []
        for row in rows:
            item = dict(row)
            item["attendance_pct"] = round(item["classes_attended"] * 100 / item["classes_held"], 2)
            records.append(item)
        return records, []
    return run_tool("get_attendance_all", {}, action)


def get_results(ctx: RequestContext, course_code: str | None = None):
    def action():
        student_id = require_identity(ctx)
        sql = ("SELECT r.course_code, c.course_name, r.exam_session, r.exam_type, "
               "r.internal_marks, r.external_marks, r.total_marks, r.max_marks, r.result "
               "FROM results r JOIN courses c ON c.course_code = r.course_code WHERE r.student_id = ?")
        params: list = [student_id]
        if course_code is not None:
            sql += " AND r.course_code = ?"
            params.append(course_code)
        rows = ctx.conn.execute(sql, params).fetchall()
        # Parse every session even though all attempts are retained, rejecting malformed dates.
        latest_attempts(ctx.conn.execute("SELECT student_id, course_code, exam_session, exam_type, result FROM results WHERE student_id = ?" + (" AND course_code = ?" if course_code is not None else ""), params).fetchall())
        return [dict(row) for row in rows], []
    inputs = {} if course_code is None else {"course_code": course_code}
    return run_tool("get_results", inputs, action)


def get_backlogs(ctx: RequestContext):
    def action():
        student_id = require_identity(ctx)
        rows = ctx.conn.execute(
            "SELECT r.student_id, r.course_code, r.exam_session, r.exam_type, r.result "
            "FROM results r WHERE r.student_id = ?", (student_id,),
        ).fetchall()
        latest = latest_attempts(rows)
        result = []
        for attempt in latest:
            if str(attempt["result"]).upper() not in {"FAIL", "ABSENT"}:
                continue
            name = ctx.conn.execute("SELECT course_name FROM courses WHERE course_code = ?", (attempt["course_code"],)).fetchone()
            result.append({
                "course_code": attempt["course_code"], "course_name": name[0] if name else None,
                "latest_exam_session": attempt["exam_session"], "latest_exam_type": attempt["exam_type"],
                "result": attempt["result"],
            })
        result.sort(key=lambda item: item["course_code"])
        return result, []
    return run_tool("get_backlogs", {}, action)


def list_courses(ctx: RequestContext, semester: int | None = None):
    def action():
        profile = student_row(ctx)
        sql = "SELECT course_code, course_name, programme, semester, credits FROM courses WHERE programme = ?"
        params: list = [profile["programme"]]
        if semester is not None:
            sql += " AND semester = ?"
            params.append(semester)
        sql += " ORDER BY semester, course_code"
        rows = ctx.conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows], []
    inputs = {} if semester is None else {"semester": semester}
    return run_tool("list_courses", inputs, action)
