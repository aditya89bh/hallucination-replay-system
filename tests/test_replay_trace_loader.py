from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import ReplayTraceLoader, steps_to_metadata
from hallucination_replay.storage import TraceRepository


class FakeRepository:
    def __init__(self, trace: RunTrace) -> None:
        self._trace = trace

    def save_trace(self, trace: RunTrace) -> None:
        self._trace = trace

    def load_trace(self, run_id: str) -> RunTrace:
        if self._trace.run_id != run_id:
            raise KeyError(run_id)
        return self._trace

    def delete_trace(self, run_id: str) -> None:
        if self._trace.run_id == run_id:
            raise KeyError(run_id)

    def list_traces(self) -> list[str]:
        return [self._trace.run_id]

    def exists(self, run_id: str) -> bool:
        return self._trace.run_id == run_id


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description=f"Step {index}",
    )


def make_trace() -> RunTrace:
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata([make_step("step-2", 1), make_step("step-1", 0)]),
    )


def test_loader_loads_run_trace_from_repository() -> None:
    repository: TraceRepository = FakeRepository(make_trace())

    trace = ReplayTraceLoader(repository).load_from_repository("run-1")

    assert trace.run_id == "run-1"


def test_loader_loads_run_trace_from_object() -> None:
    trace = make_trace()

    loaded_trace = ReplayTraceLoader().load_from_object(trace)

    assert loaded_trace == trace


def test_loader_returns_ordered_steps() -> None:
    steps = ReplayTraceLoader().get_steps(make_trace())

    assert [step.step_id for step in steps] == ["step-1", "step-2"]


def test_loader_requires_repository_for_repository_loads() -> None:
    with pytest.raises(ReplayError, match="requires a repository"):
        ReplayTraceLoader().load_from_repository("run-1")


def test_loader_rejects_duplicate_step_ids() -> None:
    trace = RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata([make_step("step-1", 0), make_step("step-1", 1)]),
    )

    with pytest.raises(ReplayError, match="Duplicate replay step_id"):
        ReplayTraceLoader().load_from_object(trace)
