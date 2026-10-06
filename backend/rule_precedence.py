import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.database import get_db_connection

def parse_scope_batch_match(scope: str, batch: str) -> bool:
    if not scope or scope.upper() == 'ALL':
        return True
    
    scope = scope.strip()
    
    # 2023+
    if scope.endswith('+'):
        try:
            min_year = int(scope[:-1])
            student_year = int(batch)
            return student_year >= min_year
        except ValueError:
            return False

    # 2021-2023
    if '-' in scope:
        parts = scope.split('-')
        if len(parts) == 2:
            try:
                start_year = int(parts[0])
                end_year = int(parts[1])
                student_year = int(batch)
                return start_year <= student_year <= end_year
            except ValueError:
                return False

    # 2022;2023
    batches = [b.strip() for b in scope.replace(';', ',').split(',')]
    return batch in batches

def parse_scope_programme_match(scope: str, programme: str) -> bool:
    if not scope or scope.upper() == 'ALL':
        return True
    
    programmes = [p.strip().lower() for p in scope.split(';')]
    return programme.strip().lower() in programmes or 'all' in programmes

def eval_operator_condition(operator: str, threshold_val: str, actual_val: float) -> bool:
    operator = operator.strip().lower()
    
    if operator == '>=':
        return actual_val >= float(threshold_val)
    elif operator == '>':
        return actual_val > float(threshold_val)
    elif operator == '<=':
        return actual_val <= float(threshold_val)
    elif operator == '<':
        return actual_val < float(threshold_val)
    elif operator == '==':
        return actual_val == float(threshold_val)
    elif operator == 'between':
        parts = threshold_val.split(',')
        if len(parts) == 2:
            lo, hi = float(parts[0]), float(parts[1])
            return lo <= actual_val <= hi
        raise ValueError(f"Invalid 'between' value schema: '{threshold_val}'. Expected 'lo,hi'.")
    else:
        raise ValueError(f"Unsupported rule registry operator: '{operator}'")

def get_applicable_rules(
    parameter: str,
    as_of_date: str,
    programme: str = "ALL",
    batch: str = "ALL"
) -> Tuple[Optional[Dict[str, Any]], bool, List[Dict[str, Any]]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, rule_code, parameter, operator, value, effective_from, 
               scope_programmes, scope_batches, authority_level, source_doc_id, status
        FROM rule_registry
        WHERE parameter = ? AND status = 'active' AND effective_from <= ?
        ORDER BY authority_level ASC, effective_from DESC
    ''', (parameter, as_of_date))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    matching_rules = []
    for r in rows:
        prog_match = parse_scope_programme_match(r['scope_programmes'], programme)
        batch_match = parse_scope_batch_match(r['scope_batches'], batch)
        if prog_match and batch_match:
            matching_rules.append(r)

    if not matching_rules:
        return None, False, []

    # Winning rule is highest authority (lowest level int) and most recent effective_from
    winning_rule = matching_rules[0]

    # Check for conflict: same authority level & date, but different threshold values
    has_conflict = False
    for r in matching_rules[1:]:
        if (r['authority_level'] == winning_rule['authority_level'] and 
            r['effective_from'] == winning_rule['effective_from'] and 
            r['value'] != winning_rule['value']):
            has_conflict = True
            break

    return winning_rule, has_conflict, matching_rules
