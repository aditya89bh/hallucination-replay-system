"""Memory reconstruction for replay traces."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import MemoryEvent, RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context


class MemoryRecord(TraceModel):
    """A memory event associated with a replay step."""

    step_index: int = Field(ge=0)
    event: MemoryEvent


class ReconstructedMemory(TraceModel):
    """Memory state available at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    reads: list[MemoryRecord] = Field(default_factory=list)
    writes: list[MemoryRecord] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)


def reconstruct_memory(trace: RunTrace, step_index: int) -> ReconstructedMemory:
    """Reconstruct memory reads, writes, and state at a step."""
    reconstruct_context(trace, step_index)
    records = _memory_records(trace, step_index)
    state: dict[str, Any] = {}
    for record in records:
        if record.event.event_type == "write":
            state[record.event.key] = record.event.value
    return ReconstructedMemory(
        trace_id=trace.run_id,
        step_index=step_index,
        reads=[record for record in records if record.event.event_type == "read"],
        writes=[record for record in records if record.event.event_type == "write"],
        state=state,
    )


def _memory_records(trace: RunTrace, step_index: int) -> list[MemoryRecord]:
    raw_records = trace.metadata.get("memory", [])
    if not isinstance(raw_records, list):
        message = "RunTrace metadata field 'memory' must be a list"
        raise ReplayError(message)
    records = [MemoryRecord.model_validate(record) for record in raw_records]
    available_records = [
        record for record in records if record.step_index <= step_index
    ]
    return sorted(
        available_records,
        key=lambda record: (
            record.step_index,
            record.event.timestamp,
            record.event.key,
        ),
    )
