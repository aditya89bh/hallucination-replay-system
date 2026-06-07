from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import (
    FilesystemTraceRepository,
    TraceLifecycleManager,
)


def make_trace() -> RunTrace:
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="running",
        metadata={"agent_name": "agent-a", "tags": ["lifecycle"]},
    )


def test_lifecycle_manager_marks_completed(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(make_trace())
    completed_at = datetime(2026, 1, 1, 0, 5, tzinfo=UTC)

    trace = TraceLifecycleManager(repository).mark_completed("run-1", completed_at)

    assert trace.status == "completed"
    assert trace.completed_at == completed_at
    assert repository.load_trace("run-1").status == "completed"


def test_lifecycle_manager_marks_failed(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(make_trace())
    failed_at = datetime(2026, 1, 1, 0, 6, tzinfo=UTC)

    trace = TraceLifecycleManager(repository).mark_failed("run-1", failed_at)

    assert trace.status == "failed"
    assert trace.completed_at == failed_at


def test_lifecycle_manager_marks_archived_and_preserves_data(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    original_trace = make_trace()
    repository.save_trace(original_trace)

    trace = TraceLifecycleManager(repository).mark_archived("run-1")

    assert trace.status == "archived"
    assert trace.run_id == original_trace.run_id
    assert trace.started_at == original_trace.started_at
    assert trace.metadata == original_trace.metadata
