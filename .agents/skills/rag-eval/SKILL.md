---
name: rag-eval
description: Automated evaluation and benchmark runner for UniAssist AI RAG policy engine. Use to execute pytest suite and update eval/report.md.
---

# RAG Evaluation & Benchmark Skill (`rag-eval`)

This skill automates the testing and reporting workflow for the **UniAssist AI** policy and RAG backend engine.

## Workflows

### 1. Run Benchmark Test Suite
Execute the 100% precision evaluation test suite:
```bash
python3 -m pytest -v eval/test_eval_suite.py
```

### 2. Verify API Health Endpoint
Check vector store chunk count and SQLite database status:
```bash
curl -s http://localhost:8000/health
```

### 3. Test What-If Result Simulation (R6)
Simulate dry-run course results without database mutations:
```bash
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-Student-Id: HCL2026-8891" \
  -d '{"question":"What if I pass CS601?"}'
```

### 4. Verify Document Cryptographic Verification Hash
```bash
curl -s http://localhost:8000/verify/VERIFIED-HASH-HCL2026-8891-99421A
```
