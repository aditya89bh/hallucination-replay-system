from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository, TraceIndex


def make_trace(run_id: str = "run-1", status: str = "completed") -> RunTrace:
    return RunTrace.model_validate(
        {
            "run_id": run_id,
            "started_at": datetime(2026, 1, 1, tzinfo=UTC),
            "completed_at": datetime(2026, 1, 1, 0, 5, tzinfo=UTC),
            "status": status,
            "metadata": {"agent_name": "agent-a", "tags": ["smoke", "eval"]},
        }
    )


def test_trace_index_extracts_searchable_fields() -> None:
    index = TraceIndex()

    index.update_trace(make_trace())

    entry = index.entries["run-1"]
    assert entry.run_id == "run-1"
    assert entry.status == "completed"
    assert entry.agent_name == "agent-a"
    assert entry.tags == ["smoke", "eval"]


def test_trace_index_persists_to_disk(tmp_path: Path) -> None:
    index_path = tmp_path / ".trace-index.json"
    index = TraceIndex()
    index.update_trace(make_trace())

    index.save(index_path)
    loaded_index = TraceIndex.load(index_path)

    assert loaded_index.entries == index.entries


def test_filesystem_repository_updates_index_on_save_and_delete(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)

    repository.save_trace(make_trace())

    assert repository.index.entries["run-1"].agent_name == "agent-a"
    assert (tmp_path / ".trace-index.json").exists()

    repository.delete_trace("run-1")

    assert repository.index.entries == {}
