"""Synchronous replay event stream."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field

from hallucination_replay.models.base import TraceModel

ReplayEventType = Literal[
    "step_entered",
    "step_exited",
    "checkpoint_created",
    "snapshot_created",
]


class ReplayEvent(TraceModel):
    """Base replay event."""

    event_type: ReplayEventType
    session_id: str
    trace_id: str
    position: int = Field(ge=0)
    timestamp: datetime


class StepEntered(ReplayEvent):
    """Event emitted when a replay step is entered."""

    event_type: Literal["step_entered"] = "step_entered"
    step_id: str


class StepExited(ReplayEvent):
    """Event emitted when a replay step is exited."""

    event_type: Literal["step_exited"] = "step_exited"
    step_id: str


class CheckpointCreated(ReplayEvent):
    """Event emitted when a checkpoint is created."""

    event_type: Literal["checkpoint_created"] = "checkpoint_created"
    checkpoint_id: str


class SnapshotCreated(ReplayEvent):
    """Event emitted when a snapshot is created."""

    event_type: Literal["snapshot_created"] = "snapshot_created"
    snapshot_id: str


class ReplayEventStream:
    """In-memory synchronous replay event stream."""

    def __init__(self) -> None:
        """Create an empty event stream."""
        self._events: list[ReplayEvent] = []

    def emit(self, event: ReplayEvent) -> ReplayEvent:
        """Append an event to the stream and return it."""
        self._events.append(event)
        return event

    def list_events(self) -> list[ReplayEvent]:
        """Return emitted events in order."""
        return list(self._events)


def utc_now() -> datetime:
    """Return current UTC time for event creation."""
    return datetime.now(UTC)
