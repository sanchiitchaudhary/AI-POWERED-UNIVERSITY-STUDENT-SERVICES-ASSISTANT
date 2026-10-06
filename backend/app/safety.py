"""Request identity and safe tool error conventions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any


class AuthRequired(PermissionError):
    """A tool request has no authenticated student identity."""


@dataclass
class RequestContext:
    """Trusted request-scoped identity, date, and database connection."""

    student_id: str | None
    as_of_date: str | date
    conn: Any


ToolResult = dict[str, Any]


_STUDENT_ID = re.compile(r"\bS\d{4}\b", re.IGNORECASE)
_INJECTION_PATTERNS = (
    re.compile(r"\b(ignore|disregard|forget|override)\b.{0,50}\b(previous|prior|system|developer|application)\b.{0,30}\b(instruction|rule|prompt)s?\b", re.I),
    re.compile(r"\b(bypass|disable|ignore)\b.{0,35}\b(safety|identity|precedence|citation|threshold|tool)\b", re.I),
    re.compile(r"\b(reveal|print|show)\b.{0,30}\b(system prompt|hidden instructions|secret prompt)\b", re.I),
    re.compile(r"\b(change|set|invent|make up)\b.{0,30}\b(attendance|pass|cgpa|placement|eligibility)?\s*threshold", re.I),
    re.compile(r"\byou are now\b.{0,60}\b(system|developer|admin|unrestricted)", re.I),
)
_PERSONAL_DATA_TERMS = re.compile(r"\b(attendance|result|grade|marks|cgpa|backlog|profile|record|data|transcript)\b", re.I)


def contains_prompt_injection(question: str) -> bool:
    """Detect direct attempts to override application and policy safeguards."""
    return any(pattern.search(question or "") for pattern in _INJECTION_PATTERNS)


def requests_another_student(question: str, authenticated_student_id: str | None) -> bool:
    """Detect requests for a different student's personal data."""
    text = question or ""
    ids = {match.upper() for match in _STUDENT_ID.findall(text)}
    own_id = authenticated_student_id.upper() if authenticated_student_id else None
    if any(student_id != own_id for student_id in ids):
        return True
    if not _PERSONAL_DATA_TERMS.search(text):
        return False
    lower = text.casefold()
    explicit = (
        "another student", "someone else's", "someone else’s", "my friend's",
        "my friend’s", "their attendance", "their grades", "their results",
        "other student's", "other student’s", "all students'", "all students’",
    )
    return any(phrase in lower for phrase in explicit)


def requires_student_identity(question: str, category: str | None = None) -> bool:
    """Return whether this request needs a student-scoped tool context."""
    category = (category or "").casefold()
    if category in {"personal_data", "personal_eligibility", "multi_step"}:
        return True
    lower = (question or "").casefold()
    self_reference = re.search(r"\b(my|me|mine|am i|do i|can i|will i)\b", lower)
    personal_intent = _PERSONAL_DATA_TERMS.search(lower) or re.search(r"\b(eligible|eligibility|placement|supplementary)\b", lower)
    return bool(self_reference and personal_intent)
