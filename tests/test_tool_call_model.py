from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models.tool_call import ToolCall


def test_tool_call_accepts_required_fields() -> None:
    invocation_time = datetime(2026, 1, 1, tzinfo=UTC)

    call = ToolCall(
        tool_name="search",
        arguments={"query": "agent trace"},
        invocation_time=invocation_time,
        step_id="step-1",
    )

    assert call.tool_name == "search"
    assert call.arguments == {"query": "agent trace"}
    assert call.invocation_time == invocation_time
    assert call.step_id == "step-1"


def test_tool_call_defaults_arguments() -> None:
    invocation_time = datetime(2026, 1, 1, tzinfo=UTC)

    call = ToolCall(
        tool_name="clock",
        invocation_time=invocation_time,
        step_id="step-2",
    )

    assert call.arguments == {}


def test_tool_call_rejects_non_mapping_arguments() -> None:
    payload = {
        "tool_name": "search",
        "arguments": ["not", "a", "mapping"],
        "invocation_time": datetime(2026, 1, 1, tzinfo=UTC),
        "step_id": "step-1",
    }

    with pytest.raises(ValidationError, match="arguments"):
        ToolCall.model_validate(payload)
