"""Tool result schema model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, StrictBool


class ToolResult(BaseModel):
    """Result returned by a tool invocation."""

    tool_name: str
    success: StrictBool
    output: Any = None
    execution_time_ms: float = Field(ge=0)
    step_id: str
