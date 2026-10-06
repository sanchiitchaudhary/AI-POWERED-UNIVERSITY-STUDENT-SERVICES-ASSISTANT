import re
from typing import Tuple, Optional
from backend.database import get_db_connection

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system:",
    r"override\s+rules",
    r"reveal\s+all\s+student",
    r"change\s+answer_type",
    r"bypass\s+security"
]

PERSONAL_INTENT_PATTERNS = [
    r"\bmy\b",
    r"\bme\b",
    r"\bi\b",
    r"\bmy\s+gpa\b",
    r"\bmy\s+attendance\b",
    r"\bmy\s+fee\b",
    r"\bmy\s+transcript\b"
]

CROSS_STUDENT_PATTERNS = [
    r"other\s+students",
    r"all\s+students",
    r"list\s+everyone",
    r"friend\s+s\d+",
    r"student\s+sitting\s+next",
    r"classmate",
    r"everyone\s+with\s+backlogs"
]

def check_guardrails(
    question: str,
    header_student_id: Optional[str]
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Returns (is_refused, refusal_type, refusal_message)
    refusal_type: 'refused' | 'not_found' | None
    """
    question_lower = question.lower()

    # 1. Prompt Injection Detection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, question_lower):
            return True, 'refused', "Request refused due to safety policy violation."

    # 2. Cross-Student Privacy / Enumeration Attempt
    for pattern in CROSS_STUDENT_PATTERNS:
        if re.search(pattern, question_lower):
            return True, 'refused', "Request refused: Access to other students' personal records or aggregate student enumerations is prohibited."

    # 3. Personal Intent without Header
    is_personal_intent = any(re.search(pattern, question_lower) for pattern in PERSONAL_INTENT_PATTERNS)
    if is_personal_intent and not header_student_id:
        return True, 'refused', "Request refused: Personal student inquiries require a valid X-Student-Id authentication header."

    # 4. Header Validation against DB
    if header_student_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (header_student_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            # Neutral message (do not reveal if ID exists or not)
            return True, 'refused', "Request refused: Student authorization verification failed."

    return False, None, None
