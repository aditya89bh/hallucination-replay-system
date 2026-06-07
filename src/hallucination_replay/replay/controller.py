"""Replay controller for active sessions."""

from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay.loader import ReplayTraceLoader
from hallucination_replay.replay.session import ReplaySession


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
