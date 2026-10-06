"""One finite LangGraph pipeline for safe student-service requests."""
from __future__ import annotations

import re
import uuid
from collections import defaultdict
from typing import Any

from langgraph.graph import END, StateGraph

from app.audit import make_audit_record, write_audit_record
from app.llm.client import LLMClient, LLMStructuredError
from app.llm.prompts import Classification, ToolPlan, classification_messages, explanation_messages, tool_plan_messages
from app.precedence import Candidate, Context, PrecedenceDecision, resolve_candidates
from app.rag_interface import Chunk, get_default_retriever
from app.safety import RequestContext, contains_prompt_injection, requests_another_student, requires_student_identity
from app.schemas import AskResponse
from app.tools import TOOL_REGISTRY
from app.tools.selection import select_tool
from app.tools.student import get_profile
from app.graph.state import GraphState


NOT_FOUND = "I could not find this information in the authorised university sources."
_COURSE = re.compile(r"\b([A-Z]{2,3}\d{3})\b", re.IGNORECASE)
_NUMBER = re.compile(r"(?<![A-Za-z])(?:\d+(?:\.\d+)?%?|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)(?![A-Za-z])", re.I)
_PER_COURSE = {
    "get_attendance", "check_exam_eligibility", "check_supplementary_eligibility",
    "whatif_supplementary_placement",
}


def _bump(state: GraphState, result: Any) -> dict[str, Any]:
    return {
        "llm_calls": state.get("llm_calls", 0) + int(getattr(result, "llm_calls", 0)),
        "tokens": state.get("tokens", 0) + int(getattr(result, "prompt_tokens", 0)) + int(getattr(result, "completion_tokens", 0)),
        "latency_ms": state.get("latency_ms", 0.0) + float(getattr(result, "latency_ms", 0.0)),
        "model": getattr(result, "model", state.get("model", "")),
    }


def _fallback_classification(question: str) -> dict[str, Any]:
    plan = select_tool(question)
    tool = plan.get("tool", "")
    text = question.casefold()
    if any(part in text for part in ("what if", "if i pass", "if i clear", "suppose i")) and ("placement" in text or "eligible" in text):
        category = "multi_step"
    elif tool in {"check_exam_eligibility", "check_supplementary_eligibility", "check_placement_eligibility", "whatif_supplementary_placement"}:
        category = "personal_eligibility"
    elif tool in {"get_profile", "get_attendance", "get_attendance_all", "get_results", "get_backlogs"} and re.search(r"\b(my|me|mine|i)\b", text):
        category = "personal_data"
    elif any(word in text for word in ("apply", "application", "how to", "procedure")):
        category = "procedure"
    elif any(word in text for word in ("policy", "regulation", "minimum", "requirement", "threshold", "attendance")):
        category = "policy_fact"
    else:
        category = "other"
    match = _COURSE.search(question)
    return {
        "category": category,
        "course_code": match.group(1).upper() if match else None,
        "needs_identity": requires_student_identity(question, category),
    }


def _schema_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return {}


def _rule_source(conn: Any, doc_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM source_register WHERE doc_id = ?", (doc_id,)).fetchone()
    return dict(row) if row else {}


def _token_items(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(part).strip() for part in value if str(part).strip()]
    return [part.strip() for part in str(value).replace(";", ",").split(",") if part.strip()]


def _candidate_context(candidates: list[Candidate], state: GraphState) -> Context:
    profile = state.get("profile") or {}
    programme = profile.get("programme") or getattr(state["context"], "programme", None)
    batch = profile.get("batch_year") or getattr(state["context"], "batch_year", None)
    if programme is not None and batch is not None:
        return Context(state["as_of_date"], str(programme), batch)
    # Public policy questions have no student context. Use the narrowest
    # retrieved scope as the context for this question's policy candidates.
    ranked = sorted(
        candidates,
        key=lambda item: (
            int(str(item.scope_programmes).strip().casefold() != "all")
            + int(str(item.scope_batches).strip().casefold() != "all"),
            -int(item.authority_level),
        ), reverse=True,
    )
    chosen = ranked[0]
    programme_tokens = _token_items(chosen.scope_programmes)
    programme = next((item for item in programme_tokens if item.casefold() != "all"), "ALL")
    batch_tokens = _token_items(chosen.scope_batches)
    batch = 0
    if batch_tokens and batch_tokens[0].casefold() != "all":
        match = re.match(r"(\d{4})", batch_tokens[0])
        if match:
            batch = int(match.group(1))
    return Context(state["as_of_date"], programme, batch)


def _candidate_from_chunk(chunk: Chunk, index: int, conn: Any) -> Candidate | None:
    metadata = dict(chunk.metadata or {})
    source = _rule_source(conn, chunk.doc_id)
    authority = metadata.get("authority_level", source.get("authority_level"))
    effective_from = chunk.effective_from or metadata.get("effective_from") or source.get("effective_from")
    if authority is None or not effective_from:
        return None
    value = metadata.get("value", metadata.get("parameter_value", chunk.text))
    return Candidate(
        key=f"{chunk.doc_id}#{chunk.section or 'unknown'}:{index}",
        doc_id=chunk.doc_id,
        section=str(metadata.get("source_section") or chunk.section or ""),
        authority_level=int(authority),
        effective_from=str(effective_from),
        effective_to=metadata.get("effective_to", source.get("effective_to", "")) or "",
        supersedes=metadata.get("supersedes", source.get("supersedes", "")) or "",
        scope_programmes=metadata.get("scope_programmes", source.get("scope_programmes", "ALL")) or "ALL",
        scope_batches=metadata.get("scope_batches", source.get("scope_batches", "ALL")) or "ALL",
        value=value,
    )


def _candidate_record(candidate: Candidate) -> dict[str, Any]:
    return {
        "key": candidate.key, "doc_id": candidate.doc_id, "section": candidate.section,
        "authority_level": candidate.authority_level, "effective_from": str(candidate.effective_from),
        "value": candidate.value,
    }


def _source_citation(source: dict[str, Any], *, section: str | None = None, page: int | None = None) -> dict[str, Any]:
    return {
        "doc_id": source.get("doc_id", ""),
        "title": source.get("title"),
        "section": section,
        "page": page,
        "version": source.get("version"),
        "effective_from": source.get("effective_from"),
    }


def _rule_metadata(conn: Any, rule_ids: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    applied, citations, upcoming = [], [], []
    for rule_id in dict.fromkeys(rule_ids):
        row = conn.execute(
            "SELECT r.rule_id, r.value, r.effective_from, r.effective_to, r.source_doc_id, r.source_section, "
            "s.doc_id, s.title, s.version, s.effective_from AS source_effective_from "
            "FROM rule_registry r JOIN source_register s ON s.doc_id = r.source_doc_id WHERE r.rule_id = ?",
            (rule_id,),
        ).fetchone()
        if not row:
            continue
        data = dict(row)
        applied.append({"rule_id": data["rule_id"], "value": str(data["value"]), "source_doc_id": data["source_doc_id"]})
        citations.append(_source_citation({
            "doc_id": data["doc_id"], "title": data["title"], "version": data["version"],
            "effective_from": data["source_effective_from"],
        }, section=data["source_section"]))
    return applied, citations, upcoming


def _all_numeric_tokens(text: str) -> set[str]:
    text = re.sub(r"\b[A-Z]{2,3}\d{3}\b", " ", text or "", flags=re.IGNORECASE)
    return {match.group(0).casefold().rstrip("%") for match in _NUMBER.finditer(text)}


def _supported_numbers(state: GraphState, explanation: str) -> bool:
    allowed: set[str] = {token.casefold() for token in _all_numeric_tokens(state.get("as_of_date", ""))}
    for result in state.get("tool_results", []):
        allowed.update(_all_numeric_tokens(str(result.get("output", ""))))
        allowed.update(_all_numeric_tokens(str(result.get("input", ""))))
    for rule in state.get("applied_rules", []):
        allowed.update(_all_numeric_tokens(str(rule)))
    for chunk in [*state.get("winning_chunks", []), *state.get("upcoming_chunks", [])]:
        allowed.update(_all_numeric_tokens(chunk.text))
        allowed.update(_all_numeric_tokens(str(chunk.metadata)))
        if chunk.page is not None:
            allowed.update(_all_numeric_tokens(str(chunk.page)))
    for citation in state.get("citations", []):
        allowed.update(_all_numeric_tokens(str(citation)))
    return _all_numeric_tokens(explanation).issubset(allowed)


def _tool_sentence(result: dict[str, Any]) -> str:
    tool = result.get("tool", "")
    output = result.get("output")
    if result.get("status") != "ok":
        return ""
    if tool == "get_profile":
        return "Your profile: " + ", ".join(f"{key} {value}" for key, value in output.items())
    if tool == "get_attendance":
        return f"Attendance in {output['course_code']} is {output['attendance_pct']}% ({output['classes_attended']} of {output['classes_held']} classes)."
    if tool == "get_attendance_all":
        return "Attendance records: " + "; ".join(f"{item['course_code']} {item['attendance_pct']}% ({item['classes_attended']}/{item['classes_held']})" for item in output)
    if tool == "check_exam_eligibility":
        return f"Exam eligibility for {output['course_code']}: {output['eligibility']}. Attendance {output['attendance_pct']}%; minimum {output['min_threshold']}%, floor {output['floor_threshold']}%. {output['reason']}"
    if tool == "check_supplementary_eligibility":
        return f"Supplementary eligibility for {output['course_code']}: {output['eligible']}. {output['reason']}"
    if tool == "check_placement_eligibility":
        return f"Placement eligibility: {output['eligible']}. CGPA {output['cgpa']}; active backlogs {output['active_backlogs']}. {output['reason']}"
    if tool == "whatif_supplementary_placement":
        return f"Current placement eligibility: {output['current_placement_eligible']}; after the stated supplementary assumption: {output['whatif_placement_eligible']}. CGPA remains {output['current_cgpa']}."
    if tool == "get_backlogs":
        return "Pending courses: " + (", ".join(item["course_code"] for item in output) if output else "none")
    if tool == "get_results":
        return "Results: " + "; ".join(f"{item['course_code']} {item['exam_session']} {item['exam_type']} {item['result']} ({item['total_marks']}/{item['max_marks']})" for item in output)
    if tool == "list_courses":
        return "Available courses: " + ", ".join(item["course_code"] for item in output)
    return ""


def _deterministic_explanation(state: GraphState) -> str:
    if state.get("answer_type") == "refused":
        return state.get("answer", "I can only help with the authenticated student's own information.")
    if state.get("answer_type") == "clarification_needed":
        courses = []
        for result in state.get("tool_results", []):
            if result.get("tool") == "list_courses" and result.get("status") == "ok":
                courses = result.get("output", [])
        suffix = " Available courses: " + ", ".join(row["course_code"] for row in courses) if courses else ""
        return "Please specify the course you mean." + suffix
    if state.get("answer_type") == "conflict_flagged":
        return "Applicable sources conflict. Please contact the issuing university office for clarification."
    tool_text = [_tool_sentence(item) for item in state.get("tool_results", [])]
    tool_text = [text for text in tool_text if text]
    policy_text = []
    for chunk in state.get("winning_chunks", []):
        title = chunk.title or chunk.doc_id
        section = f", section {chunk.section}" if chunk.section else ""
        policy_text.append(f"According to {title}{section}: {chunk.text}")
    combined = " ".join([*tool_text, *policy_text]).strip()
    return combined or NOT_FOUND


def build_graph(*, llm_client: Any = None, retriever: Any = None):
    """Build the single fixed finite StateGraph; dependencies are injectable for tests."""
    llm = llm_client or LLMClient()
    rag = retriever or get_default_retriever()

    def safety_gate(state: GraphState):
        if requests_another_student(state["question"], state.get("student_id")):
            return {"terminal": True, "answer_type": "refused", "answer": "I can only provide personal information for the authenticated student."}
        if contains_prompt_injection(state["question"]):
            return {"terminal": True, "answer_type": "refused", "answer": "I cannot follow requests to override university safety or policy rules."}
        return {"terminal": False}

    def classify(state: GraphState):
        if state.get("terminal"):
            return {}
        try:
            result = llm.chat(classification_messages(state["question"]), Classification)
            payload = _schema_payload(result.parsed)
            fallback = _fallback_classification(state["question"])
            category = payload.get("category", fallback["category"])
            if category == "other" and fallback["category"] in {"personal_data", "personal_eligibility", "multi_step"}:
                category = fallback["category"]
            course_code = payload.get("course_code") or fallback.get("course_code")
            if course_code and not _COURSE.fullmatch(str(course_code)):
                course_code = fallback.get("course_code")
            needs_identity = bool(payload.get("needs_identity")) or requires_student_identity(state["question"], category)
            return {**_bump(state, result), "category": category, "course_code": course_code,
                    "needs_identity": needs_identity}
        except Exception:
            return {**_fallback_classification(state["question"]), "model": getattr(llm, "model", "") or "mock"}

    def identity_check(state: GraphState):
        if state.get("terminal"):
            return {}
        if state.get("needs_identity") and not state.get("student_id"):
            return {"terminal": True, "answer_type": "refused",
                    "answer": "Please provide your X-Student-Id header to access your own student information."}
        return {}

    def route(state: GraphState):
        if state.get("terminal"):
            return {"needs_retrieval": False, "needs_tools": False}
        category = state.get("category", "other")
        return {
            "needs_retrieval": category in {"policy_fact", "procedure", "personal_eligibility", "multi_step", "other"},
            "needs_tools": category in {"personal_data", "personal_eligibility", "multi_step"},
        }

    def retrieve(state: GraphState):
        if state.get("terminal") or not state.get("needs_retrieval"):
            return {"chunks": [], "sources_retrieved": []}
        context = state["context"]
        filters: dict[str, Any] = {"as_of_date": state["as_of_date"]}
        results = list(state.get("tool_results", []))
        profile = state.get("profile")
        # Eligibility needs scope filters. Obtain the profile through its existing
        # deterministic tool, keeping identity sourced exclusively from context.
        if state.get("category") in {"personal_eligibility", "multi_step"} and state.get("student_id"):
            profile_result = get_profile(context)
            results.append(profile_result)
            if profile_result.get("status") == "ok":
                profile = profile_result["output"]
                filters.update({"programme": profile.get("programme"), "batch_year": profile.get("batch_year")})
        try:
            chunks = list(rag.retrieve(state["question"], filters) or [])
        except Exception:
            chunks = []
        return {
            "chunks": chunks,
            "tool_results": results,
            "profile": profile,
            "sources_retrieved": [
                {"doc_id": chunk.doc_id, "section": chunk.section, "score": chunk.score}
                for chunk in chunks if not chunk.metadata.get("upcoming")
            ],
        }

    def run_tools(state: GraphState):
        if state.get("terminal") or not state.get("needs_tools"):
            return {}
        results = list(state.get("tool_results", []))
        try:
            plan_result = llm.chat(tool_plan_messages(state["question"], state.get("category")), ToolPlan)
            plan_data = _schema_payload(plan_result.parsed)
            metrics = _bump(state, plan_result)
        except Exception:
            plan_data = select_tool(state["question"])
            metrics = {}
        if "input" in plan_data:
            plan_data = {"tool": plan_data.get("tool"), **plan_data.get("input", {})}
        tool_name = plan_data.get("tool")
        if tool_name not in TOOL_REGISTRY:
            fallback = select_tool(state["question"])
            tool_name = fallback["tool"]
            plan_data = {"tool": tool_name, **fallback.get("input", {})}
        requested_course = state.get("course_code")
        question_match = _COURSE.search(state["question"])
        explicit_course = question_match.group(1).upper() if question_match else None
        suggested_course = plan_data.get("course_code")
        course_code = requested_course or explicit_course
        if suggested_course and str(suggested_course).upper() == explicit_course:
            course_code = str(suggested_course).upper()
        args: dict[str, Any] = {}
        clarification_needed = False
        if tool_name in _PER_COURSE:
            if course_code:
                args["course_code"] = course_code
            else:
                tool_name = "list_courses"
                clarification_needed = True
        elif tool_name == "get_results" and course_code:
            args["course_code"] = course_code
        elif tool_name == "list_courses" and isinstance(plan_data.get("semester"), int):
            args["semester"] = plan_data["semester"]
        # Only explicitly supported non-identity arguments can cross this boundary.
        if "student_id" in args:
            return {**metrics, "answer_type": "refused", "answer": "Student identity is supplied only by request context."}
        try:
            tool_result = TOOL_REGISTRY[tool_name](state["context"], **args)
        except Exception:
            tool_result = {"tool": tool_name, "input": args, "output": {"message": "The requested university record could not be retrieved."}, "status": "error", "ms": 0, "rule_ids": [], "citations_meta": []}
        results.append(tool_result)
        return {**metrics, "tool_plan": {"tool": tool_name, **args}, "tool_results": results,
                "clarification_needed": clarification_needed}

    def precedence(state: GraphState):
        if state.get("terminal") or not state.get("needs_retrieval"):
            return {"winning_chunks": [], "upcoming_chunks": [], "precedence": None, "conflicts": []}
        conn = state["context"].conn
        chunks = state.get("chunks", [])
        upcoming_chunks = [chunk for chunk in chunks if chunk.metadata.get("upcoming")]
        grouped: dict[str, list[tuple[Candidate, Chunk]]] = defaultdict(list)
        for index, chunk in enumerate(chunks):
            if chunk.metadata.get("upcoming"):
                continue
            candidate = _candidate_from_chunk(chunk, index, conn)
            if candidate is None or candidate.authority_level == 5:
                continue
            group = str(chunk.metadata.get("parameter") or chunk.section or "same-question").casefold()
            grouped[group].append((candidate, chunk))
        decisions, winners, conflict_rows = [], [], []
        for group, items in sorted(grouped.items()):
            candidates = [item[0] for item in items]
            context = _candidate_context(candidates, state)
            decision = resolve_candidates(candidates, context)
            decision_row = {
                "group": group,
                "winner": _candidate_record(decision.winner) if decision.winner else None,
                "losers": decision.losers,
                "upcoming": [_candidate_record(item) for item in decision.upcoming],
                "conflict": decision.conflict,
                "conflict_keys": decision.conflict_keys,
                "decided_at_step": decision.decided_at_step,
                "explanation": decision.explanation,
            }
            decisions.append(decision_row)
            if decision.conflict:
                conflict_rows.append({
                    "group": group,
                    "keys": decision.conflict_keys,
                    "sources": [candidate.doc_id for candidate in candidates if candidate.key in decision.conflict_keys],
                    "explanation": decision.explanation,
                })
            elif decision.winner:
                winner_pair = next((pair for pair in items if pair[0].key == decision.winner.key), None)
                if winner_pair:
                    winners.append(winner_pair[1])
            by_key = {candidate.key: chunk for candidate, chunk in items}
            upcoming_chunks.extend(by_key[candidate.key] for candidate in decision.upcoming if candidate.key in by_key)
        return {
            "precedence": {"groups": decisions},
            "winning_chunks": winners,
            "upcoming_chunks": upcoming_chunks,
            "conflicts": conflict_rows,
        }

    def compose(state: GraphState):
        if state.get("terminal"):
            return {"explanation": state.get("answer", NOT_FOUND)}
        if state.get("conflicts"):
            answer_type = "conflict_flagged"
            state_answer = "Applicable sources conflict. Please contact the issuing university office for clarification."
            return {"answer_type": answer_type, "answer": state_answer, "explanation": state_answer}
        if state.get("clarification_needed"):
            explanation = _deterministic_explanation({**state, "answer_type": "clarification_needed"})
            return {"answer_type": "clarification_needed", "answer": explanation, "explanation": explanation}
        successful_task_tools = [
            item for item in state.get("tool_results", [])
            if item.get("status") == "ok" and item.get("tool") != "get_profile"
        ]
        if state.get("needs_tools") and not successful_task_tools:
            return {"answer_type": "not_found", "answer": NOT_FOUND, "explanation": NOT_FOUND}
        if successful_task_tools:
            answer_type = "calculated"
        elif state.get("winning_chunks"):
            answer_type = "retrieved_fact"
        else:
            return {"answer_type": "not_found", "answer": NOT_FOUND, "explanation": NOT_FOUND}
        state_for_compose = {**state, "answer_type": answer_type}
        if getattr(llm, "mock", False):
            explanation = _deterministic_explanation(state_for_compose)
            return {"answer_type": answer_type, "answer": explanation, "explanation": explanation}
        try:
            result = llm.chat(explanation_messages(
                facts={"as_of_date": state["as_of_date"]},
                tool_results=state.get("tool_results", []),
                winning_document_chunks=[{
                    "doc_id": chunk.doc_id, "title": chunk.title,
                    "section": chunk.section, "page": chunk.page,
                    "version": chunk.version, "effective_from": chunk.effective_from,
                    "text": chunk.text, "metadata": chunk.metadata,
                } for chunk in state.get("winning_chunks", [])],
                upcoming_changes=[{
                    "doc_id": chunk.doc_id, "effective_from": chunk.effective_from,
                    "text": chunk.text,
                } for chunk in state.get("upcoming_chunks", [])],
                assumptions=[assumption for item in successful_task_tools for assumption in item.get("output", {}).get("assumptions", [])],
            ))
            explanation = result.text.strip()
            metrics = _bump(state, result)
        except Exception:
            explanation = _deterministic_explanation(state_for_compose)
            metrics = {}
        return {**metrics, "answer_type": answer_type, "answer": explanation, "explanation": explanation}

    def verify(state: GraphState):
        citations: list[dict[str, Any]] = []
        seen = set()
        for chunk in state.get("winning_chunks", []):
            if not chunk.doc_id or chunk.metadata.get("upcoming"):
                continue
            citation = {
                "doc_id": chunk.doc_id,
                "title": chunk.title or chunk.metadata.get("doc_title"),
                "section": chunk.section,
                "page": chunk.page,
                "version": chunk.version,
                "effective_from": chunk.effective_from,
            }
            key = (citation["doc_id"], citation["section"], citation["page"])
            if key not in seen:
                seen.add(key)
                citations.append(citation)
        rule_ids = [
            rule_id
            for result in state.get("tool_results", []) if result.get("status") == "ok"
            for rule_id in result.get("rule_ids", [])
        ]
        applied_rules, rule_citations, _ = _rule_metadata(state["context"].conn, rule_ids)
        for citation in rule_citations:
            key = (citation["doc_id"], citation["section"], citation["page"])
            if citation["doc_id"] and key not in seen:
                seen.add(key)
                citations.append(citation)
        citations = [citation for citation in citations if citation.get("doc_id") and (citation.get("title") or citation.get("doc_id"))]
        allowed_result = {"citations": citations, "applied_rules": applied_rules}
        answer = state.get("answer", NOT_FOUND)
        explanation = state.get("explanation", answer)
        if state.get("answer_type") != "not_found" and not _supported_numbers({**state, **allowed_result}, explanation):
            fallback = _deterministic_explanation(state)
            if _supported_numbers({**state, **allowed_result}, fallback):
                answer = explanation = fallback
            else:
                answer = explanation = "I could not verify a safe explanation from the available university records."
        return {"citations": citations, "applied_rules": applied_rules, "answer": answer, "explanation": explanation}

    def finalize(state: GraphState):
        answer_type = state.get("answer_type", "not_found")
        answer = state.get("answer", NOT_FOUND)
        if answer_type == "not_found":
            answer = NOT_FOUND
        return {"answer": answer, "explanation": state.get("explanation") or answer}

    def audit(state: GraphState):
        try:
            record = make_audit_record(state)
            write_audit_record(state["context"].conn, record)
        except Exception:
            pass
        return {}

    graph = StateGraph(GraphState)
    graph.add_node("safety_gate", safety_gate)
    graph.add_node("classify", classify)
    graph.add_node("identity_check", identity_check)
    graph.add_node("route", route)
    graph.add_node("retrieve", retrieve)
    graph.add_node("run_tools", run_tools)
    graph.add_node("precedence", precedence)
    graph.add_node("compose", compose)
    graph.add_node("verify", verify)
    graph.add_node("finalize", finalize)
    graph.add_node("audit", audit)
    graph.set_entry_point("safety_gate")
    graph.add_edge("safety_gate", "classify")
    graph.add_edge("classify", "identity_check")
    graph.add_edge("identity_check", "route")
    graph.add_edge("route", "retrieve")
    graph.add_edge("retrieve", "run_tools")
    graph.add_edge("run_tools", "precedence")
    graph.add_edge("precedence", "compose")
    graph.add_edge("compose", "verify")
    graph.add_edge("verify", "finalize")
    graph.add_edge("finalize", "audit")
    graph.add_edge("audit", END)
    return graph.compile()


def run_graph(question: str, ctx: RequestContext, *, llm_client: Any = None, retriever: Any = None) -> AskResponse:
    """Run the fixed graph and return a validated response without exposing failures."""
    trace_id = f"TRC-{uuid.uuid4().hex[:12]}"
    as_of_date = ctx.as_of_date.isoformat() if hasattr(ctx.as_of_date, "isoformat") else str(ctx.as_of_date)
    initial: GraphState = {
        "question": question,
        "context": ctx,
        "student_id": ctx.student_id,
        "as_of_date": as_of_date,
        "category": "other",
        "course_code": None,
        "needs_identity": False,
        "needs_retrieval": False,
        "needs_tools": False,
        "clarification_needed": False,
        "terminal": False,
        "chunks": [],
        "winning_chunks": [],
        "upcoming_chunks": [],
        "tool_results": [],
        "precedence": None,
        "applied_rules": [],
        "citations": [],
        "conflicts": [],
        "sources_retrieved": [],
        "answer": "",
        "answer_type": "not_found",
        "explanation": "",
        "trace_id": trace_id,
        "model": getattr(getattr(llm_client, "config", None), "OLLAMA_MODEL", ""),
        "llm_calls": 0,
        "tokens": 0,
        "latency_ms": 0.0,
    }
    try:
        result = build_graph(llm_client=llm_client, retriever=retriever).invoke(initial)
        return AskResponse(
            trace_id=trace_id, answer=result["answer"], answer_type=result["answer_type"],
            citations=result.get("citations", []), tools_invoked=[
                {"tool": item.get("tool", ""), "input": item.get("input", {}), "output": item.get("output")}
                for item in result.get("tool_results", [])
            ], applied_rules=result.get("applied_rules", []), conflicts_detected=result.get("conflicts", []),
            explanation=result.get("explanation", result["answer"]), as_of_date=as_of_date,
        )
    except Exception:
        answer = NOT_FOUND
        try:
            fallback = {**initial, "answer": answer, "explanation": answer, "answer_type": "not_found"}
            write_audit_record(ctx.conn, make_audit_record(fallback))
        except Exception:
            pass
        return AskResponse(
            trace_id=trace_id, answer=answer, answer_type="not_found", citations=[],
            tools_invoked=[], applied_rules=[], conflicts_detected=[],
            explanation=answer, as_of_date=as_of_date,
        )
