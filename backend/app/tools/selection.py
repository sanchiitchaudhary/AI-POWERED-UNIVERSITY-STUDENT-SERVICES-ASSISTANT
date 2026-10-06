"""Small deterministic fallback from user intent to a registered tool plan."""
from __future__ import annotations

import re


_COURSE = re.compile(r"\b([A-Z]{2,}[A-Z0-9]*\d{2,}[A-Z0-9]*)\b", re.IGNORECASE)


def select_tool(question: str) -> dict:
    """Select a tool and course code without ever extracting student identity."""
    text = question.casefold()
    match = _COURSE.search(question)
    course_code = match.group(1).upper() if match else None
    if any(word in text for word in ("if i clear", "what if", "supplementary")) and any(word in text for word in ("placement", "eligible", "clear")) and "supplementary" in text:
        return {"tool": "whatif_supplementary_placement", "input": {"course_code": course_code}} if course_code else {"tool": "whatif_supplementary_placement", "input": {}}
    if "supplementary" in text:
        return {"tool": "check_supplementary_eligibility", "input": {"course_code": course_code}} if course_code else {"tool": "check_supplementary_eligibility", "input": {}}
    if "placement" in text:
        return {"tool": "check_placement_eligibility", "input": {}}
    if "eligible" in text or "eligibility" in text:
        return {"tool": "check_exam_eligibility", "input": {"course_code": course_code}} if course_code else {"tool": "check_exam_eligibility", "input": {}}
    if "attendance" in text:
        return {"tool": "get_attendance", "input": {"course_code": course_code}} if course_code else {"tool": "get_attendance_all", "input": {}}
    if "result" in text or "marks" in text:
        return {"tool": "get_results", "input": {"course_code": course_code} if course_code else {}}
    if "backlog" in text:
        return {"tool": "get_backlogs", "input": {}}
    return {"tool": "get_profile", "input": {}}
