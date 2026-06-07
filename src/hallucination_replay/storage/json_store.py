"""Readable JSON persistence for trace models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from hallucination_replay.exceptions import StorageError
from hallucination_replay.models import RunTrace


class JsonTraceStore:
    """Persist run traces as human-readable JSON files."""

    def __init__(self, base_path: Path) -> None:
        """Create a JSON trace store rooted at a directory."""
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, trace: RunTrace) -> None:
        """Save a trace as formatted JSON."""
        trace_path = self.trace_path(trace.run_id)
        temporary_path = trace_path.with_suffix(".json.tmp")
        payload = trace.model_dump(mode="json")
        temporary_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(trace_path)

    def load(self, run_id: str) -> RunTrace:
        """Load and validate a trace from JSON."""
        trace_path = self.trace_path(run_id)
        if not trace_path.exists():
            message = f"Trace not found: {run_id}"
            raise StorageError(message)
        try:
            payload: Any = json.loads(trace_path.read_text(encoding="utf-8"))
            return RunTrace.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            message = f"Failed to load trace JSON for run_id={run_id!r}"
            raise StorageError(message) from exc

    def delete(self, run_id: str) -> None:
        """Delete a trace JSON file if present."""
        trace_path = self.trace_path(run_id)
        if trace_path.exists():
            trace_path.unlink()

    def list_run_ids(self) -> list[str]:
        """List run identifiers for stored JSON traces."""
        return sorted(path.stem for path in self.base_path.glob("*.json"))

    def exists(self, run_id: str) -> bool:
        """Return whether a JSON trace exists."""
        return self.trace_path(run_id).exists()

    def trace_path(self, run_id: str) -> Path:
        """Return a safe JSON path for a run identifier."""
        if not run_id or Path(run_id).name != run_id:
            message = f"Invalid run_id for JSON storage: {run_id!r}"
            raise StorageError(message)
        return self.base_path / f"{run_id}.json"
