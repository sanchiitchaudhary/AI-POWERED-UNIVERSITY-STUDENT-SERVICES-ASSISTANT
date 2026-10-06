from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class Citation(BaseModel):
    doc_id: str
    doc_title: str
    page: int
    section: Optional[str] = None
    authority_level: int = 3
    effective_from: Optional[str] = None
    snippet: str

class AppliedRule(BaseModel):
    rule_code: str
    parameter: str
    operator: str
    value: str
    source_doc_id: str

class ToolInvocation(BaseModel):
    tool: str
    input: Dict[str, Any]
    output: Dict[str, Any]

class UpcomingChange(BaseModel):
    doc_id: str
    effective_from: str
    description: str

class AskRequest(BaseModel):
    question: str
    as_of_date: Optional[str] = None
    student_id_override: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    answer_type: Literal[
        'calculated',
        'direct_retrieval',
        'simulated',
        'clarification_needed',
        'conflict_flagged',
        'not_found',
        'refused'
    ]
    confidence: float = Field(..., ge=0.0, le=1.0)
    citations: List[Citation] = []
    applied_rules: List[AppliedRule] = []
    tools_invoked: List[ToolInvocation] = []
    upcoming_changes: Optional[List[UpcomingChange]] = []
    retrieved_fact: Optional[str] = None
    trace_id: str

class IngestResponse(BaseModel):
    doc_id: str
    chunks: int
    indexed: bool
    status: str

class RuleCreateRequest(BaseModel):
    rule_code: str
    parameter: str
    operator: str
    value: str
    effective_from: str = "2026-01-01"
    scope_programmes: str = "ALL"
    scope_batches: str = "ALL"
    authority_level: int = 3
    source_doc_id: str

class RuleResponse(BaseModel):
    id: int
    rule_code: str
    parameter: str
    operator: str
    value: str
    effective_from: str
    scope_programmes: str
    scope_batches: str
    authority_level: int
    source_doc_id: str
    status: str
