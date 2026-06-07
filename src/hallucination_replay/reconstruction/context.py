"""Context reconstruction for replay traces."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.replay import ReplayTraceLoader


class ContextEntry(TraceModel):
    """A context item available at a replay step."""

    key: str
    value: Any
    source: str = "trace"
    step_index: int = Field(ge=0)


class ReconstructedContext(TraceModel):
    """Deterministic context available at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    current_step: AgentStep
    prior_steps: list[AgentStep] = Field(default_factory=list)
    entries: list[ContextEntry] = Field(default_factory=list)


def reconstruct_context(trace: RunTrace, step_index: int) -> ReconstructedContext:
    """Reconstruct context available to the agent at a step index."""
    steps = ReplayTraceLoader().get_steps(trace)
    current_step = _step_at_index(steps, step_index)
    entries = _context_entries(trace, step_index)
    prior_steps = [step for step in steps if step.step_index <= step_index]
    return ReconstructedContext(
        trace_id=trace.run_id,
        step_index=step_index,
        current_step=current_step,
        prior_steps=prior_steps,
        entries=entries,
    )


def _step_at_index(steps: list[AgentStep], step_index: int) -> AgentStep:
    for step in steps:
        if step.step_index == step_index:
            return step
    message = f"Replay step index not found: {step_index}"
    raise ReplayError(message)


def _context_entries(trace: RunTrace, step_index: int) -> list[ContextEntry]:
    raw_entries = trace.metadata.get("context", [])
    if not isinstance(raw_entries, list):
        message = "RunTrace metadata field 'context' must be a list"
        raise ReplayError(message)
    entries = [ContextEntry.model_validate(entry) for entry in raw_entries]
    available_entries = [entry for entry in entries if entry.step_index <= step_index]
    return sorted(available_entries, key=lambda entry: (entry.step_index, entry.key))
