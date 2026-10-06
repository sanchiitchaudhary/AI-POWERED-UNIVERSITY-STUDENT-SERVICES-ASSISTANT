# Live Change Guide (LIVE_CHANGE_GUIDE.md)

This document provides quick step-by-step instructions for making rapid live changes during judge evaluation.

---

## 1. How to Add or Change a Rule
- **Via Admin API**:
  ```bash
  curl -X POST http://localhost:8000/admin/rules \
    -H "Content-Type: application/json" \
    -d '{
      "rule_code": "R-ATT-NEW-01",
      "parameter": "min_attendance_pct",
      "operator": ">=",
      "value": "80",
      "effective_from": "2026-10-06",
      "scope_programmes": "ALL",
      "scope_batches": "2024+",
      "authority_level": 1,
      "source_doc_id": "DOC-CIRC-2026-04"
    }'
  ```
- **Via Database**: Update `rule_registry` in `data/university.db`.

---

## 2. How to Change `TOP_K` Vector Search Depth
- Edit `backend/config.py`:
  ```python
  TOP_K = int(os.environ.get("TOP_K", "6"))  # Change default to 6
  ```
- Or pass environment variable when starting uvicorn:
  ```bash
  TOP_K=6 python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```

---

## 3. How to Add a New Deterministic Tool
1. Add the Python function in `backend/tools.py`.
2. Register the tool invocation handler in `backend/main.py` under `ask_question()`.
3. Append `ToolInvocation(tool="my_tool_name", input={...}, output={...})` to `tools_invoked`.

---

## 4. How to Modify Refusal Messages or Guardrail Patterns
- Open [`backend/guardrails.py`](file:///Users/sanchitchaudhary/Desktop/HCL%20HACKATHON/backend/guardrails.py).
- Add new regex patterns to `INJECTION_PATTERNS` or `CROSS_STUDENT_PATTERNS`.
- Changes take effect immediately upon server reload.

---

## 5. How to Add a New Answer Type
1. Edit [`backend/models.py`](file:///Users/sanchitchaudhary/Desktop/HCL%20HACKATHON/backend/models.py) to add the literal string to `answer_type` in `AskResponse`.
2. Return the new `answer_type` in `backend/main.py`.
