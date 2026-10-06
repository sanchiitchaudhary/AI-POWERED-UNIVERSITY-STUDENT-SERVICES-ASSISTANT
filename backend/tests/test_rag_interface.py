"""Tests for the application-to-RAG boundary and its unavailable fallback."""
from app.rag_interface import Chunk, ExistingRAGAdapter, FakeRetriever, NotConfiguredRetriever
from app.llm.client import LLMClient
from app.llm.prompts import Classification, classification_messages
from app.precedence import Candidate, Context, resolve_candidates


def test_fake_retriever_returns_fixture_chunks_and_receives_context_filters():
    chunk = Chunk("DOC-1", "7.1", 2, "3.1", "2024-07-01", "Attendance clause", 0.92)
    retriever = FakeRetriever([chunk])
    filters = {"programme": "B.Tech CSE", "batch_year": 2025, "as_of_date": "2026-10-06"}
    assert retriever.retrieve("attendance", filters) == [chunk]
    assert retriever.calls == [("attendance", filters)]


def test_policy_question_retrieval_flows_through_existing_precedence_engine():
    client = LLMClient(mock=True)
    classification = client.chat(
        classification_messages("What is the minimum attendance requirement?"), Classification,
    ).parsed
    assert classification.category == "policy_fact"
    regulation = Chunk("REG", "7.1", 2, "3.1", "2024-07-01", "75 percent", 0.9,
                       metadata={"authority_level": 1, "scope_programmes": "B.Tech", "scope_batches": "ALL"})
    circular = Chunk("CIRC", "7.1", 1, "1.0", "2026-08-01", "80 percent", 0.95,
                     metadata={"authority_level": 2, "supersedes": "REG#7.1", "scope_programmes": "B.Tech", "scope_batches": "2025+"})
    faq = Chunk("FAQ", "7.1", 1, "1.0", "2026-09-15", "65 percent", 0.8,
                metadata={"authority_level": 4, "scope_programmes": "ALL", "scope_batches": "ALL"})
    retrieved = FakeRetriever([regulation, circular, faq]).retrieve("minimum attendance", {
        "programme": "B.Tech CSE", "batch_year": 2025, "as_of_date": "2026-10-06",
    })
    candidates = [Candidate(
        key=chunk.doc_id, doc_id=chunk.doc_id, section=chunk.section or "",
        authority_level=chunk.metadata["authority_level"], effective_from=chunk.effective_from or "",
        supersedes=chunk.metadata.get("supersedes", ""),
        scope_programmes=chunk.metadata["scope_programmes"],
        scope_batches=chunk.metadata["scope_batches"], value=chunk.text,
    ) for chunk in retrieved]
    decision = resolve_candidates(candidates, Context("2026-10-06", "B.Tech CSE", 2025))
    assert decision.winner.key == "CIRC"
    assert decision.decided_at_step == 3  # Supersession then FAQ loses on authority.


def test_not_configured_retriever_returns_empty_without_crashing():
    retriever = NotConfiguredRetriever()
    assert retriever.retrieve("policy question", {"as_of_date": "2026-10-06"}) == []
    result = retriever.ingest(b"content", "policy.txt", {"doc_id": "DOC-1"})
    assert result["status"] == "unavailable"
    assert result["indexed"] is False


def test_chunk_keeps_required_fields_and_extra_precedence_metadata():
    chunk = Chunk(
        doc_id="DOC-1", section="7.1", page=2, version="3.1",
        effective_from="2024-07-01", text="Clause text", score=0.8,
        metadata={"authority_level": 1, "effective_to": "", "supersedes": "",
                  "scope_programmes": "B.Tech", "scope_batches": "ALL", "source_section": "7.1"},
    )
    assert (chunk.doc_id, chunk.section, chunk.page, chunk.version, chunk.effective_from, chunk.score) == (
        "DOC-1", "7.1", 2, "3.1", "2024-07-01", 0.8,
    )
    assert chunk.metadata["authority_level"] == 1
    assert chunk.metadata["scope_programmes"] == "B.Tech"
    assert chunk.metadata["source_section"] == "7.1"


def test_existing_adapter_uses_teammate_retrieval_and_preserves_returned_metadata():
    class Citation:
        doc_id = "DOC-1"
        doc_title = "Regulations"
        page = 2
        section = "Clause 7.1"
        authority_level = 1
        effective_from = "2024-07-01"
        snippet = "Attendance requirement"

        def model_dump(self):
            return {"doc_id": self.doc_id, "doc_title": self.doc_title, "page": self.page,
                    "section": self.section, "authority_level": self.authority_level,
                    "effective_from": self.effective_from, "snippet": self.snippet}

    class Upcoming:
        doc_id = "DOC-2"
        effective_from = "2027-01-01"
        description = "Future change"

        def model_dump(self):
            return {"doc_id": self.doc_id, "effective_from": self.effective_from,
                    "description": self.description}

    class Engine:
        DEFAULT_AS_OF_DATE = "2026-10-06"
        def query_vector_store(self, query, as_of_date):
            self.call = (query, as_of_date)
            return [Citation()], [Upcoming()], False

    engine = Engine()
    chunks = ExistingRAGAdapter(engine).retrieve("attendance", {
        "programme": "B.Tech CSE", "batch_year": 2025, "as_of_date": "2026-10-06",
    })
    assert engine.call == ("attendance", "2026-10-06")
    assert chunks[0].doc_id == "DOC-1"
    assert chunks[0].section == "7.1"
    assert chunks[0].metadata["legacy_section"] == "Clause 7.1"
    assert chunks[0].metadata["authority_level"] == 1
    assert chunks[1].metadata["upcoming"] is True
    assert chunks[1].effective_from == "2027-01-01"


def test_adapter_forwards_all_context_filters_supported_by_rag_owner():
    class Engine:
        DEFAULT_AS_OF_DATE = "2026-10-06"
        def query_vector_store(self, query, filters=None, as_of_date=None, programme=None, batch_year=None):
            self.call = (filters, as_of_date, programme, batch_year)
            return [], [], False

    engine = Engine()
    filters = {"programme": "B.Tech CSE", "batch_year": 2025, "as_of_date": "2026-10-06"}
    ExistingRAGAdapter(engine).retrieve("attendance", filters)
    assert engine.call == (filters, "2026-10-06", "B.Tech CSE", 2025)


def test_ingestion_adapter_delegates_to_existing_pipeline():
    class Engine:
        def ingest_document_to_vector_store(self, **kwargs):
            self.kwargs = kwargs
            with open(kwargs["file_path"], "rb") as stream:
                self.file_bytes = stream.read()
            return {"doc_id": kwargs["doc_id"], "chunks": 1, "indexed": True, "status": "active"}

    engine = Engine()
    result = ExistingRAGAdapter(engine).ingest(
        b"PDF bytes", "source.pdf", {"doc_id": "DOC-1", "title": "Source", "authority_level": 2, "effective_from": "2026-08-01"},
    )
    assert result["indexed"] is True
    assert engine.kwargs["authority_level"] == 2
    assert engine.kwargs["effective_from"] == "2026-08-01"
    assert engine.file_bytes == b"PDF bytes"
    assert not __import__("pathlib").Path(engine.kwargs["file_path"]).exists()
