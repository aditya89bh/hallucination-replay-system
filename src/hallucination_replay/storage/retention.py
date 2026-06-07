"""Retention policy support for stored traces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from hallucination_replay.storage.index import TraceIndex


@dataclass(frozen=True, slots=True)
class TraceRetentionPolicy:
    """Select traces eligible for deletion under retention constraints."""

    max_age_days: int | None = None
    max_traces: int | None = None
    dry_run: bool = True

    def select_traces_for_deletion(
        self, index: TraceIndex, reference_time: datetime
    ) -> list[str]:
        """Return run identifiers selected for deletion."""
        selected_run_ids: set[str] = set()
        if self.max_age_days is not None:
            cutoff = reference_time - timedelta(days=self.max_age_days)
            selected_run_ids.update(
                entry.run_id
                for entry in index.entries.values()
                if entry.started_at < cutoff
            )
        if self.max_traces is not None and len(index.entries) > self.max_traces:
            entries_by_age = sorted(
                index.entries.values(), key=lambda entry: entry.started_at, reverse=True
            )
            selected_run_ids.update(
                entry.run_id for entry in entries_by_age[self.max_traces :]
            )
        return sorted(selected_run_ids)
