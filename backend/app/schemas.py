"""Pydantic schemas shared by the future HTTP route and graph."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


AnswerType = Literal[
    "refused", "clarification_needed", "conflict_flagged", "calculated",
    "retrieved_fact", "not_found",
]


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str
    title: str | None = None
    section: str | None = None
    page: int | None = None
    version: str | None = None
    effective_from: str | None = None


class ToolInvocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any


class AppliedRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    value: str
    source_doc_id: str


class AskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    answer: str
    answer_type: AnswerType
    citations: list[Citation] = Field(default_factory=list)
    tools_invoked: list[ToolInvocation] = Field(default_factory=list)
    applied_rules: list[AppliedRule] = Field(default_factory=list)
    conflicts_detected: list[dict[str, Any]] = Field(default_factory=list)
    explanation: str
    as_of_date: str
