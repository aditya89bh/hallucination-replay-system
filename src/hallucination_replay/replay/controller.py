"""Replay controller for active sessions."""

from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay.checkpoints import (
    ReplayCheckpoint,
    ReplayCheckpointManager,
)
from hallucination_replay.replay.loader import ReplayTraceLoader
from hallucination_replay.replay.navigation import ReplayNavigation
from hallucination_replay.replay.session import ReplaySession
from hallucination_replay.replay.snapshots import ReplaySnapshot, create_replay_snapshot
from hallucination_replay.replay.state_manager import ReplayStateManager


class ReplayController:
    """Coordinate an active replay session and loaded trace."""

    def __init__(self, trace: RunTrace, session: ReplaySession) -> None:
        """Create a controller for a loaded trace and session."""
        if session.trace_id != trace.run_id:
            message = "ReplaySession trace_id must match RunTrace run_id"
            raise ValueError(message)
        self.trace = trace
        self.session = session
        self.steps = ReplayTraceLoader().get_steps(trace)
        self._navigation = ReplayNavigation(self.session, self.steps)
        self._checkpoints = ReplayCheckpointManager(self.session)
        self.state_manager = ReplayStateManager()
        self._record_current_position()

    @classmethod
    def create(
        cls,
        trace: RunTrace,
        session_id: str,
        created_at: datetime | None = None,
    ) -> ReplayController:
        """Create a replay controller with a new session."""
        loaded_trace = ReplayTraceLoader().load_from_object(trace)
        session = ReplaySession(
            session_id=session_id,
            trace_id=loaded_trace.run_id,
            current_position=0,
            created_at=created_at or datetime.now(UTC),
        )
        return cls(trace=loaded_trace, session=session)

    @property
    def step_count(self) -> int:
        """Return the number of replayable steps."""
        return len(self.steps)

    def current_step(self) -> AgentStep | None:
        """Return the current step, or None when the trace has no steps."""
        if not self.steps:
            return None
        return self.steps[self.session.current_position]

    def has_next(self) -> bool:
        """Return whether replay can move forward."""
        return self._navigation.has_next()

    def next_step(self) -> AgentStep | None:
        """Return the next step without moving replay state."""
        return self._navigation.next_step()

    def move_forward(self) -> AgentStep | None:
        """Move replay state forward by one step."""
        step = self._navigation.move_forward()
        self._record_current_position()
        return step

    def has_previous(self) -> bool:
        """Return whether replay can move backward."""
        return self._navigation.has_previous()

    def previous_step(self) -> AgentStep | None:
        """Return the previous step without moving replay state."""
        return self._navigation.previous_step()

    def move_backward(self) -> AgentStep | None:
        """Move replay state backward by one step."""
        step = self._navigation.move_backward()
        self._record_current_position()
        return step

    def jump_to_step(self, step_id: str) -> AgentStep:
        """Jump replay state to a step identifier."""
        step = self._navigation.jump_to_step(step_id)
        self._record_current_position()
        return step

    def jump_to_index(self, index: int) -> AgentStep:
        """Jump replay state to a zero-based step index."""
        step = self._navigation.jump_to_index(index)
        self._record_current_position()
        return step

    def create_checkpoint(
        self, checkpoint_id: str, metadata: dict[str, object] | None = None
    ) -> ReplayCheckpoint:
        """Create a replay checkpoint at the current position."""
        return self._checkpoints.create_checkpoint(checkpoint_id, metadata)

    def restore_checkpoint(self, checkpoint_id: str) -> ReplayCheckpoint:
        """Restore replay state from a checkpoint."""
        checkpoint = self._checkpoints.restore_checkpoint(checkpoint_id)
        self._record_current_position()
        return checkpoint

    def create_snapshot(
        self, snapshot_id: str, metadata: dict[str, object] | None = None
    ) -> ReplaySnapshot:
        """Create a serializable snapshot of the current replay state."""
        return create_replay_snapshot(
            self.session, self.current_step(), snapshot_id, metadata
        )

    def _record_current_position(self) -> None:
        """Record the current replay position in state manager."""
        self.state_manager.record_position(
            self.session.current_position, self.current_step()
        )
