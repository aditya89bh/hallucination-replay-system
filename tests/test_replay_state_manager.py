from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import (
    ReplayController,
    ReplayStateManager,
    steps_to_metadata,
)


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description=step_id,
    )


def test_state_manager_tracks_current_step_visited_steps_and_history() -> None:
    manager = ReplayStateManager()
    step = make_step("step-1", 0)

    state = manager.record_position(0, step)

    assert state.current_position == 0
    assert state.current_step_id == "step-1"
    assert state.visited_steps == ["step-1"]
    assert state.navigation_history == [0]


def test_controller_updates_state_manager_during_navigation() -> None:
    trace = RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata(
            [make_step("step-1", 0), make_step("step-2", 1)]
        ),
    )
    controller = ReplayController.create(trace, "session-1")

    controller.move_forward()
    controller.move_backward()

    state = controller.state_manager.state
    assert state.current_step_id == "step-1"
    assert state.visited_steps == ["step-1", "step-2"]
    assert state.navigation_history == [0, 1, 0]
