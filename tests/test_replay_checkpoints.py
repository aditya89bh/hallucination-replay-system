from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import ReplayController, steps_to_metadata


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
            [make_step("step-1", 0), make_step("step-2", 1)]
        ),
    )
    return ReplayController.create(trace, "session-1")


def test_create_checkpoint_stores_position_and_metadata() -> None:
    controller = make_controller()
    controller.move_forward()

    checkpoint = controller.create_checkpoint("checkpoint-1", {"label": "after-step-2"})

    assert checkpoint.checkpoint_id == "checkpoint-1"
    assert checkpoint.position == 1
    assert checkpoint.metadata == {"label": "after-step-2"}


def test_restore_checkpoint_resets_session_position() -> None:
    controller = make_controller()
    checkpoint = controller.create_checkpoint("checkpoint-1")
    controller.move_forward()

    restored = controller.restore_checkpoint("checkpoint-1")

    assert restored == checkpoint
    assert controller.session.current_position == 0


def test_restore_checkpoint_rejects_unknown_checkpoint() -> None:
    controller = make_controller()

    with pytest.raises(ReplayError, match="checkpoint not found"):
        controller.restore_checkpoint("missing")
