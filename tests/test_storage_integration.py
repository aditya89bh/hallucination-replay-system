from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import (
    FilesystemTraceRepository,
    TraceFilter,
    TraceSearch,
    export_traces,
    filter_traces,
    import_traces,
)


def make_trace(run_id: str, status: str, agent_name: str, tags: list[str]) -> RunTrace:
    return RunTrace.model_validate(
        {
            "run_id": run_id,
            "started_at": datetime(2026, 1, 1, tzinfo=UTC),
            "completed_at": datetime(2026, 1, 1, 0, 1, tzinfo=UTC),
            "status": status,
            "metadata": {"agent_name": agent_name, "tags": tags},
        }
    )


def test_storage_layer_save_index_search_filter_export_import(tmp_path: Path) -> None:
    source_repository = FilesystemTraceRepository(tmp_path / "source")
    source_repository.save_trace(
        make_trace("run-1", "completed", "agent-a", ["retrieval", "smoke"])
    )
    source_repository.save_trace(make_trace("run-2", "failed", "agent-b", ["memory"]))

    assert source_repository.index.list_run_ids() == ["run-1", "run-2"]
    assert source_repository.index.count_by_status() == {"completed": 1, "failed": 1}
    assert source_repository.index.list_unique_tags() == [
        "memory",
        "retrieval",
        "smoke",
    ]

    search_results = TraceSearch(source_repository.index).by_tag("retrieval")
    assert [entry.run_id for entry in search_results] == ["run-1"]

    filter_results = filter_traces(
        source_repository.index.entries.values(),
        TraceFilter(status="completed", agent_name="agent-a"),
    )
    assert [entry.run_id for entry in filter_results] == ["run-1"]

    exported_paths = export_traces(
        source_repository,
        source_repository.list_traces(),
        tmp_path / "exports",
    )
    assert [path.name for path in exported_paths] == ["run-1.json", "run-2.json"]

    imported_repository = FilesystemTraceRepository(tmp_path / "imported")
    imported_traces = import_traces(imported_repository, tmp_path / "exports")

    assert [trace.run_id for trace in imported_traces] == ["run-1", "run-2"]
    assert imported_repository.index.count_by_agent_name() == {
        "agent-a": 1,
        "agent-b": 1,
    }
    assert imported_repository.load_trace("run-1") == source_repository.load_trace(
        "run-1"
    )
