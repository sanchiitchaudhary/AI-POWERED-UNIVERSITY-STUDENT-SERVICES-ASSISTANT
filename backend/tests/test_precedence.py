import csv
from pathlib import Path

from app.precedence import Candidate, Context, resolve_candidates, resolve_rules


TODAY = "2026-10-06"


def candidate(key, doc_id, authority, start, value, *, section="7.1", end="", supersedes=(), programmes="ALL", batches="ALL"):
    return Candidate(
        key=key,
        doc_id=doc_id,
        section=section,
        authority_level=authority,
        effective_from=start,
        effective_to=end,
        supersedes=supersedes,
        scope_programmes=programmes,
        scope_batches=batches,
        value=value,
    )


def context(programme="B.Tech CSE", batch=2025, as_of=TODAY):
    return Context(as_of_date=as_of, programme=programme, batch_year=batch)


def rule(rule_id, parameter, value, doc_id, section, start, *, end="", programmes="ALL", batches="ALL"):
    return {
        "rule_id": rule_id,
        "parameter": parameter,
        "value": value,
        "source_doc_id": doc_id,
        "source_section": section,
        "effective_from": start,
        "effective_to": end,
        "scope_programmes": programmes,
        "scope_batches": batches,
    }


def source(doc_id, authority, *, supersedes=(), start="2024-01-01", end=""):
    return {
        "doc_id": doc_id,
        "authority_level": authority,
        "supersedes": list(supersedes),
        "effective_from": start,
        "effective_to": end,
    }


def _attendance_rules():
    """Use the checked-in Annex C minimum rule with the requested Annex A additions."""
    base_path = Path(__file__).resolve().parents[2] / "data" / "rule_registry.csv"
    with base_path.open(newline="", encoding="utf-8-sig") as f:
        base = next(row for row in csv.DictReader(f) if row["rule_id"] == "ATT-MIN-01")
    # The repository currently has only the Annex C DOC-001 seed. Enrich this
    # test copy with the source/scope metadata from the requested Annex A cases.
    base.update({"source_doc_id": "ACAD-REG-2024", "source_section": "7.1", "scope_programmes": "B.Tech", "scope_batches": "ALL"})
    circular = rule("ATT-MIN-03", "min_attendance_pct", "80", "ACAD-CIR-2026-08", "7.1", "2026-08-01", programmes="B.Tech", batches="2025+")
    mtech = rule("ATT-MIN-02", "min_attendance_pct", "75", "MTECH-REG-2025", "4.2", "2025-01-01", programmes="M.Tech", batches="ALL")
    rules = [base, circular, mtech]
    docs = [
        source("ACAD-REG-2024", 1, start="2024-01-01"),
        source("ACAD-CIR-2026-08", 2, supersedes=["ACAD-REG-2024#7.1"], start="2026-08-01"),
        source("MTECH-REG-2025", 1, start="2025-01-01"),
    ]
    return rules, docs


def test_annex_a_example_supersession_then_authority():
    regulation = candidate("ACAD-REG-2024", "ACAD-REG-2024", 1, "2024-01-01", 75)
    circular = candidate("ACAD-CIR-2026-08", "ACAD-CIR-2026-08", 2, "2026-08-01", 80, supersedes=["ACAD-REG-2024#7.1"])
    faq = candidate("FAQ-ATT", "STUDENT-FAQ", 4, "2026-09-15", 65)
    decision = resolve_candidates([regulation, circular, faq], context())

    assert decision.winner.key == "ACAD-CIR-2026-08"
    assert decision.winner.value == 80
    assert decision.decided_at_step == 3
    assert {loser["key"]: loser["step"] for loser in decision.losers} == {"ACAD-REG-2024": 2, "FAQ-ATT": 3}
    assert "supersedes ACAD-REG-2024#7.1 (step 2)" in decision.explanation


def test_registry_btech_batch_2025_circular_wins_at_step_two():
    rules, docs = _attendance_rules()
    decision = resolve_rules(rules, docs, context("B.Tech CSE", 2025))["min_attendance_pct"]
    assert decision.winner.key == "ATT-MIN-03"
    assert decision.winner.value == "80"
    assert decision.decided_at_step == 2


def test_registry_btech_2025_before_circular_has_regulation_and_upcoming_change():
    rules, docs = _attendance_rules()
    decision = resolve_rules(rules, docs, context("B.Tech CSE", 2025, "2026-07-31"))["min_attendance_pct"]
    assert decision.winner.key == "ATT-MIN-01"
    assert [item.key for item in decision.upcoming] == ["ATT-MIN-03"]


def test_registry_btech_batch_2024_only_old_rule_applies():
    rules, docs = _attendance_rules()
    decision = resolve_rules(rules, docs, context("B.Tech CSE", 2024))["min_attendance_pct"]
    assert decision.winner.key == "ATT-MIN-01"
    assert decision.decided_at_step == 1
    assert any(loser["key"] == "ATT-MIN-03" and loser["step"] == 1 for loser in decision.losers)


def test_registry_mtech_only_mtech_rule_applies():
    rules, docs = _attendance_rules()
    decision = resolve_rules(rules, docs, context("M.Tech AI", 2025))["min_attendance_pct"]
    assert decision.winner.key == "ATT-MIN-02"
    assert decision.winner.value == "75"
    assert decision.decided_at_step == 1


def test_detention_circular_supersedes_clause_7_3():
    rules = [
        rule("ATT-DETAIN-01", "detention_below_pct", "65", "ACAD-REG-2024", "7.3", "2024-01-01", programmes="B.Tech"),
        rule("ATT-DETAIN-02", "detention_below_pct", "70", "ACAD-CIR-2026-08", "7.3", "2026-08-01", programmes="B.Tech", batches="2025+"),
    ]
    docs = [source("ACAD-REG-2024", 1), source("ACAD-CIR-2026-08", 2, supersedes=["ACAD-REG-2024#7.3"])]
    decision = resolve_rules(rules, docs, context())["detention_below_pct"]
    assert decision.winner.key == "ATT-DETAIN-02"
    assert decision.winner.value == "70"
    assert decision.decided_at_step == 2


def test_level_three_supersession_is_ignored():
    top_authority = candidate("REG", "REG-DOC", 1, "2024-01-01", 75)
    notice = candidate("NOTICE", "NOTICE-DOC", 3, "2026-09-01", 80, supersedes=["REG-DOC#7.1"])
    decision = resolve_candidates([top_authority, notice], context())
    assert decision.winner.key == "REG"
    assert decision.decided_at_step == 3
    assert decision.losers == [{"key": "NOTICE", "doc_id": "NOTICE-DOC", "reason": "lower authority than level 1 candidate(s)", "step": 3}]


def test_same_authority_later_effective_date_wins_at_step_four():
    earlier = candidate("CIRC-1", "CIRC-1", 2, "2025-01-01", 75)
    later = candidate("CIRC-2", "CIRC-2", 2, "2026-03-01", 80)
    decision = resolve_candidates([earlier, later], context())
    assert decision.winner.key == "CIRC-2"
    assert decision.decided_at_step == 4
    assert decision.losers[0]["step"] == 4


def test_same_authority_and_date_with_different_values_is_conflict():
    one = candidate("CIRC-1", "CIRC-1", 2, "2026-03-01", 75)
    two = candidate("CIRC-2", "CIRC-2", 2, "2026-03-01", 80)
    decision = resolve_candidates([one, two], context())
    assert decision.winner is None
    assert decision.conflict is True
    assert decision.conflict_keys == ["CIRC-1", "CIRC-2"]
    assert decision.decided_at_step == 5
    assert "contact the issuing office" in decision.explanation


def test_level_five_content_is_only_informational():
    regulation = candidate("REG", "REG-DOC", 1, "2024-01-01", 75)
    forum = candidate("FORUM", "FORUM-DOC", 5, "2026-09-01", 90)
    decision = resolve_candidates([regulation, forum], context())
    assert decision.winner.key == "REG"
    assert decision.losers[0]["key"] == "FORUM"
    assert "informational" in decision.losers[0]["reason"]


def test_programme_prefix_and_2025_plus_batch_scope():
    scoped = candidate("CIRC", "CIRC", 2, "2026-01-01", 80, programmes="B.Tech", batches="2025+")
    included = resolve_candidates([scoped], context("B.Tech IT", 2025))
    excluded = resolve_candidates([scoped], context("B.Tech IT", 2024))
    assert included.winner.key == "CIRC"
    assert excluded.winner is None
    assert excluded.losers[0]["step"] == 1


