"""Retrieval diffing for execution comparisons."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import ReconstructedRetrieval


class RetrievalDiff(TraceModel):
    """Diff between reconstructed retrieval states."""

    queries_added: list[str] = Field(default_factory=list)
    queries_removed: list[str] = Field(default_factory=list)
    documents_added: list[str] = Field(default_factory=list)
    documents_removed: list[str] = Field(default_factory=list)
    coverage_delta: int


def diff_retrieval_state(
    retrieval_a: ReconstructedRetrieval, retrieval_b: ReconstructedRetrieval
) -> RetrievalDiff:
    """Compare retrieval queries, documents, and coverage differences."""
    queries_a = {record.event.query for record in retrieval_a.events}
    queries_b = {record.event.query for record in retrieval_b.events}
    documents_a = {
        _document_key(document) for document in retrieval_a.retrieved_documents
    }
    documents_b = {
        _document_key(document) for document in retrieval_b.retrieved_documents
    }
    return RetrievalDiff(
        queries_added=sorted(queries_b - queries_a),
        queries_removed=sorted(queries_a - queries_b),
        documents_added=sorted(documents_b - documents_a),
        documents_removed=sorted(documents_a - documents_b),
        coverage_delta=len(documents_b) - len(documents_a),
    )


def _document_key(document: dict[str, object]) -> str:
    for key in ("id", "url", "title", "text", "content"):
        value = document.get(key)
        if isinstance(value, str) and value:
            return value
    return repr(sorted(document.items()))
