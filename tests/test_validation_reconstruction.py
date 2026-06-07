from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_validation
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="validation",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["validations"] = [
        {
            "step_index": 0,
            "event": {
                "validator_name": "schema",
                "passed": True,
                "findings": [],
                "timestamp": "2026-01-01T00:00:00Z",
            },
        },
        {
            "step_index": 1,
            "event": {
                "validator_name": "citation",
                "passed": False,
                "findings": ["missing citation"],
                "timestamp": "2026-01-01T00:01:00Z",
            },
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_validation_returns_activity_and_results() -> None:
    validation = reconstruct_validation(make_trace(), 1)

    assert [record.event.validator_name for record in validation.records] == [
        "schema",
        "citation",
    ]
    assert [record.event.validator_name for record in validation.passed] == ["schema"]
    assert [record.event.validator_name for record in validation.failed] == ["citation"]


def test_reconstruct_validation_filters_future_activity() -> None:
    validation = reconstruct_validation(make_trace(), 0)

    assert [record.event.validator_name for record in validation.records] == ["schema"]


def test_reconstruct_validation_rejects_invalid_metadata() -> None:
    trace = make_trace()
    trace.metadata["validations"] = "invalid"

    with pytest.raises(ReplayError, match="validations"):
        reconstruct_validation(trace, 0)
