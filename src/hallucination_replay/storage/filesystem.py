"""Filesystem-backed trace repository."""

from __future__ import annotations

from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage.index import TraceIndex
from hallucination_replay.storage.json_store import JsonTraceStore
from hallucination_replay.storage.repository import TraceRepository


class FilesystemTraceRepository(TraceRepository):
    """Persist one run trace per readable JSON file under a base directory."""

    def __init__(self, base_path: Path) -> None:
        """Create a filesystem repository rooted at the provided path."""
        self.base_path = base_path
        self._store = JsonTraceStore(base_path)
        self._index_path = self.base_path / ".trace-index.json"
        self._index = TraceIndex.load(self._index_path)

    @property
    def index(self) -> TraceIndex:
        """Return the in-memory trace index."""
        return self._index

    def save_trace(self, trace: RunTrace) -> None:
        """Persist a trace as readable JSON and update the index."""
        self._store.save(trace)
        self._index.update_trace(trace)
        self._index.save(self._index_path)

    def load_trace(self, run_id: str) -> RunTrace:
        """Load a trace from its run identifier."""
        return self._store.load(run_id)

    def delete_trace(self, run_id: str) -> None:
        """Delete a trace file if it exists and update the index."""
        self._store.delete(run_id)
        self._index.remove_trace(run_id)
        self._index.save(self._index_path)

    def list_traces(self) -> list[str]:
        """List all run identifiers stored in the repository."""
        if self._index.entries:
            return self._index.list_run_ids()
        return self._store.list_run_ids()

    def exists(self, run_id: str) -> bool:
        """Return whether a trace file exists."""
        return self._store.exists(run_id)
