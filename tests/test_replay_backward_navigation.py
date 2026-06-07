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
    controller = ReplayController.create(trace, "session-1")
    controller.move_forward()
    return controller


def test_has_previous_reports_backward_availability() -> None:
    controller = make_controller()

    assert controller.has_previous() is True


def test_previous_step_peeks_without_moving() -> None:
    controller = make_controller()

    previous_step = controller.previous_step()

    assert previous_step is not None
    assert previous_step.step_id == "step-1"
    assert controller.session.current_position == 1


def test_move_backward_moves_to_previous_step() -> None:
    controller = make_controller()

    step = controller.move_backward()

    assert step is not None
    assert step.step_id == "step-1"
    assert controller.session.current_position == 0


def test_move_backward_does_not_move_before_first_step() -> None:
    controller = make_controller()

    controller.move_backward()
    controller.move_backward()

    assert controller.session.current_position == 0
    assert controller.has_previous() is False
