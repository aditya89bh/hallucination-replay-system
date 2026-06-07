"""Reasoning event schema model."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from hallucination_replay.models.base import TraceModel

ReasoningType = Literal["planning", "reflection", "decision", "error_analysis"]


class ReasoningEvent(TraceModel):
    """A concise reasoning summary without chain-of-thought content."""

    reasoning_type: ReasoningType
    summary: str
    confidence: float = Field(ge=0, le=1)
    timestamp: datetime
