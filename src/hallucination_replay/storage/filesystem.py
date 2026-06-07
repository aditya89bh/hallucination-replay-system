"""Filesystem-backed trace repository."""

from __future__ import annotations

from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage.repository import TraceRepository


class FilesystemTraceRepository(TraceRepository):
    """Persist one run trace per file under a base directory."""

    def __init__(self, base_path: Path) -> None:
        """Create a filesystem repository rooted at the provided path."""
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_trace(self, trace: RunTrace) -> None:
        """Persist a trace as a file named by run identifier."""
        trace_path = self._trace_path(trace.run_id)
        temporary_path = trace_path.with_suffix(".json.tmp")
        temporary_path.write_text(trace.to_json(), encoding="utf-8")
        temporary_path.replace(trace_path)

    def load_trace(self, run_id: str) -> RunTrace:
        """Load a trace from its run identifier."""
        return RunTrace.from_json(self._trace_path(run_id).read_text(encoding="utf-8"))

    def delete_trace(self, run_id: str) -> None:
        """Delete a trace file if it exists."""
        trace_path = self._trace_path(run_id)
        if trace_path.exists():
            trace_path.unlink()

    def list_traces(self) -> list[str]:
        """List all run identifiers stored in the repository."""
        return sorted(path.stem for path in self.base_path.glob("*.json"))

    def exists(self, run_id: str) -> bool:
        """Return whether a trace file exists."""
        return self._trace_path(run_id).exists()

    def _trace_path(self, run_id: str) -> Path:
        """Return a safe trace file path for a run identifier."""
        if not run_id or Path(run_id).name != run_id:
            message = f"Invalid run_id for filesystem storage: {run_id!r}"
            raise ValueError(message)
        return self.base_path / f"{run_id}.json"
