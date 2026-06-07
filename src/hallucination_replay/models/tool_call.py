"""Tool call schema model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """A request made by an agent to an external or internal tool."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    invocation_time: datetime
    step_id: str
