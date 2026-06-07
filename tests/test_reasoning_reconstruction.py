from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_reasoning
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="reasoning",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["reasoning"] = [
        {
            "step_index": 0,
            "event": {
                "reasoning_type": "planning",
                "summary": "Plan retrieval.",
                "confidence": 0.4,
                "timestamp": "2026-01-01T00:00:00Z",
            },
        },
        {
            "step_index": 1,
            "event": {
                "reasoning_type": "decision",
                "summary": "Use retrieved evidence.",
                "confidence": 0.8,
                "timestamp": "2026-01-01T00:01:00Z",
            },
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_reasoning_returns_summaries_and_confidence() -> None:
    reasoning = reconstruct_reasoning(make_trace(), 1)

    assert [record.event.summary for record in reasoning.summaries] == [
        "Plan retrieval.",
        "Use retrieved evidence.",
    ]
    assert [point.confidence for point in reasoning.confidence_evolution] == [0.4, 0.8]


def test_reconstruct_reasoning_filters_future_summaries() -> None:
    reasoning = reconstruct_reasoning(make_trace(), 0)

    assert [record.event.summary for record in reasoning.summaries] == [
        "Plan retrieval."
    ]


def test_reconstruct_reasoning_does_not_accept_chain_of_thought() -> None:
    trace = make_trace()
    trace.metadata["reasoning"][0]["event"]["chain_of_thought"] = "hidden"

    with pytest.raises(ValidationError):
        reconstruct_reasoning(trace, 0)


def test_reconstruct_reasoning_rejects_invalid_metadata() -> None:
    trace = make_trace()
    trace.metadata["reasoning"] = "invalid"

    with pytest.raises(ReplayError, match="reasoning"):
        reconstruct_reasoning(trace, 0)
