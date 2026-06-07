from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import TraceRepository


class FakeTraceRepository:
    def __init__(self) -> None:
        self._traces: dict[str, RunTrace] = {}

    def save_trace(self, trace: RunTrace) -> None:
        self._traces[trace.run_id] = trace

    def load_trace(self, run_id: str) -> RunTrace:
        return self._traces[run_id]

    def delete_trace(self, run_id: str) -> None:
        del self._traces[run_id]

    def list_traces(self) -> list[str]:
        return sorted(self._traces)

    def exists(self, run_id: str) -> bool:
        return run_id in self._traces


def make_trace(run_id: str = "run-1") -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="running",
    )


def test_fake_repository_satisfies_trace_repository_protocol() -> None:
    repository: TraceRepository = FakeTraceRepository()
    trace = make_trace()

    repository.save_trace(trace)

    assert repository.exists("run-1") is True
    assert repository.load_trace("run-1") == trace
    assert repository.list_traces() == ["run-1"]


def test_fake_repository_deletes_trace() -> None:
    repository: TraceRepository = FakeTraceRepository()
    repository.save_trace(make_trace())

    repository.delete_trace("run-1")

    assert repository.exists("run-1") is False


def test_fake_repository_raises_for_missing_trace() -> None:
    repository: TraceRepository = FakeTraceRepository()

    with pytest.raises(KeyError):
        repository.load_trace("missing")
