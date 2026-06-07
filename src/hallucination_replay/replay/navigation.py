"""Replay navigation primitives."""

from __future__ import annotations

from hallucination_replay.models import AgentStep
from hallucination_replay.replay.session import ReplaySession


class ReplayNavigation:
    """Navigate ordered replay steps deterministically."""

    def __init__(self, session: ReplaySession, steps: list[AgentStep]) -> None:
        """Create a navigator for a replay session and ordered steps."""
        self._session = session
        self._steps = steps

    def has_next(self) -> bool:
        """Return whether another step exists after the current position."""
        return bool(self._steps) and self._session.current_position < (
            len(self._steps) - 1
        )

    def next_step(self) -> AgentStep | None:
        """Return the next step without moving the session."""
        if not self.has_next():
            return None
        return self._steps[self._session.current_position + 1]

    def move_forward(self) -> AgentStep | None:
        """Move to the next step, stopping at the final step."""
        if self.has_next():
            self._session.current_position += 1
        if not self._steps:
            return None
        return self._steps[self._session.current_position]

    def has_previous(self) -> bool:
        """Return whether a step exists before the current position."""
        return bool(self._steps) and self._session.current_position > 0

    def previous_step(self) -> AgentStep | None:
        """Return the previous step without moving the session."""
        if not self.has_previous():
            return None
        return self._steps[self._session.current_position - 1]

    def move_backward(self) -> AgentStep | None:
        """Move to the previous step, stopping at the first step."""
        if self.has_previous():
            self._session.current_position -= 1
        if not self._steps:
            return None
        return self._steps[self._session.current_position]
