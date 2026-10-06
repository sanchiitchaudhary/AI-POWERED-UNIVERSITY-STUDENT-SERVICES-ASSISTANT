"""Code-owned deterministic tool registry."""
from app.tools.eligibility import (
    check_exam_eligibility,
    check_placement_eligibility,
    check_supplementary_eligibility,
    whatif_supplementary_placement,
)
from app.tools.student import (
    get_attendance,
    get_attendance_all,
    get_backlogs,
    get_profile,
    get_results,
    list_courses,
)

TOOL_REGISTRY = {
    function.__name__: function
    for function in (
        get_profile, get_attendance, get_attendance_all, get_results, get_backlogs,
        check_exam_eligibility, check_supplementary_eligibility,
        check_placement_eligibility, whatif_supplementary_placement, list_courses,
    )
}


def get_tool(name: str):
    """Return a tool by its exact registered name."""
    return TOOL_REGISTRY[name]


TOOLS = TOOL_REGISTRY

__all__ = ["TOOL_REGISTRY", "TOOLS", "get_tool", *TOOL_REGISTRY]
