"""Reasoning event schema model."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReasoningType = Literal["planning", "reflection", "decision", "error_analysis"]


class ReasoningEvent(BaseModel):
    """A concise reasoning summary without chain-of-thought content."""

    reasoning_type: ReasoningType
    summary: str
    confidence: float = Field(ge=0, le=1)
    timestamp: datetime
