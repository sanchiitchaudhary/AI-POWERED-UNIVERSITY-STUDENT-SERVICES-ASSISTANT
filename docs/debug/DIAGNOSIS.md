# UniAssist AI - System Diagnosis Report (`docs/debug/DIAGNOSIS.md`)

**Date**: 2026-10-06  
**Target System**: UniAssist AI Policy Engine (HCL Hackathon Edition)

---

## 1. Problem 3 (Short / Truncated Answers) Diagnosis

- **Output Token Limit (`num_predict` / `max_tokens`)**:
  - `num_predict` was previously unset in some Ollama client payloads, relying on default short completion windows.
- **Context Window (`num_ctx`)**:
  - Ollama defaults `num_ctx` to 2048/4096 tokens. When prompt text was formatted without chunk metadata, long document snippets ran close to context boundaries.
- **Prompt Wording & String Slicing**:
  - Direct retrieval answers in `backend/main.py` were using direct string snippet concatenation (`top_cite.snippet`) rather than invoking full 2-5 sentence LLM synthesis with evidence grounding.
- **Pydantic / Schema Truncation**:
  - No Pydantic `max_length` field limits were violated, but snippet string slicing truncated answers mid-sentence.

---

## 2. Problem 2 (Wrong PDF Retrieval) Diagnosis

- **Chunk Text Lacks Identity**:
  - **Root Cause Identified**: Chunks were passed to the embedding function as raw text snippets without document headers. Consequently, a query for *"summer semester course registration"* matched generic registration terms in `DOC-PLACEMENT` (distance 0.9412) rather than `DOC-SUMMER` (distance 1.0380).
- **Index Hygiene & Chunk IDs**:
  - Scanned PDF documents (`DOC-FEE-SCHED`, `DOC-SUMMER`) lacked prepended document metadata headers during vector embedding.
- **Top-k Dominated by Generic Terms**:
  - Prepending `[Document Title | Section | Version]` to the chunk text prior to embedding solves cross-document confusion and ensures correct document ranking.

---

## 3. Problem 1 (Hallucination & Evidence Grounding) Diagnosis

- **Prompt Grounding**:
  - The generation prompt must explicitly enforce strict evidence-only answering: copy numbers and dates verbatim, abstain when evidence is partial, and cite sources.
- **Evidence Threshold Calibration**:
  - Distance threshold of `1.20` effectively isolates unanswerable queries (`not_found`), but prepending chunk identity ensures valid matches have distance `< 0.90`.
- **Temperature**:
  - System temperature is strictly set to `0.0`.
