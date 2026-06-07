"""Replay state manager."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models import AgentStep
from hallucination_replay.models.base import TraceModel


class ReplayState(TraceModel):
    """Current replay state and navigation audit trail."""

    current_position: int = Field(default=0, ge=0)
    current_step_id: str | None = None
    visited_steps: list[str] = Field(default_factory=list)
    navigation_history: list[int] = Field(default_factory=list)


class ReplayStateManager:
    """Maintain current replay state for a deterministic replay session."""

    def __init__(self) -> None:
        """Create an empty replay state manager."""
        self.state = ReplayState()

    def record_position(self, position: int, step: AgentStep | None) -> ReplayState:
        """Record the current replay position and step."""
        self.state.current_position = position
        self.state.current_step_id = step.step_id if step is not None else None
        self.state.navigation_history.append(position)
        if step is not None and step.step_id not in self.state.visited_steps:
            self.state.visited_steps.append(step.step_id)
        return self.state
