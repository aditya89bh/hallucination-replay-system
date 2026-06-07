from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_memory
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="memory",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["memory"] = [
        {
            "step_index": 0,
            "event": {
                "event_type": "write",
                "key": "goal",
                "value": "draft",
                "timestamp": "2026-01-01T00:00:00Z",
            },
        },
        {
            "step_index": 1,
            "event": {
                "event_type": "read",
                "key": "goal",
                "value": "draft",
                "timestamp": "2026-01-01T00:01:00Z",
            },
        },
        {
            "step_index": 1,
            "event": {
                "event_type": "write",
                "key": "goal",
                "value": "final",
                "timestamp": "2026-01-01T00:02:00Z",
            },
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_memory_returns_reads_writes_and_state() -> None:
    memory = reconstruct_memory(make_trace(), 1)

    assert [record.event.key for record in memory.reads] == ["goal"]
    assert [record.event.value for record in memory.writes] == ["draft", "final"]
    assert memory.state == {"goal": "final"}


def test_reconstruct_memory_filters_future_events() -> None:
    memory = reconstruct_memory(make_trace(), 0)

    assert memory.reads == []
    assert memory.state == {"goal": "draft"}


def test_reconstruct_memory_rejects_invalid_metadata() -> None:
    trace = make_trace()
    trace.metadata["memory"] = "invalid"

    with pytest.raises(ReplayError, match="memory"):
        reconstruct_memory(trace, 0)
