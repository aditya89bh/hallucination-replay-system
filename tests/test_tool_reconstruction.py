from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_tools
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="tool",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["tools"] = [
        {
            "step_index": 0,
            "call": {
                "tool_name": "search",
                "arguments": {"query": "trace"},
                "invocation_time": "2026-01-01T00:00:00Z",
                "step_id": "step-1",
            },
            "result": {
                "tool_name": "search",
                "success": True,
                "output": {"hits": 1},
                "execution_time_ms": 3.0,
                "step_id": "step-1",
            },
        },
        {
            "step_index": 1,
            "call": {
                "tool_name": "calc",
                "arguments": {"expr": "1+1"},
                "invocation_time": "2026-01-01T00:01:00Z",
                "step_id": "step-2",
            },
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_tools_returns_calls_results_and_timeline() -> None:
    tools = reconstruct_tools(make_trace(), 1)

    assert [call.tool_name for call in tools.calls] == ["search", "calc"]
    assert [result.tool_name for result in tools.results] == ["search"]
    assert [item.status for item in tools.timeline] == ["success", "pending"]


def test_reconstruct_tools_filters_future_calls() -> None:
    tools = reconstruct_tools(make_trace(), 0)

    assert [call.tool_name for call in tools.calls] == ["search"]


def test_reconstruct_tools_rejects_invalid_metadata() -> None:
    trace = make_trace()
    trace.metadata["tools"] = "invalid"

    with pytest.raises(ReplayError, match="tools"):
        reconstruct_tools(trace, 0)
