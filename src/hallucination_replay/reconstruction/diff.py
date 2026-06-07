"""Structured reconstruction diff support."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.state import (
    ReconstructedState,
    reconstruct_state,
)


class SectionDiff(TraceModel):
    """Difference for one reconstructed state section."""

    section: str
    before: dict[str, Any]
    after: dict[str, Any]


class ReconstructionDiff(TraceModel):
    """Structured diff between two reconstructed states."""

    trace_id: str
    from_step_index: int = Field(ge=0)
    to_step_index: int = Field(ge=0)
    changed_sections: list[SectionDiff] = Field(default_factory=list)


def diff_states(
    before: ReconstructedState, after: ReconstructedState
) -> ReconstructionDiff:
    """Compare two reconstructed states."""
    changed_sections: list[SectionDiff] = []
    for section in _state_sections():
        before_value = getattr(before, section).to_dict()
        after_value = getattr(after, section).to_dict()
        if before_value != after_value:
            changed_sections.append(
                SectionDiff(section=section, before=before_value, after=after_value)
            )
    return ReconstructionDiff(
        trace_id=after.trace_id,
        from_step_index=before.step_index,
        to_step_index=after.step_index,
        changed_sections=changed_sections,
    )


def diff_replay_positions(
    trace: RunTrace, from_step_index: int, to_step_index: int
) -> ReconstructionDiff:
    """Compare reconstructed state at two replay positions."""
    return diff_states(
        reconstruct_state(trace, from_step_index),
        reconstruct_state(trace, to_step_index),
    )


def _state_sections() -> list[str]:
    return [
        "context",
        "prompt",
        "memory",
        "retrieval",
        "tools",
        "validation",
        "reasoning",
    ]
