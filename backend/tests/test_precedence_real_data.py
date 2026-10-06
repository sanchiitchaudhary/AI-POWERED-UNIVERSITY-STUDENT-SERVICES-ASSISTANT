import csv
from pathlib import Path

from app.precedence import Context, resolve_rules


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _load_csv(name):
    with (DATA_DIR / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _decision(parameter, *, programme, batch, as_of):
    decisions = resolve_rules(
        _load_csv("rule_registry.csv"),
        _load_csv("source_register.csv"),
        Context(as_of_date=as_of, programme=programme, batch_year=batch),
    )
    return decisions[parameter]


def test_btech_2025_minimum_attendance_circular_wins():
    decision = _decision("min_attendance_pct", programme="B.Tech CSE", batch=2025, as_of="2026-10-06")
    assert decision.winner.key == "ATT-MIN-03"
    assert decision.winner.value == "80"
    assert decision.decided_at_step == 2
    assert any(loser["key"] == "ATT-MIN-01" for loser in decision.losers)


def test_btech_2025_minimum_attendance_before_circular_effective_date():
    decision = _decision("min_attendance_pct", programme="B.Tech CSE", batch=2025, as_of="2026-07-31")
    assert decision.winner.key == "ATT-MIN-01"
    assert decision.winner.value == "75"
    assert [candidate.key for candidate in decision.upcoming] == ["ATT-MIN-03"]


def test_btech_2024_minimum_attendance_only_old_rule_applies():
    decision = _decision("min_attendance_pct", programme="B.Tech CSE", batch=2024, as_of="2026-10-06")
    assert decision.winner.key == "ATT-MIN-01"
    assert decision.decided_at_step == 1


def test_mtech_2025_minimum_attendance_uses_mtech_rule_only():
    decision = _decision("min_attendance_pct", programme="M.Tech CSE", batch=2025, as_of="2026-10-06")
    assert decision.winner.key == "ATT-MIN-02"
    assert decision.winner.value == "80"
    assert decision.decided_at_step == 1


def test_btech_2025_detention_circular_supersedes_regulation_clause():
    decision = _decision("detention_below_pct", programme="B.Tech CSE", batch=2025, as_of="2026-10-06")
    assert decision.winner.key == "ATT-DETAIN-02"
    assert decision.winner.value == "70"
    assert decision.decided_at_step == 2
    assert any(loser["key"] == "ATT-DETAIN-01" for loser in decision.losers)
    assert "supersedes ACAD-REG-2024#7.3 (step 2)" in decision.explanation


def test_btech_2024_detention_uses_regulation_rule():
    decision = _decision("detention_below_pct", programme="B.Tech CSE", batch=2024, as_of="2026-10-06")
    assert decision.winner.key == "ATT-DETAIN-01"
    assert decision.winner.value == "65"
    assert decision.decided_at_step == 1
