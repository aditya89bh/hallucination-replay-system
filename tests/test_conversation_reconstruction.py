from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_conversation
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["conversation"] = [
        {
            "step_index": 1,
            "role": "assistant",
            "content": "Answer",
            "timestamp": "2026-01-01T00:01:00Z",
        },
        {
            "step_index": 0,
            "role": "user",
            "content": "Question",
            "timestamp": "2026-01-01T00:00:00Z",
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_conversation_returns_ordered_history() -> None:
    conversation = reconstruct_conversation(make_trace(), 1)

    assert [message.role for message in conversation.messages] == ["user", "assistant"]
    assert [message.content for message in conversation.messages] == [
        "Question",
        "Answer",
    ]


def test_reconstruct_conversation_filters_future_messages() -> None:
    conversation = reconstruct_conversation(make_trace(), 0)

    assert [message.content for message in conversation.messages] == ["Question"]


def test_reconstruct_conversation_rejects_invalid_metadata() -> None:
    trace = make_trace()
    trace.metadata["conversation"] = "invalid"

    with pytest.raises(ReplayError, match="conversation"):
        reconstruct_conversation(trace, 0)
