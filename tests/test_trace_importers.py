from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from hallucination_replay.exceptions import StorageError
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import (
    FilesystemTraceRepository,
    import_trace,
    import_traces,
)


def make_trace(run_id: str) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={"agent_name": "agent-a"},
    )


def write_trace(path: Path, trace: RunTrace) -> None:
    path.write_text(json.dumps(trace.model_dump(mode="json")), encoding="utf-8")


def test_import_one_trace_from_json(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "repo")
    source_path = tmp_path / "run-1.json"
    write_trace(source_path, make_trace("run-1"))

    trace = import_trace(repository, source_path)

    assert trace.run_id == "run-1"
    assert repository.exists("run-1") is True


def test_import_multiple_traces_from_directory(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "repo")
    source_directory = tmp_path / "imports"
    source_directory.mkdir()
    write_trace(source_directory / "run-1.json", make_trace("run-1"))
    write_trace(source_directory / "run-2.json", make_trace("run-2"))

    traces = import_traces(repository, source_directory)

    assert [trace.run_id for trace in traces] == ["run-1", "run-2"]


def test_import_avoids_overwrite_unless_enabled(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "repo")
    repository.save_trace(make_trace("run-1"))
    source_path = tmp_path / "run-1.json"
    write_trace(source_path, make_trace("run-1"))

    with pytest.raises(StorageError, match="already exists"):
        import_trace(repository, source_path)

    assert import_trace(repository, source_path, overwrite=True).run_id == "run-1"


def test_import_validates_trace_payload(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path / "repo")
    source_path = tmp_path / "invalid.json"
    source_path.write_text('{"run_id":"missing-required-fields"}', encoding="utf-8")

    with pytest.raises(StorageError, match="Failed to import"):
        import_trace(repository, source_path)
