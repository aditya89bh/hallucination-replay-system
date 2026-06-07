"""Tool result schema model."""

from __future__ import annotations

from typing import Any

from pydantic import Field, StrictBool

from hallucination_replay.models.base import TraceModel


class ToolResult(TraceModel):
    """Result returned by a tool invocation."""

    tool_name: str
    success: StrictBool
    output: Any = None
    execution_time_ms: float = Field(ge=0)
    step_id: str
