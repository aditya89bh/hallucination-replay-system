"""Agent step schema model."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

StepType = Literal["model", "tool", "retrieval", "memory", "validation", "reasoning"]


class AgentStep(BaseModel):
    """A single ordered step in an agent execution trace."""

    step_id: str
    step_index: int = Field(ge=0)
    step_type: StepType
    timestamp: datetime
    description: str
