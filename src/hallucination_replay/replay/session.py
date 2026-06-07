"""Replay session state model."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from hallucination_replay.models.base import TraceModel


class ReplaySession(TraceModel):
    """State for a deterministic replay session."""

    session_id: str
    trace_id: str
    current_position: int = Field(default=0, ge=0)
    created_at: datetime
