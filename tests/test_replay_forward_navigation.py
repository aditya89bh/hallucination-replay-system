from __future__ import annotations

from datetime import UTC, datetime

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


def test_has_next_reports_forward_availability() -> None:
    controller = make_controller()

    assert controller.has_next() is True


def test_next_step_peeks_without_moving() -> None:
    controller = make_controller()

    next_step = controller.next_step()

    assert next_step is not None
    assert next_step.step_id == "step-2"
    assert controller.session.current_position == 0


def test_move_forward_advances_to_next_step() -> None:
    controller = make_controller()

    step = controller.move_forward()

    assert step is not None
    assert step.step_id == "step-2"
    assert controller.session.current_position == 1


def test_move_forward_does_not_move_beyond_final_step() -> None:
    controller = make_controller()

    controller.move_forward()
    controller.move_forward()

    assert controller.session.current_position == 1
    assert controller.has_next() is False
