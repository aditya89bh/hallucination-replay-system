from __future__ import annotations

import json
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
        metadata=steps_to_metadata([make_step("step-1", 0)]),
    )
    return ReplayController.create(trace, "session-1")


def test_create_snapshot_captures_current_replay_state() -> None:
    controller = make_controller()

    snapshot = controller.create_snapshot("snapshot-1", {"label": "start"})

    assert snapshot.snapshot_id == "snapshot-1"
    assert snapshot.session_id == "session-1"
    assert snapshot.trace_id == "run-1"
    assert snapshot.current_position == 0
    assert snapshot.current_step is not None
    assert snapshot.current_step["step_id"] == "step-1"
    assert snapshot.metadata == {"label": "start"}


def test_snapshot_is_serializable() -> None:
    snapshot = make_controller().create_snapshot("snapshot-1")

    payload = json.loads(snapshot.to_json())

    assert payload["snapshot_id"] == "snapshot-1"
    assert payload["current_step"]["step_id"] == "step-1"
