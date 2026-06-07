"""Trace filtering primitives."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from hallucination_replay.storage.index import TraceIndexEntry


@dataclass(frozen=True, slots=True)
class TraceFilter:
    """Criteria for filtering indexed traces."""

    status: str | None = None
    agent_name: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    started_after: datetime | None = None
    started_before: datetime | None = None

    def matches(self, entry: TraceIndexEntry) -> bool:
        """Return whether an index entry satisfies the filter."""
        if self.status is not None and entry.status != self.status:
            return False
        if self.agent_name is not None and entry.agent_name != self.agent_name:
            return False
        if self.tags and not self.tags.issubset(entry.tags):
            return False
        if self.started_after is not None and entry.started_at <= self.started_after:
            return False
        return not (
            self.started_before is not None and entry.started_at >= self.started_before
        )


def filter_traces(
    entries: Iterable[TraceIndexEntry], trace_filter: TraceFilter
) -> list[TraceIndexEntry]:
    """Filter entries and return them sorted by run identifier."""
    return sorted(
        (entry for entry in entries if trace_filter.matches(entry)),
        key=lambda entry: entry.run_id,
    )
