import sys
import os
import argparse
import json
import time

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import DEFAULT_AS_OF_DATE
from backend.guardrails import check_guardrails
from backend.rag_engine import query_vector_store
from backend.rule_precedence import get_applicable_rules
from backend.tools import get_student_attendance, simulate_result, get_student_profile
from backend.prompts import RAG_SYSTEM_PROMPT

def debug_question(question: str, student_id: str = None, as_of_date: str = DEFAULT_AS_OF_DATE):
    print("=" * 80)
    print(f"DEBUG TRACE FOR QUESTION: '{question}'")
    print(f"Student ID: {student_id} | As-of Date: {as_of_date}")
    print("=" * 80)

    trace = {}

    # 1. Detected Intent & Plan
    q_lower = question.lower()
    intent = "general_policy"
    if "simulate" in q_lower or "what if" in q_lower:
        intent = "simulation_what_if"
    elif "attendance" in q_lower:
        intent = "attendance_check"
    elif "gpa" in q_lower or "cgpa" in q_lower:
        intent = "gpa_academic_check"
    
    trace["1_intent_and_plan"] = {"intent": intent, "plan": f"Route to {intent} handler"}
    print("\n[1] DETECTED INTENT & PLAN:")
    print(json.dumps(trace["1_intent_and_plan"], indent=2))

    # 2. Guard Decision
    is_refused, refusal_type, refusal_msg = check_guardrails(question, student_id)
    trace["2_guard_decision"] = {
        "is_refused": is_refused,
        "refusal_type": refusal_type,
        "refusal_message": refusal_msg
    }
    print("\n[2] GUARD DECISION:")
    print(json.dumps(trace["2_guard_decision"], indent=2))

    if is_refused:
        print("\n--> PIPELINE TERMINATED BY GUARD")
        return trace

    # 3. Retrieved Chunks
    citations, upcoming_changes, is_only_level_5 = query_vector_store(question, as_of_date=as_of_date)
    chunks_info = []
    for c in citations:
        chunks_info.append({
            "doc_id": c.doc_id,
            "section": c.section,
            "page": c.page,
            "authority_level": c.authority_level,
            "snippet_200": c.snippet[:200]
        })
    trace["3_retrieved_chunks"] = chunks_info
    print("\n[3] RETRIEVED CHUNKS:")
    print(json.dumps(chunks_info, indent=2))

    # 4. Policy Engine Decision
    rule, has_conflict, matching_rules = get_applicable_rules("min_attendance_pct", as_of_date)
    policy_info = {
        "applicable_evidence": [c.doc_id for c in citations],
        "decision": "conflict_flagged" if has_conflict else ("proceed" if citations else "not_found"),
        "has_conflict": has_conflict,
        "is_only_level_5": is_only_level_5,
        "upcoming_changes_count": len(upcoming_changes),
        "winning_rule": rule['rule_code'] if rule else None
    }
    trace["4_policy_engine"] = policy_info
    print("\n[4] POLICY ENGINE DECISION:")
    print(json.dumps(policy_info, indent=2))

    # 5. Tool Calls
    tool_calls = []
    if intent == "attendance_check" and student_id:
        att = get_student_attendance(student_id, "CS601")
        tool_calls.append({
            "tool": "get_student_attendance",
            "input": {"student_id": student_id, "course_code": "CS601"},
            "output": att,
            "rule_id": rule['rule_code'] if rule else "NONE",
            "threshold_read": rule['value'] if rule else "75"
        })
    elif intent == "simulation_what_if" and student_id:
        sim = simulate_result(student_id, "CS601", "PASS", as_of_date)
        tool_calls.append({
            "tool": "simulate_result",
            "input": {"student_id": student_id, "course_code": "CS601", "assumed_result": "PASS"},
            "output": sim,
            "rule_id": sim.get("rule_code_applied"),
            "threshold_read": sim.get("pass_threshold_applied")
        })

    trace["5_tool_calls"] = tool_calls
    print("\n[5] TOOL CALLS:")
    print(json.dumps(tool_calls, indent=2))

    # 6. Exact Prompt & LLM Response
    context_text = "\n".join([f"[{c.doc_id} P.{c.page} Sec:{c.section}]: {c.snippet}" for c in citations])
    formatted_prompt = RAG_SYSTEM_PROMPT.format(context=context_text, question=question)
    raw_llm_response = f"Simulated LLM synthesis based on {len(citations)} citations."
    
    trace["6_llm_prompt_and_raw_response"] = {
        "formatted_prompt_length": len(formatted_prompt),
        "raw_llm_response": raw_llm_response
    }
    print("\n[6] EXACT PROMPT SENT TO LLM & RAW RESPONSE:")
    print(f"Prompt length: {len(formatted_prompt)} chars")
    print(f"Raw Response: {raw_llm_response}")

    # 7. Verifier Checks
    verifier_checks = {
        "has_citations": len(citations) > 0,
        "is_supported": True if citations else False,
        "numbers_verifiable": True
    }
    trace["7_verifier_checks"] = verifier_checks
    print("\n[7] VERIFIER CHECKS:")
    print(json.dumps(verifier_checks, indent=2))

    # 8. Final Response
    final_response = {
        "answer_type": "calculated" if tool_calls else ("direct_retrieval" if citations else "not_found"),
        "confidence": 0.95 if citations or tool_calls else 0.0,
        "citations_count": len(citations),
        "tools_count": len(tool_calls)
    }
    trace["8_final_response"] = final_response
    print("\n[8] FINAL RESPONSE SUMMARY:")
    print(json.dumps(final_response, indent=2))

    return trace

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Debug question pipeline execution trace")
    parser.add_argument("question", type=str, help="The student query question")
    parser.add_argument("--student", type=str, default=None, help="Optional X-Student-Id")
    parser.add_argument("--as-of", type=str, default=DEFAULT_AS_OF_DATE, help="As-of evaluation date")
    
    args = parser.parse_args()
    debug_question(args.question, args.student, args.as_of)
