from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import (
    FilesystemTraceRepository,
    export_trace,
    export_traces,
)


def make_trace(run_id: str) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={"agent_name": "agent-a"},
    )


def test_export_one_trace_to_target_path(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "source")
    repository.save_trace(make_trace("run-1"))
    target_path = tmp_path / "exports" / "trace.json"

    exported_path = export_trace(repository, "run-1", target_path)

    assert exported_path == target_path
    assert json.loads(target_path.read_text(encoding="utf-8"))["run_id"] == "run-1"


def test_export_multiple_traces_to_directory(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "source")
    repository.save_trace(make_trace("run-1"))
    repository.save_trace(make_trace("run-2"))

    exported_paths = export_traces(repository, ["run-1", "run-2"], tmp_path / "exports")

    assert exported_paths == [
        tmp_path / "exports" / "run-1.json",
        tmp_path / "exports" / "run-2.json",
    ]
    assert all(path.exists() for path in exported_paths)


def test_export_rejects_unsupported_format(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "source")

    with pytest.raises(ValueError, match="Unsupported"):
        export_trace(repository, "run-1", tmp_path / "trace.yaml", export_format="yaml")
