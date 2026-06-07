from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from hallucination_replay.exceptions import StorageError
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository


def make_trace(run_id: str = "run-1") -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={"agent_name": "agent-a"},
    )


def test_filesystem_repository_creates_base_directory(tmp_path: Path) -> None:
    base_path = tmp_path / "traces"

    FilesystemTraceRepository(base_path)

    assert base_path.exists()


def test_filesystem_repository_saves_one_trace_per_run_id(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    trace = make_trace()

    repository.save_trace(trace)

    assert (tmp_path / "run-1.json").exists()
    assert repository.exists("run-1") is True


def test_filesystem_repository_loads_saved_trace(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    trace = make_trace()

    repository.save_trace(trace)

    assert repository.load_trace("run-1") == trace


def test_filesystem_repository_lists_and_deletes_traces(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(make_trace("run-2"))
    repository.save_trace(make_trace("run-1"))

    assert repository.list_traces() == ["run-1", "run-2"]

    repository.delete_trace("run-1")

    assert repository.list_traces() == ["run-2"]
    assert repository.exists("run-1") is False


def test_filesystem_repository_rejects_path_traversal_run_id(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)

    with pytest.raises(StorageError, match="Invalid run_id"):
        repository.save_trace(make_trace("../unsafe"))
