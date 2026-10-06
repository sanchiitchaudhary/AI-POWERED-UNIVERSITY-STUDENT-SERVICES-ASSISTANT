"""Shared safe result formatting for deterministic tools."""
from __future__ import annotations

from time import perf_counter
from typing import Any, Callable

from app.rules import RuleConflict, RuleNotFound
from app.safety import AuthRequired, RequestContext


def require_identity(ctx: RequestContext) -> str:
    student_id = getattr(ctx, "student_id", None)
    if not student_id:
        raise AuthRequired("Authenticated student identity is required.")
    return str(student_id)


def citations(rules) -> list[dict[str, Any]]:
    output = []
    seen = set()
    for rule in rules:
        if rule is None or rule.source_doc_id in seen:
            continue
        seen.add(rule.source_doc_id)
        source = rule.source_document
        output.append({
            "doc_id": rule.source_doc_id,
            "title": source.get("title"),
            "section": rule.source_section,
            "version": source.get("version"),
            "effective_from": rule.effective_from or source.get("effective_from"),
        })
    return output


def run_tool(name: str, inputs: dict[str, Any], action: Callable[[], tuple[Any, list[Any]]]):
    started = perf_counter()
    try:
        output, used_rules = action()
        status = "ok"
        rule_ids = list(dict.fromkeys(rule.rule_id for rule in used_rules if rule is not None))
        citation_meta = citations(used_rules)
    except AuthRequired:
        raise
    except RuleConflict as exc:
        output, status, rule_ids, citation_meta = {"message": "Applicable university rules conflict; contact the issuing office.", "conflict": exc.decision.conflict_keys}, "error", [], []
    except RuleNotFound as exc:
        output, status, rule_ids, citation_meta = {"message": str(exc)}, "error", [], []
    except (ValueError, LookupError) as exc:
        output, status, rule_ids, citation_meta = {"message": str(exc)}, "error", [], []
    except Exception:
        output, status, rule_ids, citation_meta = {"message": "The requested university record could not be retrieved."}, "error", [], []
    return {
        "tool": name,
        "input": inputs,
        "output": output,
        "status": status,
        "ms": round((perf_counter() - started) * 1000, 3),
        "rule_ids": rule_ids,
        "citations_meta": citation_meta,
    }


def student_row(ctx: RequestContext):
    student_id = require_identity(ctx)
    row = ctx.conn.execute(
        "SELECT programme, batch_year, current_semester, cgpa, active_backlogs FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()
    if row is None:
        raise LookupError("Student profile not found for the authenticated identity.")
    return dict(row)


def course_attendance(ctx: RequestContext, course_code: str):
    student_id = require_identity(ctx)
    row = ctx.conn.execute(
        "SELECT course_code, classes_held, classes_attended FROM attendance WHERE student_id = ? AND course_code = ?",
        (student_id, course_code),
    ).fetchone()
    if row is None:
        raise LookupError("Attendance record not found for the requested course.")
    result = dict(row)
    result["attendance_pct"] = round(result["classes_attended"] * 100 / result["classes_held"], 2)
    return result


def latest_course_attempt(ctx: RequestContext, course_code: str):
    from app.results_util import latest_attempts

    student_id = require_identity(ctx)
    rows = ctx.conn.execute(
        "SELECT student_id, course_code, exam_session, exam_type, result FROM results WHERE student_id = ? AND course_code = ?",
        (student_id, course_code),
    ).fetchall()
    attempts = latest_attempts(rows)
    return attempts[0] if attempts else None
