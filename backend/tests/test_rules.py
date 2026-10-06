import csv
import sqlite3
from pathlib import Path

import pytest

from app.db import init_db
from app.rules import RuleNotFound, compare_values, get_applicable_rules, get_attendance_band, resolve_parameter
from scripts.load_rules import load_rule_rows
from scripts.load_sources import load_source_rows


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _read_csv(name):
    with (DATA_DIR / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


@pytest.fixture
def registry_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    load_source_rows(_read_csv("source_register.csv"), conn)
    load_rule_rows(_read_csv("rule_registry.csv"), conn)
    yield conn
    conn.close()


def test_load_rules_rejects_missing_source_without_writing(registry_conn):
    before = registry_conn.execute("SELECT COUNT(*) FROM rule_registry").fetchone()[0]
    rows = [{
        "rule_id": "BAD-RULE", "description": "test", "parameter": "test_parameter",
        "operator": ">=", "value": "1", "scope_programmes": "ALL",
        "scope_batches": "ALL", "effective_from": "2026-01-01", "effective_to": "",
        "source_doc_id": "MISSING-DOC", "source_section": "1.1",
    }]
    with pytest.raises(ValueError, match="BAD-RULE.*MISSING-DOC"):
        load_rule_rows(rows, registry_conn)
    assert registry_conn.execute("SELECT COUNT(*) FROM rule_registry").fetchone()[0] == before


def test_programme_prefix_and_batch_scopes(registry_conn):
    btech_cse = get_applicable_rules("min_attendance_pct", "B.Tech CSE", 2025, "2026-10-06", conn=registry_conn)["applicable"]
    btech_it = get_applicable_rules("min_attendance_pct", "B.Tech IT", 2026, "2026-10-06", conn=registry_conn)["applicable"]
    mtech = get_applicable_rules("min_attendance_pct", "M.Tech CSE", 2025, "2026-10-06", conn=registry_conn)["applicable"]
    btech_2024 = get_applicable_rules("min_attendance_pct", "B.Tech CSE", 2024, "2026-10-06", conn=registry_conn)["applicable"]

    assert {rule.rule_id for rule in btech_cse} == {"ATT-MIN-01", "ATT-MIN-03"}
    assert {rule.rule_id for rule in btech_it} == {"ATT-MIN-01", "ATT-MIN-03"}
    assert {rule.rule_id for rule in mtech} == {"ATT-MIN-02"}
    assert {rule.rule_id for rule in btech_2024} == {"ATT-MIN-01"}


def test_btech_2025_condonation_band(registry_conn):
    band = get_attendance_band("B.Tech CSE", 2025, 0, 40, 31, "2026-10-06", conn=registry_conn)
    assert band.band == "CONDONATION"
    assert band.min_threshold == 80
    assert band.floor_threshold == 70
    assert {"ATT-MIN-03", "ATT-DETAIN-02"}.issubset(band.rule_ids)


def test_btech_2025_before_circular_is_eligible_and_reports_upcoming(registry_conn):
    band = get_attendance_band("B.Tech CSE", 2025, 0, 40, 31, "2026-07-31", conn=registry_conn)
    assert band.band == "ELIGIBLE"
    assert band.min_threshold == 75
    assert "ATT-MIN-03" in {rule.rule_id for rule in band.upcoming}


def test_btech_2024_exact_minimum_is_eligible(registry_conn):
    band = get_attendance_band("B.Tech CSE", 2024, 0, 48, 36, "2026-10-06", conn=registry_conn)
    assert band.band == "ELIGIBLE"
    assert band.pct == 75
    assert "ATT-MIN-01" in band.rule_ids


def test_btech_2024_below_minimum_is_condonation(registry_conn):
    band = get_attendance_band("B.Tech CSE", 2024, 0, 48, 35, "2026-10-06", conn=registry_conn)
    assert band.band == "CONDONATION"
    assert str(band.pct) == "72.92"


@pytest.mark.parametrize(
    "batch,attended,expected",
    [(2025, 27, "DETENTION"), (2024, 27, "CONDONATION"), (2025, 28, "CONDONATION"), (2025, 32, "ELIGIBLE")],
)
def test_btech_boundary_bands(registry_conn, batch, attended, expected):
    band = get_attendance_band("B.Tech CSE", batch, 0, 40, attended, "2026-10-06", conn=registry_conn)
    assert band.band == expected
    if attended == 28:
        assert band.pct == 70
    if attended == 32:
        assert band.pct == 80


@pytest.mark.parametrize(
    "attended,expected",
    [(31, "CONDONATION"), (26, "CONDONATION"), (25, "DETENTION")],
)
def test_mtech_boundaries(registry_conn, attended, expected):
    band = get_attendance_band("M.Tech CSE", 2025, 0, 40, attended, "2026-10-06", conn=registry_conn)
    assert band.band == expected
    assert band.min_threshold == 80
    assert band.floor_threshold == 65
    if attended == 26:
        assert band.pct == 65


def test_backlog_block_uses_registry_operator_and_limit(registry_conn):
    blocked = get_attendance_band("B.Tech CSE", 2024, 5, 10, 7, "2026-10-06", conn=registry_conn)
    allowed = get_attendance_band("B.Tech CSE", 2024, 4, 10, 7, "2026-10-06", conn=registry_conn)
    assert blocked.band == "DETENTION"
    assert "more than 4 active backlogs" in blocked.reason
    assert "COND-BLOCK-01" in blocked.rule_ids
    assert allowed.band == "CONDONATION"


def test_rule_effective_from_day_is_inclusive(registry_conn):
    winner, decision, _ = resolve_parameter("min_attendance_pct", "B.Tech CSE", 2025, "2026-08-01", conn=registry_conn)
    assert winner.rule_id == "ATT-MIN-03"
    assert decision.decided_at_step == 2


def test_missing_parameter_raises_rule_not_found(registry_conn):
    with pytest.raises(RuleNotFound):
        resolve_parameter("no_such_parameter", "B.Tech CSE", 2025, "2026-10-06", conn=registry_conn)


def test_band_citations_exist_in_source_register(registry_conn):
    band = get_attendance_band("B.Tech CSE", 2025, 5, 40, 28, "2026-10-06", conn=registry_conn)
    docs = {row[0] for row in registry_conn.execute("SELECT doc_id FROM source_register")}
    assert band.rule_ids
    assert set(band.source_doc_ids).issubset(docs)


def test_safe_rule_comparator():
    assert compare_values(80, ">=", "80")
    assert compare_values(2, "<=", "2")
    assert compare_values(5, ">", "4")
    assert compare_values(64, "<", "65")
    assert compare_values(65, "between", "65,75")
    assert compare_values("PASS", "=", "PASS")
    with pytest.raises(ValueError, match="Unsupported"):
        compare_values(1, "or True", 1)
