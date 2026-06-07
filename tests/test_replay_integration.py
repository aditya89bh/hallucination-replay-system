from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import (
    ReplayController,
    ReplayTimeline,
    steps_to_metadata,
)

STEP_TWO_POSITION = 1
STEP_COUNT = 3


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    return RunTrace(
        run_id="integration-run",
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


def test_replay_end_to_end_flow() -> None:
    trace = make_trace()

    controller = ReplayController.create(trace, "integration-session")

    current_step = controller.current_step()
    assert current_step is not None
    assert current_step.step_id == "step-1"
    assert controller.move_forward() is not None
    current_step = controller.current_step()
    assert current_step is not None
    assert current_step.step_id == "step-2"
    assert controller.move_backward() is not None
    current_step = controller.current_step()
    assert current_step is not None
    assert current_step.step_id == "step-1"

    jumped = controller.jump_to_step("step-3")
    assert jumped.step_id == "step-3"

    checkpoint = controller.create_checkpoint("checkpoint-step-3")
    controller.jump_to_index(STEP_TWO_POSITION)
    restored = controller.restore_checkpoint("checkpoint-step-3")

    assert restored == checkpoint
    current_step = controller.current_step()
    assert current_step is not None
    assert current_step.step_id == "step-3"

    snapshot = controller.create_snapshot("snapshot-step-3")
    assert snapshot.current_step is not None
    assert snapshot.current_step["step_id"] == "step-3"

    timeline = ReplayTimeline(trace).export()
    assert timeline.summary.step_count == STEP_COUNT
    assert [step.step_id for step in timeline.steps] == ["step-1", "step-2", "step-3"]
