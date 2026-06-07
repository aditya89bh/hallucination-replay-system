"""Reasoning summary diffing without chain-of-thought comparison."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import ReconstructedReasoning


class ReasoningDiff(TraceModel):
    """Diff between reasoning summaries and confidence evolution."""

    summaries_added: list[str] = Field(default_factory=list)
    summaries_removed: list[str] = Field(default_factory=list)
    event_types_added: list[str] = Field(default_factory=list)
    event_types_removed: list[str] = Field(default_factory=list)
    confidence_delta: float


def diff_reasoning_state(
    reasoning_a: ReconstructedReasoning, reasoning_b: ReconstructedReasoning
) -> ReasoningDiff:
    """Compare reasoning summaries, confidence, and event types only."""
    summaries_a = {_summary_key(record.to_dict()) for record in reasoning_a.summaries}
    summaries_b = {_summary_key(record.to_dict()) for record in reasoning_b.summaries}
    types_a = {_event_type(record.to_dict()) for record in reasoning_a.summaries}
    types_b = {_event_type(record.to_dict()) for record in reasoning_b.summaries}
    return ReasoningDiff(
        summaries_added=sorted(summaries_b - summaries_a),
        summaries_removed=sorted(summaries_a - summaries_b),
        event_types_added=sorted(types_b - types_a),
        event_types_removed=sorted(types_a - types_b),
        confidence_delta=round(
            _latest_confidence(reasoning_b) - _latest_confidence(reasoning_a), 4
        ),
    )


def _summary_key(record: dict[str, object]) -> str:
    event = record.get("event")
    if not isinstance(event, dict):
        return ""
    return "|".join(str(event.get(key, "")) for key in ("reasoning_type", "summary"))


def _event_type(record: dict[str, object]) -> str:
    event = record.get("event")
    if not isinstance(event, dict):
        return ""
    value = event.get("reasoning_type", "")
    return value if isinstance(value, str) else ""


def _latest_confidence(reasoning: ReconstructedReasoning) -> float:
    if not reasoning.confidence_evolution:
        return 0.0
    return reasoning.confidence_evolution[-1].confidence
