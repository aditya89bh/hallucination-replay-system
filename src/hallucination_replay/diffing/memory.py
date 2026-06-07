"""Memory diffing for execution comparisons."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import ReconstructedMemory


class MemoryDiff(TraceModel):
    """Diff between reconstructed memory states."""

    reads_added: list[str] = Field(default_factory=list)
    reads_removed: list[str] = Field(default_factory=list)
    writes_added: list[str] = Field(default_factory=list)
    writes_removed: list[str] = Field(default_factory=list)
    state_added: list[str] = Field(default_factory=list)
    state_removed: list[str] = Field(default_factory=list)
    state_modified: list[str] = Field(default_factory=list)


def diff_memory_state(
    memory_a: ReconstructedMemory, memory_b: ReconstructedMemory
) -> MemoryDiff:
    """Compare memory reads, writes, and final memory state."""
    reads_a = {_record_key(record.to_dict()) for record in memory_a.reads}
    reads_b = {_record_key(record.to_dict()) for record in memory_b.reads}
    writes_a = {_record_key(record.to_dict()) for record in memory_a.writes}
    writes_b = {_record_key(record.to_dict()) for record in memory_b.writes}
    state_a = memory_a.state
    state_b = memory_b.state
    return MemoryDiff(
        reads_added=sorted(reads_b - reads_a),
        reads_removed=sorted(reads_a - reads_b),
        writes_added=sorted(writes_b - writes_a),
        writes_removed=sorted(writes_a - writes_b),
        state_added=sorted(set(state_b) - set(state_a)),
        state_removed=sorted(set(state_a) - set(state_b)),
        state_modified=sorted(
            key for key in set(state_a) & set(state_b) if state_a[key] != state_b[key]
        ),
    )


def _record_key(record: dict[str, object]) -> str:
    event = record.get("event")
    if not isinstance(event, dict):
        return repr(sorted(record.items()))
    return "|".join(str(event.get(key, "")) for key in ("event_type", "key", "value"))
