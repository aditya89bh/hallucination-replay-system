from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models.agent_step import AgentStep


def test_agent_step_accepts_required_fields() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    step = AgentStep(
        step_id="step-1",
        step_index=0,
        step_type="tool",
        timestamp=timestamp,
        description="Call search tool",
    )

    assert step.step_id == "step-1"
    assert step.step_index == 0
    assert step.step_type == "tool"
    assert step.timestamp == timestamp
    assert step.description == "Call search tool"


def test_agent_step_rejects_negative_index() -> None:
    payload = {
        "step_id": "step-1",
        "step_index": -1,
        "step_type": "tool",
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        "description": "Invalid step",
    }

    with pytest.raises(ValidationError, match="step_index"):
        AgentStep.model_validate(payload)


def test_agent_step_rejects_invalid_step_type() -> None:
    payload = {
        "step_id": "step-1",
        "step_index": 0,
        "step_type": "unknown",
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        "description": "Invalid step",
    }

    with pytest.raises(ValidationError, match="step_type"):
        AgentStep.model_validate(payload)
