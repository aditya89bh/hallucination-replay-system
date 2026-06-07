from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import (
    diff_replay_positions,
    diff_states,
    reconstruct_state,
)
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
            "step_index": 1,
            "event": {
                "event_type": "write",
                "key": "answer",
                "value": "42",
                "timestamp": "2026-01-01T00:01:00Z",
            },
        }
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_diff_states_returns_changed_sections() -> None:
    trace = make_trace()
    before = reconstruct_state(trace, 0)
    after = reconstruct_state(trace, 1)

    diff = diff_states(before, after)

    assert diff.from_step_index == 0
    assert diff.to_step_index == 1
    assert "memory" in [section.section for section in diff.changed_sections]


def test_diff_replay_positions_reconstructs_and_compares_positions() -> None:
    diff = diff_replay_positions(make_trace(), 0, 1)

    assert diff.trace_id == "run-1"
    assert diff.changed_sections
