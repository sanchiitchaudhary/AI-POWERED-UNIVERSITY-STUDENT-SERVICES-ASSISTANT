"""Registry-backed attendance, supplementary, and placement decisions."""
from __future__ import annotations

from app import rules
from app.safety import RequestContext
from app.tools.common import course_attendance, latest_course_attempt, require_identity, run_tool, student_row


def _rule_brief(rule):
    return {"rule_id": rule.rule_id, "value": rule.value, "source_doc_id": rule.source_doc_id, "source_section": rule.source_section}


def _upcoming(rows):
    return [_rule_brief(rule) for rule in rows]


def check_exam_eligibility(ctx: RequestContext, course_code: str):
    def action():
        profile = student_row(ctx)
        attendance = course_attendance(ctx, course_code)
        band = rules.get_attendance_band(
            profile["programme"], profile["batch_year"], profile["active_backlogs"],
            attendance["classes_held"], attendance["classes_attended"], ctx.as_of_date, conn=ctx.conn,
        )
        mapped = {"ELIGIBLE": "ELIGIBLE", "CONDONATION": "CONDONATION_REQUIRED", "DETENTION": "NOT_ELIGIBLE"}[band.band]
        output = {
            "course_code": course_code, "classes_held": attendance["classes_held"],
            "classes_attended": attendance["classes_attended"], "attendance_pct": float(band.pct),
            "eligibility": mapped, "min_threshold": str(band.min_threshold),
            "floor_threshold": str(band.floor_threshold), "reason": band.reason,
            "rule_ids": band.rule_ids, "source_doc_ids": band.source_doc_ids,
            "source_sections": band.source_sections, "upcoming": _upcoming(band.upcoming),
        }
        applicable = rules.load_rules(ctx.conn)
        used = [rule for rule in applicable if rule.rule_id in band.rule_ids]
        return output, used
    return run_tool("check_exam_eligibility", {"course_code": course_code}, action)


def check_supplementary_eligibility(ctx: RequestContext, course_code: str):
    def action():
        profile = student_row(ctx)
        latest = latest_course_attempt(ctx, course_code)
        if latest is None:
            raise LookupError("No result record found for the requested course.")
        if str(latest["result"]).upper() not in {"FAIL", "ABSENT"}:
            return ({"course_code": course_code, "latest_result": latest["result"],
                     "latest_exam_session": latest["exam_session"], "latest_exam_type": latest["exam_type"],
                     "eligible": False, "reason": "There is no latest FAIL or ABSENT attempt requiring supplementary eligibility.",
                     "rule_ids": [], "source_doc_ids": [], "source_sections": [], "upcoming": []}, [])
        rule, _, upcoming = rules.resolve_parameter(
            "supplementary_eligibility", profile["programme"], profile["batch_year"], ctx.as_of_date, conn=ctx.conn,
        )
        eligible = rules.compare_values(latest["result"], rule.operator, rule.value)
        output = {"course_code": course_code, "latest_result": latest["result"],
                  "latest_exam_session": latest["exam_session"], "latest_exam_type": latest["exam_type"],
                  "eligible": eligible, "reason": rule.description, "rule_ids": [rule.rule_id],
                  "source_doc_ids": [rule.source_doc_id], "source_sections": [rule.source_section],
                  "upcoming": _upcoming(upcoming)}
        return output, [rule]
    return run_tool("check_supplementary_eligibility", {"course_code": course_code}, action)


def _placement(ctx, profile, backlog_count):
    cgpa_rule, _, cgpa_upcoming = rules.resolve_parameter(
        "min_cgpa_placement", profile["programme"], profile["batch_year"], ctx.as_of_date, conn=ctx.conn,
    )
    backlog_rule, _, backlog_upcoming = rules.resolve_parameter(
        "max_active_backlogs_placement", profile["programme"], profile["batch_year"], ctx.as_of_date, conn=ctx.conn,
    )
    cgpa_ok = rules.compare_values(profile["cgpa"], cgpa_rule.operator, cgpa_rule.value)
    backlog_ok = rules.compare_values(backlog_count, backlog_rule.operator, backlog_rule.value)
    checks = {
        "cgpa_check": {"actual": profile["cgpa"], "operator": cgpa_rule.operator, "required": cgpa_rule.value, "passed": cgpa_ok},
        "backlog_check": {"actual": backlog_count, "operator": backlog_rule.operator, "required": backlog_rule.value, "passed": backlog_ok},
    }
    reason = "All placement criteria are met." if cgpa_ok and backlog_ok else "One or more registry placement criteria are not met."
    used = [cgpa_rule, backlog_rule]
    return {
        "eligible": cgpa_ok and backlog_ok, "cgpa": profile["cgpa"], "active_backlogs": backlog_count,
        "checks": checks, "reason": reason, "rule_ids": [r.rule_id for r in used],
        "source_doc_ids": [r.source_doc_id for r in used], "source_sections": [r.source_section for r in used],
        "upcoming": _upcoming([*cgpa_upcoming, *backlog_upcoming]),
    }, used


def check_placement_eligibility(ctx: RequestContext):
    def action():
        profile = student_row(ctx)
        output, used = _placement(ctx, profile, profile["active_backlogs"])
        return output, used
    return run_tool("check_placement_eligibility", {}, action)


def whatif_supplementary_placement(ctx: RequestContext, course_code: str):
    def action():
        profile = student_row(ctx)
        latest = latest_course_attempt(ctx, course_code)
        if latest is None:
            raise LookupError("No result record found for the requested course.")
        if str(latest["result"]).upper() not in {"FAIL", "ABSENT"}:
            raise ValueError("What-if requires the course's latest attempt to be FAIL or ABSENT.")
        current, current_rules = _placement(ctx, profile, profile["active_backlogs"])
        assumed = max(profile["active_backlogs"] - 1, 0)
        hypothetical, hypothetical_rules = _placement(ctx, profile, assumed)
        assumption = "CGPA is not recomputed; the what-if assumes the supplementary removes one active backlog only."
        output = {
            "course_code": course_code, "current_active_backlogs": profile["active_backlogs"],
            "assumed_active_backlogs": assumed, "current_cgpa": profile["cgpa"],
            "current_placement_eligible": current["eligible"], "whatif_placement_eligible": hypothetical["eligible"],
            "assumptions": ["The student is assumed to pass the supplementary examination.",
                            "Exactly one active backlog is removed.", "Active backlogs cannot become negative.", assumption],
            "rule_ids": list(dict.fromkeys(current["rule_ids"] + hypothetical["rule_ids"])),
            "source_doc_ids": list(dict.fromkeys(current["source_doc_ids"] + hypothetical["source_doc_ids"])),
            "source_sections": list(dict.fromkeys(current["source_sections"] + hypothetical["source_sections"])),
        }
        return output, current_rules + hypothetical_rules
    return run_tool("whatif_supplementary_placement", {"course_code": course_code}, action)
