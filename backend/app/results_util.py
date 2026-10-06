"""Shared ordering and backlog helpers for course result attempts."""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

_MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}
_SESSION_RE = re.compile(r"^(\d{4})-([A-Z]{3})$", re.IGNORECASE)


def parse_exam_session(session: str) -> tuple[int, int]:
    """Parse a YYYY-MON exam session into a sortable (year, month) tuple."""
    match = _SESSION_RE.fullmatch(str(session).strip())
    if not match:
        raise ValueError(f"Invalid exam_session {session!r}; expected YYYY-MON (for example, 2026-MAY)")
    year, month_name = match.groups()
    month = _MONTHS.get(month_name.upper())
    if month is None:
        raise ValueError(f"Invalid exam_session {session!r}; month must be JAN through DEC in YYYY-MON format")
    return int(year), month


def _value(row: Any, name: str) -> Any:
    if isinstance(row, Mapping):
        return row[name]
    try:
        return row[name]
    except (TypeError, IndexError, KeyError):
        return getattr(row, name)


def latest_attempts(rows: Iterable[Any]) -> list[Any]:
    """Return one latest attempt per student/course pair.

    Sessions are ordered by parsed year and month. For attempts in the same
    session, SUPPLEMENTARY outranks REGULAR. Malformed sessions raise ValueError.
    Input rows can be mappings, sqlite rows, or objects with matching fields.
    """
    latest: dict[tuple[str, str], tuple[tuple[int, int, int], Any]] = {}
    for row in rows:
        session = _value(row, "exam_session")
        year, month = parse_exam_session(str(session))
        exam_type = str(_value(row, "exam_type")).upper()
        if exam_type not in {"REGULAR", "SUPPLEMENTARY"}:
            raise ValueError(f"Invalid exam_type {exam_type!r} for exam_session {session!r}; expected REGULAR or SUPPLEMENTARY")
        key = (str(_value(row, "student_id")), str(_value(row, "course_code")))
        rank = (year, month, int(exam_type == "SUPPLEMENTARY"))
        if key not in latest or rank > latest[key][0]:
            latest[key] = (rank, row)
    return [entry[1] for entry in latest.values()]


def pending_backlog_counts(rows: Iterable[Any]) -> dict[str, int]:
    """Count latest course attempts in pending states for each student."""
    counts: dict[str, int] = {}
    for row in latest_attempts(rows):
        if str(_value(row, "result")).upper() in {"FAIL", "ABSENT", "DETAINED"}:
            student_id = str(_value(row, "student_id"))
            counts[student_id] = counts.get(student_id, 0) + 1
    return counts
