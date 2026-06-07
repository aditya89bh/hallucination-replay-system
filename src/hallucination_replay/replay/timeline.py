"""Replay timeline API."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.replay.loader import ReplayTraceLoader


class TimelineItem(TraceModel):
    """A compact timeline entry for an agent step."""

    step_id: str
    step_index: int = Field(ge=0)
    step_type: str
    timestamp: datetime
    description: str


class TimelineSummary(TraceModel):
    """High-level timeline summary."""

    trace_id: str
    step_count: int = Field(ge=0)
    first_step_id: str | None = None
    last_step_id: str | None = None


class TimelineExport(TraceModel):
    """Serializable timeline export payload."""

    trace_id: str
    summary: TimelineSummary
    steps: list[TimelineItem]


class ReplayTimeline:
    """Generate ordered replay timelines from run traces."""

    def __init__(self, trace: RunTrace) -> None:
        """Create a timeline for a trace."""
        self._trace = ReplayTraceLoader().load_from_object(trace)
        self._steps = ReplayTraceLoader().get_steps(trace)

    def ordered_steps(self) -> list[AgentStep]:
        """Return ordered timeline steps."""
        return list(self._steps)

    def items(self) -> list[TimelineItem]:
        """Return compact timeline items."""
        return [
            TimelineItem(
                step_id=step.step_id,
                step_index=step.step_index,
                step_type=step.step_type,
                timestamp=step.timestamp,
                description=step.description,
            )
            for step in self._steps
        ]

    def summary(self) -> TimelineSummary:
        """Return a summary of the replay timeline."""
        first_step_id = self._steps[0].step_id if self._steps else None
        last_step_id = self._steps[-1].step_id if self._steps else None
        return TimelineSummary(
            trace_id=self._trace.run_id,
            step_count=len(self._steps),
            first_step_id=first_step_id,
            last_step_id=last_step_id,
        )

    def export(self) -> TimelineExport:
        """Return a serializable timeline export model."""
        return TimelineExport(
            trace_id=self._trace.run_id,
            summary=self.summary(),
            steps=self.items(),
        )
