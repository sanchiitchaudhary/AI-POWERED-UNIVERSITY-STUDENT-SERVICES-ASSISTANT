# Architectural & Implementation Decisions (DECISIONS.md)

## 1. Vector Database: ChromaDB (Local Persistent)
- **Decision**: Selected ChromaDB with persistent disk storage (`CHROMA_PATH`).
- **Rationale**: ChromaDB is lightweight, runs locally without external cloud dependencies, supports metadata filtering (e.g. `effective_from`, `authority_level`), and preserves state across app restarts.
- **Alternative Rejected**: Pinecone / Qdrant Cloud (rejected to guarantee 100% offline local capability and zero network latency dependency).

## 2. Rule Precedence & Storage: SQLite DB + Deterministic Engine
- **Decision**: SQLite for `students`, `courses`, `attendance`, `results`, `rule_registry`, `source_register`, and `audit_logs`.
- **Rationale**: Guarantees ACID transactional safety for live CSV student uploads (`POST /admin/load_students`) and deterministic precedence evaluation for rules (`>=, >, <=, <, ==, between`).
- **Precedence Logic**:
  1. Filter by `as_of_date >= effective_from`.
  2. Scope matching: Programme (`ALL` or matching string) and Batch (`ALL`, `2023+`, `2021-2023`, `2022;2023`).
  3. Precedence hierarchy: Authority Level (Level 1 Statute > Level 2 Circular > Level 3/4 > Level 5 Unofficial), then Recency (`effective_from DESC`).

## 3. Auto Rule Extraction Tradeoff (Section D)
- **Decision**: Default `AUTO_RULE_EXTRACTION=false`. Newly proposed LLM rules are stored with `status=proposed`.
- **Tradeoff Analysis**: Automated LLM rule extraction without human review risks introducing faulty parameters into the core evaluation engine. Marking candidates as `proposed` and requiring explicit approval via `GET /admin/rules?status=proposed` ensures zero hallucinated rules affect student grades or eligibility calculations.

## 4. Security & Privacy Guardrails
- **Decision**: Multi-tier security check prior to RAG retrieval or tool execution.
- **Rules**:
  - Prompt injection strings trigger immediate `refused` response.
  - Personal student queries ("my attendance", "my GPA") require valid `X-Student-Id` header.
  - Inquiries attempting cross-student data leakage or aggregate student enumeration are blocked with safe neutral `refused` responses.

## 5. What-If Tool Simulation (`simulate_result`)
- **Decision**: Isolated in-memory dry-run execution (`tools.py`).
- **Rationale**: Allows students to simulate academic outcomes (e.g., "What if I pass CS601?") without modifying the production database.
