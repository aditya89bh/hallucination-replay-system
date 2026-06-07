from __future__ import annotations

import pytest
from pydantic import ValidationError

from hallucination_replay.models.retrieval_event import RetrievalEvent

RETRIEVAL_TIME_MS = 12.5


def test_retrieval_event_accepts_required_fields() -> None:
    event = RetrievalEvent(
        query="What caused the failure?",
        retrieved_documents=[{"id": "doc-1", "text": "Evidence"}],
        retrieval_time_ms=RETRIEVAL_TIME_MS,
        source="vector-store",
    )

    assert event.query == "What caused the failure?"
    assert event.retrieved_documents == [{"id": "doc-1", "text": "Evidence"}]
    assert event.retrieval_time_ms == RETRIEVAL_TIME_MS
    assert event.source == "vector-store"


def test_retrieval_event_defaults_documents() -> None:
    event = RetrievalEvent(
        query="Nothing found",
        retrieval_time_ms=0,
        source="vector-store",
    )

    assert event.retrieved_documents == []


def test_retrieval_event_rejects_negative_retrieval_time() -> None:
    payload = {
        "query": "What caused the failure?",
        "retrieved_documents": [],
        "retrieval_time_ms": -1,
        "source": "vector-store",
    }

    with pytest.raises(ValidationError, match="retrieval_time_ms"):
        RetrievalEvent.model_validate(payload)
