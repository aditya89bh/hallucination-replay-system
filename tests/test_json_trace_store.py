from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from hallucination_replay.exceptions import StorageError
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import JsonTraceStore


def make_trace(run_id: str = "run-1") -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        completed_at=datetime(2026, 1, 1, 0, 1, tzinfo=UTC),
        status="completed",
        metadata={"agent_name": "agent-a", "tags": ["smoke"]},
    )


def test_json_store_writes_readable_json(tmp_path: Path) -> None:
    store = JsonTraceStore(tmp_path)

    store.save(make_trace())

    raw_json = (tmp_path / "run-1.json").read_text(encoding="utf-8")
    assert raw_json.endswith("\n")
    assert '\n  "run_id"' in raw_json
    assert json.loads(raw_json)["run_id"] == "run-1"


def test_json_store_loads_trace_model(tmp_path: Path) -> None:
    store = JsonTraceStore(tmp_path)
    trace = make_trace()

    store.save(trace)

    assert store.load("run-1") == trace


def test_json_store_raises_storage_error_for_missing_trace(tmp_path: Path) -> None:
    store = JsonTraceStore(tmp_path)

    with pytest.raises(StorageError, match="Trace not found"):
        store.load("missing")


def test_json_store_raises_storage_error_for_invalid_json(tmp_path: Path) -> None:
    store = JsonTraceStore(tmp_path)
    (tmp_path / "run-1.json").write_text("{not-json", encoding="utf-8")

    with pytest.raises(StorageError, match="Failed to load trace JSON"):
        store.load("run-1")
