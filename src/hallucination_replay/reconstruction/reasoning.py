"""Reasoning reconstruction without chain-of-thought exposure."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import ReasoningEvent, RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context


class ReasoningRecord(TraceModel):
    """A reasoning summary associated with a replay step."""

    step_index: int = Field(ge=0)
    event: ReasoningEvent


class ConfidencePoint(TraceModel):
    """Confidence value at a replay step."""

    step_index: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)


class ReconstructedReasoning(TraceModel):
    """Reasoning summaries and confidence evolution at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    summaries: list[ReasoningRecord] = Field(default_factory=list)
    confidence_evolution: list[ConfidencePoint] = Field(default_factory=list)


def reconstruct_reasoning(trace: RunTrace, step_index: int) -> ReconstructedReasoning:
    """Reconstruct reasoning summaries and confidence evolution at a step."""
    reconstruct_context(trace, step_index)
    records = _reasoning_records(trace, step_index)
    return ReconstructedReasoning(
        trace_id=trace.run_id,
        step_index=step_index,
        summaries=records,
        confidence_evolution=[
            ConfidencePoint(
                step_index=record.step_index,
                confidence=record.event.confidence,
            )
            for record in records
        ],
    )


def _reasoning_records(trace: RunTrace, step_index: int) -> list[ReasoningRecord]:
    raw_records = trace.metadata.get("reasoning", [])
    if not isinstance(raw_records, list):
        message = "RunTrace metadata field 'reasoning' must be a list"
        raise ReplayError(message)
    records = [ReasoningRecord.model_validate(record) for record in raw_records]
    available_records = [
        record for record in records if record.step_index <= step_index
    ]
    return sorted(
        available_records,
        key=lambda record: (record.step_index, record.event.timestamp),
    )
