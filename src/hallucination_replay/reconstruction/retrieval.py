"""Retrieval reconstruction for replay traces."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import RetrievalEvent, RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context


class RetrievalRecord(TraceModel):
    """A retrieval event associated with a replay step."""

    step_index: int = Field(ge=0)
    event: RetrievalEvent


class ReconstructedRetrieval(TraceModel):
    """Retrieved evidence available at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    events: list[RetrievalRecord] = Field(default_factory=list)
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list)


def reconstruct_retrieval(trace: RunTrace, step_index: int) -> ReconstructedRetrieval:
    """Reconstruct retrieval events and documents available at a step."""
    reconstruct_context(trace, step_index)
    events = _retrieval_events(trace, step_index)
    documents: list[dict[str, Any]] = []
    for record in events:
        documents.extend(record.event.retrieved_documents)
    return ReconstructedRetrieval(
        trace_id=trace.run_id,
        step_index=step_index,
        events=events,
        retrieved_documents=documents,
    )


def _retrieval_events(trace: RunTrace, step_index: int) -> list[RetrievalRecord]:
    raw_events = trace.metadata.get("retrievals", [])
    if not isinstance(raw_events, list):
        message = "RunTrace metadata field 'retrievals' must be a list"
        raise ReplayError(message)
    records = [RetrievalRecord.model_validate(event) for event in raw_events]
    available_records = [
        record for record in records if record.step_index <= step_index
    ]
    return sorted(
        available_records, key=lambda record: (record.step_index, record.event.query)
    )
