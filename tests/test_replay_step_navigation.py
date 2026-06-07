from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import ReplayController, steps_to_metadata

STEP_THREE_POSITION = 2


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description=step_id,
    )


def make_controller() -> ReplayController:
    trace = RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata(
            [
                make_step("step-1", 0),
                make_step("step-2", 1),
                make_step("step-3", 2),
            ]
        ),
    )
    return ReplayController.create(trace, "session-1")


def test_jump_to_step_moves_to_matching_step_id() -> None:
    controller = make_controller()

    step = controller.jump_to_step("step-3")

    assert step.step_id == "step-3"
    assert controller.session.current_position == STEP_THREE_POSITION


def test_jump_to_index_moves_to_matching_index() -> None:
    controller = make_controller()

    step = controller.jump_to_index(1)

    assert step.step_id == "step-2"
    assert controller.session.current_position == 1


def test_jump_to_step_rejects_unknown_step_id() -> None:
    controller = make_controller()

    with pytest.raises(ReplayError, match="not found"):
        controller.jump_to_step("missing")


def test_jump_to_index_rejects_out_of_range_index() -> None:
    controller = make_controller()

    with pytest.raises(ReplayError, match="out of range"):
        controller.jump_to_index(3)
