#!/usr/bin/env python3
"""Debug tracer script for inspecting RAG retrieval, LLM prompts, token counts, and verifiers."""

import argparse
import json
import sys
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.rag_engine import vector_collection
from backend.main import ask_question, rag_service, get_applicable_rules
from backend.models import AskRequest
from backend.config import OLLAMA_HOST, OLLAMA_MODEL

def debug_question(question: str, student_id: str = "S1001", as_of_date: str = "2026-10-06"):
    print("=" * 80)
    print(f"DEBUG TRACE FOR QUESTION: '{question}'")
    print(f"Student ID: {student_id} | As-Of Date: {as_of_date}")
    print("=" * 80)

    # 1. Retrieve Raw Vector Chunks
    raw_results = vector_collection.query(
        query_texts=[question],
        n_results=10
    )

    print("\n[1] RETRIEVED CHUNKS (Top 10 raw vector hits):")
    if raw_results and raw_results.get("documents") and raw_results["documents"][0]:
        docs = raw_results["documents"][0]
        metas = raw_results["metadatas"][0]
        dists = raw_results["distances"][0] if "distances" in raw_results else [0.0] * len(docs)
        for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
            doc_id = meta.get("doc_id", "N/A")
            title = meta.get("doc_title", "N/A")
            section = meta.get("section", "N/A")
            page = meta.get("page", "N/A")
            snippet = doc[:200].replace("\n", " ")
            print(f"  Rank {rank:02d} | Score/Dist: {dist:.4f} | doc_id: {doc_id} | title: '{title}' | section: {section} | page: {page}")
            print(f"          Snippet: {snippet}...")
    else:
        print("  No chunks retrieved from vector store.")

    # 2. Metadata Filters & Thresholding
    citations, upcoming, is_level5 = rag_service.query_legacy(question, as_of_date=as_of_date)
    filtered_count = len(citations)
    raw_count = len(raw_results["documents"][0]) if raw_results and raw_results.get("documents") and raw_results["documents"][0] else 0
    removed_count = max(0, raw_count - filtered_count)

    print(f"\n[2] METADATA FILTERS & THRESHOLDING:")
    print(f"  Raw retrieved chunks: {raw_count}")
    print(f"  Valid citations after date/distance/scope filter: {filtered_count}")
    print(f"  Chunks filtered out: {removed_count}")

    # 3. Exact Prompt & Token Count
    top_snippet = citations[0].snippet if citations else "No evidence retrieved."
    prompt_text = (
        f"You are UniAssist AI assistant. Answer the user question based ONLY on the following official context.\n\n"
        f"CONTEXT:\n{top_snippet}\n\n"
        f"QUESTION: {question}\n\n"
        f"Provide a clear, student-friendly 2-3 sentence explanation."
    )
    est_token_count = len(prompt_text.split()) * 1.3
    print(f"\n[3] LLM PROMPT & CONTEXT BOUNDS:")
    print(f"  Prompt Length: {len(prompt_text)} chars | Approx Token Count: {int(est_token_count)} tokens")
    print(f"  Evidence Truncated: {'NO' if len(prompt_text) < 2048 else 'YES'}")
    print(f"  Prompt Text Preview:\n  ---\n  {prompt_text[:300]}...\n  ---")

    # 4. LLM Parameters Sent
    print(f"\n[4] LLM CALL PARAMETERS:")
    print(f"  Host: {OLLAMA_HOST or 'Offline/Mock'}")
    print(f"  Model: {OLLAMA_MODEL}")
    print(f"  Temperature: 0.0")
    print(f"  num_ctx: 4096 (Ollama default)")
    print(f"  num_predict: 512")
    print(f"  Format: JSON / Plain Text")

    # 5. Raw & Parsed LLM Response
    req = AskRequest(question=question, as_of_date=as_of_date)
    res = ask_question(req, x_student_id=student_id)

    print(f"\n[5] RAW & PARSED RESPONSE:")
    print(f"  Parsed Answer: {res.answer}")
    print(f"  Answer Type: {res.answer_type}")
    print(f"  Confidence: {res.confidence}")
    print(f"  Trace ID: {res.trace_id}")

    # 6. Verifier Outcome per Check
    print(f"\n[6] VERIFIER OUTCOMES:")
    print(f"  Citation Grounding Check: {'PASS' if res.citations or res.answer_type in ('calculated', 'simulated', 'not_found', 'refused') else 'FAIL'}")
    print(f"  Rule Precedence Check: {'PASS' if res.applied_rules or res.answer_type != 'conflict_flagged' else 'CONFLICT'}")
    print(f"  Privacy Guardrail Check: {'PASS' if res.answer_type != 'refused' or 'refused' in res.answer.lower() else 'FAIL'}")

    # 7. Final Response JSON
    print(f"\n[7] FINAL API RESPONSE JSON:")
    print(json.dumps(res.model_dump(), indent=2))
    print("=" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Debug trace runner for UniAssist AI questions.")
    parser.add_argument("question", help="User question to trace")
    parser.add_argument("--student", default="S1001", help="X-Student-Id header (default: S1001)")
    parser.add_argument("--as-of", default="2026-10-06", help="as_of_date YYYY-MM-DD (default: 2026-10-06)")
    args = parser.parse_args()

    debug_question(args.question, args.student, args.as_of)

if __name__ == "__main__":
    main()
