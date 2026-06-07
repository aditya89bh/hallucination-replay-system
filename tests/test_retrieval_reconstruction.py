from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_retrieval
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="retrieval",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["retrievals"] = [
        {
            "step_index": 1,
            "event": {
                "query": "beta",
                "retrieved_documents": [{"id": "doc-2", "text": "second"}],
                "retrieval_time_ms": 2.0,
                "source": "vector",
            },
        },
        {
            "step_index": 0,
            "event": {
                "query": "alpha",
                "retrieved_documents": [{"id": "doc-1", "text": "first"}],
                "retrieval_time_ms": 1.0,
                "source": "vector",
            },
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_retrieval_returns_step_specific_events_and_documents() -> None:
    retrieval = reconstruct_retrieval(make_trace(), 1)

    assert [record.event.query for record in retrieval.events] == ["alpha", "beta"]
    assert [document["id"] for document in retrieval.retrieved_documents] == [
        "doc-1",
        "doc-2",
    ]


def test_reconstruct_retrieval_filters_future_events() -> None:
    retrieval = reconstruct_retrieval(make_trace(), 0)

    assert [record.event.query for record in retrieval.events] == ["alpha"]


def test_reconstruct_retrieval_rejects_invalid_metadata() -> None:
    trace = make_trace()
    trace.metadata["retrievals"] = "invalid"

    with pytest.raises(ReplayError, match="retrievals"):
        reconstruct_retrieval(trace, 0)
