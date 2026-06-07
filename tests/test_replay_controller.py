from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import (
    ReplayController,
    ReplaySession,
    steps_to_metadata,
)

EXPECTED_STEP_COUNT = 2


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)]),
    )


def test_replay_controller_create_holds_session_and_trace() -> None:
    created_at = datetime(2026, 1, 1, tzinfo=UTC)

    controller = ReplayController.create(make_trace(), "session-1", created_at)

    assert controller.session.session_id == "session-1"
    assert controller.session.trace_id == "run-1"
    assert controller.trace.run_id == "run-1"
    assert controller.step_count == EXPECTED_STEP_COUNT


def test_replay_controller_returns_current_step() -> None:
    controller = ReplayController.create(make_trace(), "session-1")

    current_step = controller.current_step()

    assert current_step is not None
    assert current_step.step_id == "step-1"


def test_replay_controller_rejects_session_trace_mismatch() -> None:
    session = ReplaySession(
        session_id="session-1",
        trace_id="other-run",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="trace_id"):
        ReplayController(make_trace(), session)
