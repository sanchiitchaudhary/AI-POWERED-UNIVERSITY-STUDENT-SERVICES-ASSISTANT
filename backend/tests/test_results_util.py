import pytest

from app.results_util import latest_attempts, pending_backlog_counts


def attempt(session, result, exam_type="REGULAR", course="CS101"):
    return {
        "student_id": "S1001",
        "course_code": course,
        "exam_session": session,
        "exam_type": exam_type,
        "result": result,
    }


def test_july_supplementary_pass_resolves_may_fail():
    rows = [attempt("2026-MAY", "FAIL"), attempt("2026-JUL", "PASS", "SUPPLEMENTARY")]
    assert pending_backlog_counts(rows) == {}


def test_may_fail_only_is_pending():
    rows = [attempt("2026-MAY", "FAIL")]
    assert pending_backlog_counts(rows) == {"S1001": 1}


def test_later_session_fail_after_pass_is_pending():
    rows = [attempt("2026-MAY", "PASS"), attempt("2026-JUL", "FAIL")]
    assert pending_backlog_counts(rows) == {"S1001": 1}


def test_supplementary_wins_when_sessions_tie():
    rows = [attempt("2026-MAY", "FAIL", "REGULAR"), attempt("2026-MAY", "PASS", "SUPPLEMENTARY")]
    assert pending_backlog_counts(rows) == {}


def test_unparseable_session_raises_clear_error():
    with pytest.raises(ValueError, match=r"Invalid exam_session.*YYYY-MON"):
        latest_attempts([attempt("2026-REG", "FAIL")])


@pytest.mark.parametrize("result", ["ABSENT", "DETAINED"])
def test_absent_and_detained_are_pending(result):
    assert pending_backlog_counts([attempt("2026-MAY", result)]) == {"S1001": 1}
