"""Safe Annex D audit persistence; raw question text is never stored."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


_AUDIT_FIELDS = (
    "trace_id", "timestamp", "student_id", "question_category", "sources_retrieved",
    "precedence_decision", "tools_invoked", "answer_type", "model", "llm_calls",
    "tokens", "latency_ms",
)


def make_audit_record(state: dict[str, Any]) -> dict[str, Any]:
    """Create the allowed Annex D fields and deliberately omit the question."""
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "trace_id": state.get("trace_id", ""),
        "timestamp": timestamp,
        "student_id": state.get("student_id"),
        "question_category": state.get("category", "other"),
        "sources_retrieved": state.get("sources_retrieved", []),
        "precedence_decision": state.get("precedence"),
        "tools_invoked": [
            {"tool": item.get("tool"), "status": item.get("status"), "ms": item.get("ms")}
            for item in state.get("tool_results", [])
        ],
        "answer_type": state.get("answer_type", "not_found"),
        "model": state.get("model", ""),
        "llm_calls": state.get("llm_calls", 0),
        "tokens": state.get("tokens", 0),
        "latency_ms": state.get("latency_ms", 0.0),
    }
    return {key: record[key] for key in _AUDIT_FIELDS}


def write_audit_record(conn: Any, record: dict[str, Any]) -> None:
    """Persist one whitelisted record into the existing audit_log table."""
    safe = {key: record.get(key) for key in _AUDIT_FIELDS}
    conn.execute(
        "INSERT OR REPLACE INTO audit_log (trace_id, student_id, timestamp, record_json) VALUES (?, ?, ?, ?)",
        (safe["trace_id"], safe["student_id"], safe["timestamp"], json.dumps(safe, ensure_ascii=False, default=str)),
    )
    conn.commit()
