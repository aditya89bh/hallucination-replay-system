"""Trace export API."""

from __future__ import annotations

import json
from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage.repository import TraceRepository

SUPPORTED_EXPORT_FORMAT = "json"


def export_trace(
    repository: TraceRepository,
    run_id: str,
    target_path: Path,
    export_format: str = SUPPORTED_EXPORT_FORMAT,
) -> Path:
    """Export one trace to a target JSON path."""
    _ensure_json_format(export_format)
    trace = repository.load_trace(run_id)
    _write_trace_json(trace, target_path)
    return target_path


def export_traces(
    repository: TraceRepository,
    run_ids: list[str],
    target_directory: Path,
    export_format: str = SUPPORTED_EXPORT_FORMAT,
) -> list[Path]:
    """Export multiple traces to a target directory."""
    _ensure_json_format(export_format)
    target_directory.mkdir(parents=True, exist_ok=True)
    exported_paths: list[Path] = []
    for run_id in run_ids:
        target_path = target_directory / f"{run_id}.json"
        exported_paths.append(
            export_trace(repository, run_id, target_path, export_format)
        )
    return exported_paths


def _write_trace_json(trace: RunTrace, target_path: Path) -> None:
    """Write a trace as readable JSON."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(trace.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _ensure_json_format(export_format: str) -> None:
    """Validate export format."""
    if export_format != SUPPORTED_EXPORT_FORMAT:
        message = f"Unsupported trace export format: {export_format}"
        raise ValueError(message)
