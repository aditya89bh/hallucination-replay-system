"""Trace repository interface definitions."""

from __future__ import annotations

from typing import Protocol

from hallucination_replay.models import RunTrace


class TraceRepository(Protocol):
    """Repository interface for persisting and retrieving run traces."""

    def save_trace(self, trace: RunTrace) -> None:
        """Persist a run trace."""

    def load_trace(self, run_id: str) -> RunTrace:
        """Load a run trace by identifier."""

    def delete_trace(self, run_id: str) -> None:
        """Delete a run trace by identifier."""

    def list_traces(self) -> list[str]:
        """Return all persisted run identifiers."""

    def exists(self, run_id: str) -> bool:
        """Return whether a trace exists for the run identifier."""
