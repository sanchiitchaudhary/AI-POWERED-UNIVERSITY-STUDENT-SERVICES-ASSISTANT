"""Stable boundary to the separately owned legacy RAG service.

This module adapts ``backend.rag_engine``; it does not parse, chunk, embed,
index, or search documents itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from pathlib import Path
import re
import inspect
from tempfile import NamedTemporaryFile
from typing import Any, Protocol, runtime_checkable


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return vars(value)


@dataclass(frozen=True)
class Chunk:
    """Normalized retrieved chunk with source and precedence metadata."""

    doc_id: str
    section: str | None
    page: int | None
    version: str | None
    effective_from: str | None
    text: str
    score: float | None = None
    title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class RAGRetriever(Protocol):
    def retrieve(self, query: str, filters: dict | None = None) -> list[Chunk]: ...

    def ingest(self, file_bytes: bytes, filename: str, metadata: dict) -> dict: ...


class NotConfiguredRetriever:
    """Safe offline implementation used when no RAG provider is available."""

    def retrieve(self, query: str, filters: dict | None = None) -> list[Chunk]:
        return []

    def ingest(self, file_bytes: bytes, filename: str, metadata: dict) -> dict:
        return {"doc_id": metadata.get("doc_id"), "chunks": 0, "indexed": False, "status": "unavailable"}


class FakeRetriever:
    """Deterministic fixture retriever; preserves supplied fixture ordering."""

    def __init__(self, chunks: list[Chunk] | None = None):
        self.chunks = list(chunks or [])
        self.calls: list[tuple[str, dict | None]] = []

    def retrieve(self, query: str, filters: dict | None = None) -> list[Chunk]:
        self.calls.append((query, filters))
        return list(self.chunks)

    def ingest(self, file_bytes: bytes, filename: str, metadata: dict) -> dict:
        return {"doc_id": metadata.get("doc_id"), "chunks": 0, "indexed": False, "status": "fake"}


class ExistingRAGAdapter:
    """Adapter around the repository's teammate-owned ``backend.rag_engine``."""

    def __init__(self, engine: Any = None):
        self._engine = engine

    def _get_engine(self):
        if self._engine is None:
            from backend import rag_engine
            self._engine = rag_engine
        return self._engine

    @staticmethod
    def _retrieve_from_engine(engine: Any, query: str, filters: dict[str, Any]):
        """Forward every supported filter to the teammate's retrieval interface."""
        method = engine.query_vector_store
        try:
            parameters = inspect.signature(method).parameters
        except (TypeError, ValueError):
            parameters = {}
        kwargs = {}
        if "filters" in parameters:
            kwargs["filters"] = filters
        if "as_of_date" in parameters:
            as_of_date = filters.get("as_of_date") or getattr(engine, "DEFAULT_AS_OF_DATE", None)
            if as_of_date is not None:
                kwargs["as_of_date"] = str(as_of_date)
        for key in ("programme", "batch_year"):
            if key in parameters and key in filters:
                kwargs[key] = filters[key]
        return method(query, **kwargs)

    def retrieve(self, query: str, filters: dict | None = None) -> list[Chunk]:
        try:
            engine = self._get_engine()
            filters = filters or {}
            as_of_date = filters.get("as_of_date") or getattr(engine, "DEFAULT_AS_OF_DATE", None)
            if as_of_date is None:
                return []
            citations, upcoming, _ = self._retrieve_from_engine(engine, query, filters)
            source_metadata = self._source_metadata(engine, [item.doc_id for item in citations])
            chunks = []
            for citation in citations:
                data = _mapping(citation)
                source = source_metadata.get(data.get("doc_id"), {})
                original_section = data.get("section")
                section = re.sub(r"^(?:Section|Clause|Article)\s+", "", str(original_section), flags=re.IGNORECASE) if original_section else None
                metadata = {
                    "authority_level": data.get("authority_level"),
                    "doc_title": data.get("doc_title"),
                    "legacy_section": original_section,
                    "upcoming": False,
                    **source,
                }
                chunks.append(Chunk(
                    doc_id=data.get("doc_id", ""), section=section,
                    page=data.get("page"), version=data.get("version") or source.get("version"),
                    effective_from=data.get("effective_from"), text=data.get("snippet", ""),
                    score=data.get("score"), title=data.get("doc_title"), metadata=metadata,
                ))
            for change in upcoming:
                data = _mapping(change)
                chunks.append(Chunk(
                    doc_id=data.get("doc_id", ""), section=data.get("section"),
                    page=data.get("page"), version=data.get("version"),
                    effective_from=data.get("effective_from"), text=data.get("description", ""),
                    score=None, title=data.get("title"), metadata={**data, "upcoming": True},
                ))
            return chunks
        except Exception:
            # Retrieval availability must not take down the student-services app.
            return []

    @staticmethod
    def _source_metadata(engine: Any, doc_ids: list[str]) -> dict[str, dict[str, Any]]:
        """Read metadata the legacy retriever omits without duplicating search."""
        if not doc_ids or not hasattr(engine, "get_db_connection"):
            return {}
        connection = None
        try:
            connection = engine.get_db_connection()
            placeholders = ",".join("?" for _ in doc_ids)
            rows = connection.execute(
                f"SELECT doc_id, doc_type, version FROM source_register WHERE doc_id IN ({placeholders})",
                tuple(doc_ids),
            ).fetchall()
            return {row["doc_id"]: {"doc_type": row["doc_type"], "version": row["version"]} for row in rows}
        except Exception:
            return {}
        finally:
            if connection is not None:
                connection.close()

    def query_legacy(self, query: str, as_of_date: str):
        """Preserve the legacy endpoint's tuple contract while routing via this boundary."""
        try:
            return self._retrieve_from_engine(self._get_engine(), query, {"as_of_date": as_of_date})
        except Exception:
            return [], [], False

    def ingest(self, file_bytes: bytes, filename: str, metadata: dict) -> dict:
        suffix = Path(filename).suffix
        temporary_path = None
        try:
            with NamedTemporaryFile(suffix=suffix, delete=False) as temporary:
                temporary.write(file_bytes)
                temporary_path = Path(temporary.name)
            engine = self._get_engine()
            return engine.ingest_document_to_vector_store(
                doc_id=str(metadata["doc_id"]),
                doc_title=str(metadata.get("title", metadata.get("doc_title", filename))),
                file_path=str(temporary_path),
                authority_level=int(metadata.get("authority_level", 3)),
                effective_from=str(metadata.get("effective_from", "2026-01-01")),
            )
        except Exception:
            return {"doc_id": metadata.get("doc_id"), "chunks": 0, "indexed": False, "status": "unavailable"}
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def collection_count(self) -> int:
        try:
            return int(self._get_engine().vector_collection.count())
        except Exception:
            return 0


_default_retriever: RAGRetriever = ExistingRAGAdapter()


def set_default_retriever(retriever: RAGRetriever) -> None:
    """Set the process-level adapter, primarily for application wiring and tests."""
    global _default_retriever
    _default_retriever = retriever


def get_default_retriever() -> RAGRetriever:
    return _default_retriever
