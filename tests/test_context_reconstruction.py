from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_context
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
    metadata["context"] = [
        {"key": "later", "value": "hidden", "source": "fixture", "step_index": 2},
        {"key": "task", "value": "answer", "source": "fixture", "step_index": 0},
        {"key": "doc", "value": "retrieved", "source": "fixture", "step_index": 1},
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_context_returns_available_context_at_step() -> None:
    context = reconstruct_context(make_trace(), 1)

    assert context.trace_id == "run-1"
    assert context.current_step.step_id == "step-2"
    assert [entry.key for entry in context.entries] == ["task", "doc"]
    assert [step.step_id for step in context.prior_steps] == ["step-1", "step-2"]


def test_reconstruct_context_is_deterministically_ordered() -> None:
    first = reconstruct_context(make_trace(), 1)
    second = reconstruct_context(make_trace(), 1)

    assert first.to_json() == second.to_json()


def test_reconstruct_context_rejects_unknown_step() -> None:
    with pytest.raises(ReplayError, match="step index not found"):
        reconstruct_context(make_trace(), 99)
