"""Rule registry loading, applicability, precedence, and attendance bands."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Iterator, Mapping

from app.db import get_conn
from app.precedence import (
    Candidate,
    Context,
    PrecedenceDecision,
    candidate_status,
    resolve_rules as resolve_rule_rows,
)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    description: str
    parameter: str
    operator: str
    value: str
    scope_programmes: str
    scope_batches: str
    effective_from: str
    effective_to: str
    source_doc_id: str
    source_section: str
    authority_level: int
    supersedes: tuple[str, ...]
    source_effective_from: str
    source_document: Mapping[str, Any]

    def as_registry_row(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "parameter": self.parameter,
            "operator": self.operator,
            "value": self.value,
            "scope_programmes": self.scope_programmes,
            "scope_batches": self.scope_batches,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "source_doc_id": self.source_doc_id,
            "source_section": self.source_section,
        }

    def as_source_row(self) -> dict[str, Any]:
        return dict(self.source_document)


class RuleNotFound(LookupError):
    """No current authoritative rule applies in the supplied context."""


class RuleConflict(RuntimeError):
    """Applicable rules conflict at the same authority and effective date."""

    def __init__(self, decision: PrecedenceDecision):
        self.decision = decision
        super().__init__(decision.explanation)


@dataclass(frozen=True)
class AttendanceBand:
    band: str
    pct: Decimal
    min_threshold: Decimal
    floor_threshold: Decimal
    rule_ids: list[str]
    source_doc_ids: list[str]
    source_sections: list[str]
    reason: str
    precedence_decision: dict[str, PrecedenceDecision | None]
    upcoming: list[Rule]


@contextmanager
def _connection(conn=None) -> Iterator[Any]:
    if conn is not None:
        yield conn
        return
    owned = get_conn()
    try:
        yield owned
    finally:
        owned.close()


def _split_supersedes(value: Any) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return tuple(part.strip() for part in str(value).replace(";", ",").split(",") if part.strip())


def _make_rule(row: Mapping[str, Any]) -> Rule:
    source = {
        "doc_id": row["joined_doc_id"],
        "title": row["title"],
        "issuer": row["issuer"],
        "authority_level": row["authority_level"],
        "doc_type": row["doc_type"],
        "version": row["version"],
        "effective_from": row["source_effective_from"],
        "effective_to": row["source_effective_to"],
        "supersedes": row["supersedes"],
        "scope_programmes": row["source_scope_programmes"],
        "scope_batches": row["source_scope_batches"],
        "provenance": row["provenance"],
        "retrieved_on": row["retrieved_on"],
        "synthetic": row["synthetic"],
    }
    return Rule(
        rule_id=str(row["rule_id"]),
        description=str(row["description"] or ""),
        parameter=str(row["parameter"]),
        operator=str(row["operator"]),
        value=str(row["value"]),
        scope_programmes=str(row["scope_programmes"] or "ALL"),
        scope_batches=str(row["scope_batches"] or "ALL"),
        effective_from=str(row["effective_from"] or ""),
        effective_to=str(row["effective_to"] or ""),
        source_doc_id=str(row["source_doc_id"]),
        source_section=str(row["source_section"] or ""),
        authority_level=int(row["authority_level"]),
        supersedes=_split_supersedes(row["supersedes"]),
        source_effective_from=str(row["source_effective_from"] or ""),
        source_document=source,
    )


def load_rules(conn=None) -> list[Rule]:
    """Load rule rows joined with their source-register document metadata."""
    sql = """
    SELECT r.rule_id, r.description, r.parameter, r.operator, r.value,
           r.scope_programmes, r.scope_batches, r.effective_from, r.effective_to,
           r.source_doc_id, r.source_section,
           s.doc_id AS joined_doc_id, s.title, s.issuer, s.authority_level,
           s.doc_type, s.version, s.effective_from AS source_effective_from,
           s.effective_to AS source_effective_to, s.supersedes,
           s.scope_programmes AS source_scope_programmes,
           s.scope_batches AS source_scope_batches, s.provenance, s.retrieved_on,
           s.synthetic
      FROM rule_registry AS r
      JOIN source_register AS s ON s.doc_id = r.source_doc_id
     ORDER BY r.rule_id
    """
    with _connection(conn) as connection:
        rows = connection.execute(sql).fetchall()
        return [_make_rule(dict(row)) for row in rows]


def _candidate(rule: Rule) -> Candidate:
    return Candidate(
        key=rule.rule_id,
        doc_id=rule.source_doc_id,
        section=rule.source_section,
        authority_level=rule.authority_level,
        effective_from=rule.effective_from or rule.source_effective_from,
        effective_to=rule.effective_to,
        supersedes=rule.supersedes,
        scope_programmes=rule.scope_programmes,
        scope_batches=rule.scope_batches,
        value=rule.value,
    )


def _ctx(as_of_date: str | date, programme: str, batch_year: int | str) -> Context:
    return Context(as_of_date=as_of_date, programme=programme, batch_year=batch_year)


def get_applicable_rules(parameter: str, programme: str, batch_year: int | str, as_of_date: str | date, *, conn=None) -> dict[str, list[Rule]]:
    """Return current and future rules after shared scope/date classification."""
    context = _ctx(as_of_date, programme, batch_year)
    applicable: list[Rule] = []
    upcoming: list[Rule] = []
    for rule in load_rules(conn):
        if rule.parameter != parameter:
            continue
        status = candidate_status(_candidate(rule), context)
        if status == "applicable":
            applicable.append(rule)
        elif status == "upcoming":
            upcoming.append(rule)
    return {"applicable": applicable, "upcoming": upcoming}


def resolve_parameter(parameter: str, programme: str, batch_year: int | str, as_of_date: str | date, *, conn=None) -> tuple[Rule, PrecedenceDecision | None, list[Rule]]:
    """Resolve one parameter for a programme, batch, and explicit date."""
    result = get_applicable_rules(parameter, programme, batch_year, as_of_date, conn=conn)
    applicable = result["applicable"]
    upcoming = result["upcoming"]
    if not applicable:
        raise RuleNotFound(f"No applicable rule for {parameter!r}, {programme!r}, batch {batch_year} on {as_of_date}")
    if len(applicable) == 1:
        return applicable[0], None, upcoming

    rule_rows = [rule.as_registry_row() for rule in applicable]
    source_rows_by_id = {rule.source_doc_id: rule.as_source_row() for rule in applicable}
    decisions = resolve_rule_rows(rule_rows, source_rows_by_id.values(), _ctx(as_of_date, programme, batch_year))
    decision = decisions[parameter]
    if decision.conflict:
        raise RuleConflict(decision)
    if decision.winner is None:
        raise RuleNotFound(f"No authoritative rule for {parameter!r}, {programme!r}, batch {batch_year} on {as_of_date}")
    winner = next(rule for rule in applicable if rule.rule_id == decision.winner.key)
    return winner, decision, upcoming


def _as_decimal(value: Any, label: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{label} must be a numeric registry value") from exc
    if not number.is_finite():
        raise ValueError(f"{label} must be finite")
    return number


def _pair(value: Any) -> tuple[Any, Any]:
    if isinstance(value, str):
        pieces = [piece.strip() for piece in value.split(",")]
    elif isinstance(value, (tuple, list)):
        pieces = list(value)
    else:
        raise ValueError("between operator needs a two-value range")
    if len(pieces) != 2:
        raise ValueError("between operator needs a two-value range")
    return pieces[0], pieces[1]


def compare_values(left: Any, operator: str, right: Any) -> bool:
    """Compare safe supported operators without evaluating input as code."""
    op = operator.strip().lower()
    if op == "between":
        low, high = _pair(right)
        left_num = _as_decimal(left, "left value")
        return _as_decimal(low, "lower bound") <= left_num <= _as_decimal(high, "upper bound")
    try:
        left_value, right_value = _as_decimal(left, "left value"), _as_decimal(right, "right value")
    except ValueError:
        if op == "=":
            return str(left) == str(right)
        raise
    if op == ">=":
        return left_value >= right_value
    if op == "<=":
        return left_value <= right_value
    if op == ">":
        return left_value > right_value
    if op == "<":
        return left_value < right_value
    if op == "=":
        return left_value == right_value
    raise ValueError(f"Unsupported rule operator {operator!r}")


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def get_attendance_band(programme: str, batch_year: int | str, active_backlogs: int, classes_held: int, classes_attended: int, as_of_date: str | date, *, conn=None) -> AttendanceBand:
    """Calculate a student's attendance band using only applicable registry rules."""
    if classes_held <= 0:
        raise ValueError("classes_held must be greater than zero")
    if classes_attended < 0 or classes_attended > classes_held:
        raise ValueError("classes_attended must be between zero and classes_held")

    minimum, minimum_decision, upcoming_minimum = resolve_parameter("min_attendance_pct", programme, batch_year, as_of_date, conn=conn)
    floor, floor_decision, upcoming_floor = resolve_parameter("detention_below_pct", programme, batch_year, as_of_date, conn=conn)
    min_value = _as_decimal(minimum.value, f"{minimum.rule_id} value")
    floor_value = _as_decimal(floor.value, f"{floor.rule_id} value")
    attended_x100 = Decimal(classes_attended) * Decimal(100)
    held_decimal = Decimal(classes_held)

    rules = [minimum, floor]
    upcoming = [*upcoming_minimum, *upcoming_floor]
    precedence = {"min_attendance_pct": minimum_decision, "detention_below_pct": floor_decision}
    if attended_x100 >= min_value * held_decimal:
        band = "ELIGIBLE"
        reason = f"attendance meets minimum threshold {min_value}%"
    elif attended_x100 >= floor_value * held_decimal:
        band = "CONDONATION"
        reason = f"attendance is between detention floor {floor_value}% and minimum {min_value}%"
        try:
            backlog_rule, backlog_decision, upcoming_backlog = resolve_parameter("active_backlogs", programme, batch_year, as_of_date, conn=conn)
        except RuleNotFound:
            backlog_rule = None
        else:
            rules.append(backlog_rule)
            precedence["active_backlogs"] = backlog_decision
            upcoming.extend(upcoming_backlog)
            if compare_values(active_backlogs, backlog_rule.operator, backlog_rule.value):
                limit = _as_decimal(backlog_rule.value, f"{backlog_rule.rule_id} value")
                band = "DETENTION"
                reason = f"condonation not available (more than {limit.normalize():f} active backlogs)"
    else:
        band = "DETENTION"
        reason = f"attendance is below detention floor {floor_value}%"

    displayed_pct = (attended_x100 / held_decimal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return AttendanceBand(
        band=band,
        pct=displayed_pct,
        min_threshold=min_value,
        floor_threshold=floor_value,
        rule_ids=_unique([rule.rule_id for rule in rules]),
        source_doc_ids=_unique([rule.source_doc_id for rule in rules]),
        source_sections=_unique([rule.source_section for rule in rules]),
        reason=reason,
        precedence_decision=precedence,
        upcoming=list({rule.rule_id: rule for rule in upcoming}.values()),
    )
