"""Replay checkpoint models and management."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models.base import TraceModel
from hallucination_replay.replay.session import ReplaySession


class ReplayCheckpoint(TraceModel):
    """A restorable replay position with metadata."""

    checkpoint_id: str
    session_id: str
    trace_id: str
    position: int = Field(ge=0)
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReplayCheckpointManager:
    """Create and restore replay checkpoints for a session."""

    def __init__(self, session: ReplaySession) -> None:
        """Create a checkpoint manager for a replay session."""
        self._session = session
        self._checkpoints: dict[str, ReplayCheckpoint] = {}

    def create_checkpoint(
        self,
        checkpoint_id: str,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> ReplayCheckpoint:
        """Create a checkpoint at the current replay position."""
        checkpoint = ReplayCheckpoint(
            checkpoint_id=checkpoint_id,
            session_id=self._session.session_id,
            trace_id=self._session.trace_id,
            position=self._session.current_position,
            created_at=created_at or datetime.now(UTC),
            metadata=metadata or {},
        )
        self._checkpoints[checkpoint_id] = checkpoint
        return checkpoint

    def restore_checkpoint(self, checkpoint_id: str) -> ReplayCheckpoint:
        """Restore the replay session to a checkpoint position."""
        checkpoint = self._checkpoints.get(checkpoint_id)
        if checkpoint is None:
            message = f"Replay checkpoint not found: {checkpoint_id}"
            raise ReplayError(message)
        self._session.current_position = checkpoint.position
        return checkpoint

    def list_checkpoints(self) -> list[ReplayCheckpoint]:
        """Return checkpoints sorted by creation time."""
        return sorted(self._checkpoints.values(), key=lambda item: item.created_at)
