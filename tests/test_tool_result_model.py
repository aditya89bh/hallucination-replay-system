from __future__ import annotations

import pytest
from pydantic import ValidationError

from hallucination_replay.models.tool_result import ToolResult

EXECUTION_TIME_MS = 42.5


def test_tool_result_accepts_required_fields() -> None:
    result = ToolResult(
        tool_name="search",
        success=True,
        output={"matches": 3},
        execution_time_ms=EXECUTION_TIME_MS,
        step_id="step-1",
    )

    assert result.tool_name == "search"
    assert result.success is True
    assert result.output == {"matches": 3}
    assert result.execution_time_ms == EXECUTION_TIME_MS
    assert result.step_id == "step-1"


def test_tool_result_rejects_negative_execution_time() -> None:
    payload = {
        "tool_name": "search",
        "success": True,
        "output": "done",
        "execution_time_ms": -1,
        "step_id": "step-1",
    }

    with pytest.raises(ValidationError, match="execution_time_ms"):
        ToolResult.model_validate(payload)


def test_tool_result_rejects_invalid_success_type() -> None:
    payload = {
        "tool_name": "search",
        "success": "yes",
        "output": "done",
        "execution_time_ms": 1,
        "step_id": "step-1",
    }

    with pytest.raises(ValidationError, match="success"):
        ToolResult.model_validate(payload)
