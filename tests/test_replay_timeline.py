from __future__ import annotations

import json
from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import ReplayTimeline, steps_to_metadata

STEP_COUNT = 2


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
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata([make_step("step-2", 1), make_step("step-1", 0)]),
    )


def test_timeline_returns_ordered_steps() -> None:
    timeline = ReplayTimeline(make_trace())

    assert [step.step_id for step in timeline.ordered_steps()] == ["step-1", "step-2"]


def test_timeline_summary_describes_step_bounds() -> None:
    summary = ReplayTimeline(make_trace()).summary()

    assert summary.trace_id == "run-1"
    assert summary.step_count == STEP_COUNT
    assert summary.first_step_id == "step-1"
    assert summary.last_step_id == "step-2"


def test_timeline_export_is_serializable() -> None:
    export = ReplayTimeline(make_trace()).export()

    payload = json.loads(export.to_json())

    assert payload["trace_id"] == "run-1"
    assert payload["summary"]["step_count"] == STEP_COUNT
    assert payload["steps"][0]["step_id"] == "step-1"
