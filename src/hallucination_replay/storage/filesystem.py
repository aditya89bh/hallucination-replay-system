"""Filesystem-backed trace repository."""

from __future__ import annotations

from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage.json_store import JsonTraceStore
from hallucination_replay.storage.repository import TraceRepository


class FilesystemTraceRepository(TraceRepository):
    """Persist one run trace per readable JSON file under a base directory."""

    def __init__(self, base_path: Path) -> None:
        """Create a filesystem repository rooted at the provided path."""
        self.base_path = base_path
        self._store = JsonTraceStore(base_path)

    def save_trace(self, trace: RunTrace) -> None:
        """Persist a trace as readable JSON."""
        self._store.save(trace)

    def load_trace(self, run_id: str) -> RunTrace:
        """Load a trace from its run identifier."""
        return self._store.load(run_id)

    def delete_trace(self, run_id: str) -> None:
        """Delete a trace file if it exists."""
        self._store.delete(run_id)

    def list_traces(self) -> list[str]:
        """List all run identifiers stored in the repository."""
        return self._store.list_run_ids()

    def exists(self, run_id: str) -> bool:
        """Return whether a trace file exists."""
        return self._store.exists(run_id)
