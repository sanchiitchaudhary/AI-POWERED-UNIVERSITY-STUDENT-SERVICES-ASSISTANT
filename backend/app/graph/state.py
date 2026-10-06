"""Typed state passed through the graph's fixed finite sequence."""
from __future__ import annotations

from typing import Any, TypedDict

from app.rag_interface import Chunk
from app.safety import RequestContext


class GraphState(TypedDict, total=False):
    question: str
    context: RequestContext
    student_id: str | None
    as_of_date: str
    category: str
    course_code: str | None
    needs_identity: bool
    needs_retrieval: bool
    needs_tools: bool
    clarification_needed: bool
    terminal: bool
    tool_plan: dict[str, Any]
    profile: dict[str, Any]
    chunks: list[Chunk]
    winning_chunks: list[Chunk]
    upcoming_chunks: list[Chunk]
    tool_results: list[dict[str, Any]]
    precedence: dict[str, Any] | None
    applied_rules: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    sources_retrieved: list[dict[str, Any]]
    answer: str
    answer_type: str
    explanation: str
    trace_id: str
    model: str
    llm_calls: int
    tokens: int
    latency_ms: float
