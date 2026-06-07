"""Trace import API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from hallucination_replay.exceptions import StorageError
from hallucination_replay.models import RunTrace
from hallucination_replay.storage.repository import TraceRepository


def import_trace(
    repository: TraceRepository, source_path: Path, *, overwrite: bool = False
) -> RunTrace:
    """Import and persist one trace from a JSON file."""
    trace = _load_trace(source_path)
    if repository.exists(trace.run_id) and not overwrite:
        message = f"Trace already exists: {trace.run_id}"
        raise StorageError(message)
    repository.save_trace(trace)
    return trace


def import_traces(
    repository: TraceRepository, source_directory: Path, *, overwrite: bool = False
) -> list[RunTrace]:
    """Import all JSON traces from a directory."""
    return [
        import_trace(repository, source_path, overwrite=overwrite)
        for source_path in sorted(source_directory.glob("*.json"))
    ]


def _load_trace(source_path: Path) -> RunTrace:
    """Load and validate a trace from a JSON file."""
    try:
        payload: Any = json.loads(source_path.read_text(encoding="utf-8"))
        return RunTrace.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        message = f"Failed to import trace JSON: {source_path}"
        raise StorageError(message) from exc
