from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_tool_state
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_tools

STEP = {
    "step_id": "s1",
    "step_index": 1,
    "step_type": "tool",
    "timestamp": "2026-01-01T00:00:01Z",
    "description": "tool",
}


def test_diff_tool_state_compares_calls_results_and_failures() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "tools": [
                {
                    "step_index": 1,
                    "call": {
                        "tool_name": "search",
                        "arguments": {"q": "x"},
                        "invocation_time": "2026-01-01T00:00:01Z",
                        "step_id": "tool-1",
                    },
                    "result": {
                        "tool_name": "search",
                        "success": True,
                        "output": "ok",
                        "execution_time_ms": 5,
                        "step_id": "tool-1",
                    },
                }
            ],
        },
    )
    run_b = RunTrace(
        run_id="b",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="failed",
        metadata={
            "steps": [STEP],
            "tools": [
                {
                    "step_index": 1,
                    "call": {
                        "tool_name": "search",
                        "arguments": {"q": "x"},
                        "invocation_time": "2026-01-01T00:00:01Z",
                        "step_id": "tool-1",
                    },
                    "result": {
                        "tool_name": "search",
                        "success": False,
                        "output": "timeout",
                        "execution_time_ms": 10,
                        "step_id": "tool-1",
                    },
                },
                {
                    "step_index": 1,
                    "call": {
                        "tool_name": "lookup",
                        "arguments": {},
                        "invocation_time": "2026-01-01T00:00:02Z",
                        "step_id": "tool-2",
                    },
                },
            ],
        },
    )

    diff = diff_tool_state(reconstruct_tools(run_a, 1), reconstruct_tools(run_b, 1))

    assert diff.calls_added == ["tool-2:lookup"]
    assert diff.failures_added == ["tool-1"]
    assert diff.outcome_changes == ["tool-1"]
