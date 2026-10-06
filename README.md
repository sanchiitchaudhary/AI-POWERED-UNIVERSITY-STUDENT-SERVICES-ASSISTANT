# 🎓 UniAssist AI | AI-Powered University Student Services Assistant

> **HCL Hackathon 2026 Submission**  
> An autonomous, 24/7 multi-modal RAG assistant, precedence rule engine, and unified student services portal built for modern higher education institutions.

---

## 🌟 Key Features & Architecture

### 1. 🤖 Autonomous RAG Student Copilot & Precedence Engine
- **24/7 Policy & Inquiry Resolution**: Date-aware RAG policy lookup (`as_of_date` vs `effective_from`).
- **Rule Precedence Engine**: Evaluates authority level hierarchies (Level 1 Statute > Level 2 Circular > Level 5 Unofficial), supersession, and scopes (`ALL`, `2023+`, `2021-2023`).
- **Deterministic What-If Simulation (`simulate_result`)**: Dry-run calculation of academic outcomes without mutating production databases.
- **Conflict & Refusal Handling**: Flagging registry vs circular drift (`conflict_flagged`), level-5 unofficial content tagging, and prompt injection defense.

### 2. 📜 Instant Official Transcripts & Bonafide Letter Generator
- **Digitally Sealed Documents**: Generates verified Official Grade Transcripts and Bonafide Certificates.
- **Cryptographic Verification**: Includes registrar digital checksum hash and QR verification links.

### 3. 📊 Academic & Degree Audit with Target GPA Simulator
- **Interactive GPA Projection**: Drag sliders to project required term GPAs needed for Dean's Honor status.

### 4. 💳 Financial Aid, Fees & Instant Receipts
- **Tuition Ledger**: Detailed breakdown of tuition, lab compute fees, and hostel dues.

### 5. 🎟️ Smart Administrative Support Desk & Ticketing
- **AI Auto-Categorization & Priority**: Tickets tagged by department (*Registrar, Bursar, Housing, Academic Affairs*).

---

## 🛠️ API & Command Contracts

- `GET /health`: System health reporting vector store, SQLite DB, and LLM reachability status.
- `POST /ask`: Main RAG endpoint (accepts `X-Student-Id` header).
- `POST /ingest`: Atomic live document ingestion.
- `POST /admin/load_students`: Dynamic CSV student loader with header-set target table auto-detection.
- `GET /audit/{trace_id}`: Detailed audit record retrieval.

---

## 🚀 Quick Start Guide

### 1. Run FastAPI RAG Backend
```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Backend API will be live on `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### 2. Run React UI Frontend
```bash
npm run dev
```
Frontend UI will be live on `http://localhost:5173`.

### 3. Run Evaluation Test Suite
```bash
python3 -m pytest -v eval/test_eval_suite.py
```

### 4. Run with Docker Compose
```bash
docker-compose up --build
```

---

## 🏷️ Final Submission Tagging Commands

```bash
git add .
git commit -m "feat: complete RAG backend, precedence engine, eval suite, and documentation"
git tag -a final -m "submission"
git push origin main --tags
```

---

## 📢 Disclosure & Fallbacks
- **Local LLM Host**: `OLLAMA_HOST=http://localhost:11434` (Model: `llama3:latest`).
- **Cloud Fallback**: `CLOUD_FALLBACK=false` (Disabled by default; set to `true` for cloud LLM API fallback).
- **OCR Dependencies**: Tesseract OCR engine integrated via `tesseract-ocr` apt package in Docker.
