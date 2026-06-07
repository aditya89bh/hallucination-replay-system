"""Lifecycle management for stored traces."""

from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import RunTrace
from hallucination_replay.storage.repository import TraceRepository


class TraceLifecycleManager:
    """Apply lifecycle state transitions to traces in a repository."""

    def __init__(self, repository: TraceRepository) -> None:
        """Create a lifecycle manager for a trace repository."""
        self._repository = repository

    def mark_completed(
        self, run_id: str, completed_at: datetime | None = None
    ) -> RunTrace:
        """Mark a trace as completed and persist the update."""
        trace = self._repository.load_trace(run_id)
        updated_trace = trace.model_copy(
            update={"status": "completed", "completed_at": completed_at or self._now()}
        )
        self._repository.save_trace(updated_trace)
        return updated_trace

    def mark_failed(
        self, run_id: str, completed_at: datetime | None = None
    ) -> RunTrace:
        """Mark a trace as failed and persist the update."""
        trace = self._repository.load_trace(run_id)
        updated_trace = trace.model_copy(
            update={"status": "failed", "completed_at": completed_at or self._now()}
        )
        self._repository.save_trace(updated_trace)
        return updated_trace

    def mark_archived(self, run_id: str) -> RunTrace:
        """Mark a trace as archived while preserving trace data."""
        trace = self._repository.load_trace(run_id)
        updated_trace = trace.model_copy(update={"status": "archived"})
        self._repository.save_trace(updated_trace)
        return updated_trace

    @staticmethod
    def _now() -> datetime:
        """Return the current UTC timestamp."""
        return datetime.now(UTC)
