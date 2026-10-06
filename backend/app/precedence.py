"""Pure Annex A source-precedence resolution functions.

This module deliberately performs no database, LLM, or implicit current-date
access. Callers supply candidates and an explicit resolution context.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Mapping, Sequence

DateValue = date | str
ScopeValue = str | int | Sequence[str | int]


@dataclass(frozen=True)
class Candidate:
    key: str
    doc_id: str
    section: str
    authority_level: int
    effective_from: DateValue
    effective_to: DateValue | None = ""
    supersedes: Sequence[str] = field(default_factory=tuple)
    scope_programmes: ScopeValue = "ALL"
    scope_batches: ScopeValue = "ALL"
    value: Any = None


@dataclass(frozen=True)
class Context:
    as_of_date: DateValue
    programme: str
    batch_year: int | str


@dataclass
class PrecedenceDecision:
    winner: Candidate | None
    losers: list[dict[str, Any]]
    upcoming: list[Candidate]
    conflict: bool
    conflict_keys: list[str]
    decided_at_step: int
    explanation: str


def _as_date(value: DateValue, field_name: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name} date {value!r}; expected YYYY-MM-DD") from exc


def _scope_items(scope: ScopeValue | None) -> list[str]:
    if scope is None or scope == "":
        return ["ALL"]
    if isinstance(scope, (str, int)):
        return [part.strip() for part in str(scope).split(",") if part.strip()]
    return [str(item).strip() for item in scope if str(item).strip()]


def _programme_applies(scope: ScopeValue, programme: str) -> bool:
    scopes = _scope_items(scope)
    return any(token.casefold() == "all" or programme.casefold().startswith(token.casefold()) for token in scopes)


def _batch_applies(scope: ScopeValue, batch_year: int | str) -> bool:
    try:
        batch = int(batch_year)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid context batch_year {batch_year!r}; expected a year") from exc
    for token in _scope_items(scope):
        normalized = token.strip()
        if normalized.casefold() == "all":
            return True
        if normalized.endswith("+"):
            try:
                if batch >= int(normalized[:-1]):
                    return True
            except ValueError as exc:
                raise ValueError(f"Invalid batch scope {normalized!r}; expected a year, comma list, or YEAR+") from exc
        else:
            try:
                if batch == int(normalized):
                    return True
            except ValueError as exc:
                raise ValueError(f"Invalid batch scope {normalized!r}; expected a year, comma list, or YEAR+") from exc
    return False


def _matches_scope(candidate: Candidate, ctx: Context) -> bool:
    return _programme_applies(candidate.scope_programmes, ctx.programme) and _batch_applies(candidate.scope_batches, ctx.batch_year)


def _supersedes_tokens(value: Sequence[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.replace(";", ",").split(",") if v.strip()]
    return [str(v).strip() for v in value if str(v).strip()]


def _section(section: str) -> str:
    return str(section or "").strip().lstrip("#").strip()


def _supersession_match(x: Candidate, y: Candidate) -> bool:
    if x is y or x.authority_level > 2:
        return False
    targets = set(_supersedes_tokens(x.supersedes))
    return y.doc_id in targets or f"{y.doc_id}#{_section(y.section)}" in targets


def _loser(candidate: Candidate, reason: str, step: int) -> dict[str, Any]:
    return {"key": candidate.key, "doc_id": candidate.doc_id, "reason": reason, "step": step}


def resolve_candidates(candidates: Iterable[Candidate], ctx: Context) -> PrecedenceDecision:
    """Resolve candidates under Annex A steps 1 through 5."""
    as_of = _as_date(ctx.as_of_date, "as_of_date")
    losers: list[dict[str, Any]] = []
    upcoming: list[Candidate] = []
    applicable: list[Candidate] = []

    # Step 1: a future candidate is reported separately when its scopes match.
    for candidate in candidates:
        if not 1 <= int(candidate.authority_level) <= 5:
            raise ValueError(f"Candidate {candidate.key!r} has authority_level outside 1..5")
        if not _matches_scope(candidate, ctx):
            losers.append(_loser(candidate, "scope excludes this programme or batch", 1))
            continue
        starts = _as_date(candidate.effective_from, f"effective_from for {candidate.key}")
        if starts > as_of:
            upcoming.append(candidate)
            continue
        ends = _as_date(candidate.effective_to, f"effective_to for {candidate.key}") if candidate.effective_to else None
        if ends is not None and ends < as_of:
            losers.append(_loser(candidate, "not effective on the supplied as_of_date", 1))
            continue
        applicable.append(candidate)

    if not applicable:
        explanation = "No candidate is currently applicable."
        if upcoming:
            explanation = "No current candidate applies; matching candidates are listed as upcoming changes."
        return PrecedenceDecision(None, losers, upcoming, False, [], 1, explanation)

    if len(applicable) == 1:
        winner = applicable[0]
        return PrecedenceDecision(winner, losers, upcoming, False, [], 1, f"{winner.key} is the only applicable candidate (step 1).")

    # Step 2: only authority levels 1 and 2 can explicitly supersede.
    superseded_by: dict[int, Candidate] = {}
    for yi, y in enumerate(applicable):
        for x in applicable:
            if _supersession_match(x, y):
                superseded_by[yi] = x
                break
    current = []
    for i, candidate in enumerate(applicable):
        superseder = superseded_by.get(i)
        if superseder is None:
            current.append(candidate)
        else:
            losers.append(_loser(candidate, f"superseded by {superseder.key} ({superseder.doc_id})", 2))
    if not current:
        return PrecedenceDecision(None, losers, upcoming, False, [], 2, "All applicable candidates were superseded at step 2.")
    if len(current) == 1:
        winner = current[0]
        explicit = [x for x in superseded_by.values() if x is winner]
        if explicit:
            old = next(y for i, y in enumerate(applicable) if superseded_by.get(i) is winner)
            explanation = f"{winner.key} supersedes {old.doc_id}#{_section(old.section)} (step 2)."
            return PrecedenceDecision(winner, losers, upcoming, False, [], 2, explanation)
        return PrecedenceDecision(winner, losers, upcoming, False, [], 2, f"{winner.key} remains after explicit supersession checks (step 2).")

    # Step 3: lower authority number wins; level 5 is informational only.
    authoritative = [candidate for candidate in current if int(candidate.authority_level) < 5]
    if not authoritative:
        for candidate in current:
            losers.append(_loser(candidate, "level 5 content is informational and cannot be authoritative", 3))
        return PrecedenceDecision(None, losers, upcoming, False, [], 3, "Only level 5 informational content applies; contact the issuing office for an authoritative source.")
    best_level = min(int(candidate.authority_level) for candidate in authoritative)
    authority_winners = [candidate for candidate in authoritative if int(candidate.authority_level) == best_level]
    for candidate in current:
        if candidate not in authority_winners:
            if int(candidate.authority_level) == 5:
                reason = "level 5 content is informational and cannot override an authoritative source"
            else:
                reason = f"lower authority than level {best_level} candidate(s)"
            losers.append(_loser(candidate, reason, 3))
    if len(authority_winners) == 1:
        winner = authority_winners[0]
        superseded = [y for i, y in enumerate(applicable) if superseded_by.get(i) is winner]
        prefix = f"{winner.key} supersedes {superseded[0].doc_id}#{_section(superseded[0].section)} (step 2); " if superseded else ""
        return PrecedenceDecision(winner, losers, upcoming, False, [], 3, f"{prefix}{winner.key} wins by higher authority (step 3).")

    # Step 4: among equal authority, later effective_from wins.
    latest_date = max(_as_date(candidate.effective_from, f"effective_from for {candidate.key}") for candidate in authority_winners)
    recency_winners = [candidate for candidate in authority_winners if _as_date(candidate.effective_from, f"effective_from for {candidate.key}") == latest_date]
    for candidate in authority_winners:
        if candidate not in recency_winners:
            losers.append(_loser(candidate, f"older effective_from than {latest_date.isoformat()}", 4))
    if len(recency_winners) == 1:
        winner = recency_winners[0]
        superseded = [y for i, y in enumerate(applicable) if superseded_by.get(i) is winner]
        prefix = f"{winner.key} supersedes {superseded[0].doc_id}#{_section(superseded[0].section)} (step 2); " if superseded else ""
        return PrecedenceDecision(winner, losers, upcoming, False, [], 4, f"{prefix}{winner.key} wins by more recent effective_from (step 4).")

    # Step 5: a tie with differing values is unresolved; equal values are equivalent.
    tied_values: list[Any] = []
    for candidate in recency_winners:
        if candidate.value not in tied_values:
            tied_values.append(candidate.value)
    if len(tied_values) > 1:
        keys = [candidate.key for candidate in recency_winners]
        return PrecedenceDecision(None, losers, upcoming, True, keys, 5, "Conflicting candidates have the same authority and effective date; contact the issuing office.")

    winner = recency_winners[0]
    for candidate in recency_winners[1:]:
        losers.append(_loser(candidate, f"same authority, effective date, and value as {winner.key}", 5))
    return PrecedenceDecision(winner, losers, upcoming, False, [], 5, f"{winner.key} is selected from equivalent same-date candidates (step 5).")


def _row(row: Any, name: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(name, default)
    try:
        return row[name]
    except (TypeError, IndexError, KeyError):
        return getattr(row, name, default)


def _supersedes_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).replace(";", ",").split(",") if part.strip()]


def resolve_rules(rule_rows: Iterable[Any], source_register_rows: Iterable[Any], ctx: Context) -> dict[str, PrecedenceDecision]:
    """Join registry rules to source metadata and resolve each parameter alone."""
    sources = {str(_row(source, "doc_id")): source for source in source_register_rows}
    grouped: dict[str, list[Candidate]] = {}
    for rule in rule_rows:
        parameter = str(_row(rule, "parameter", ""))
        doc_id = str(_row(rule, "source_doc_id", ""))
        source = sources.get(doc_id)
        if source is None:
            raise ValueError(f"Rule {_row(rule, 'rule_id')!r} references missing source document {doc_id!r}")
        rule_from = _row(rule, "effective_from") or _row(source, "effective_from")
        if not rule_from:
            raise ValueError(f"Rule {_row(rule, 'rule_id')!r} and source {doc_id!r} have no effective_from date")
        candidate = Candidate(
            key=str(_row(rule, "rule_id")),
            doc_id=doc_id,
            section=str(_row(rule, "source_section", "") or ""),
            authority_level=int(_row(source, "authority_level")),
            effective_from=rule_from,
            effective_to=_row(rule, "effective_to") or "",
            supersedes=_supersedes_list(_row(source, "supersedes")),
            scope_programmes=_row(rule, "scope_programmes", "ALL") or "ALL",
            scope_batches=_row(rule, "scope_batches", "ALL") or "ALL",
            value=_row(rule, "value"),
        )
        grouped.setdefault(parameter, []).append(candidate)
    return {parameter: resolve_candidates(candidates, ctx) for parameter, candidates in grouped.items()}
