"""Replay snapshot models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from hallucination_replay.models import AgentStep
from hallucination_replay.models.base import TraceModel
from hallucination_replay.replay.session import ReplaySession


class ReplaySnapshot(TraceModel):
    """Serializable snapshot of current replay state."""

    snapshot_id: str
    session_id: str
    trace_id: str
    current_position: int = Field(ge=0)
    current_step: dict[str, Any] | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


def create_replay_snapshot(
    session: ReplaySession,
    current_step: AgentStep | None,
    snapshot_id: str,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> ReplaySnapshot:
    """Create a serializable replay snapshot."""
    return ReplaySnapshot(
        snapshot_id=snapshot_id,
        session_id=session.session_id,
        trace_id=session.trace_id,
        current_position=session.current_position,
        current_step=current_step.to_dict() if current_step is not None else None,
        created_at=created_at or datetime.now(UTC),
        metadata=metadata or {},
    )
