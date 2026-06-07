from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import analyze_tool_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(tools: list[dict[str, object]]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="tool",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="tool",
    )
    metadata = steps_to_metadata([step])
    metadata["tools"] = tools
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def tool_record(result: dict[str, object] | None) -> dict[str, object]:
    record: dict[str, object] = {
        "step_index": 0,
        "call": {
            "tool_name": "search",
            "arguments": {"query": "x"},
            "invocation_time": "2026-01-01T00:00:00Z",
            "step_id": "step-0",
        },
    }
    if result is not None:
        record["result"] = result
    return record


def result(tool_name: str, *, success: bool) -> dict[str, object]:
    return {
        "tool_name": tool_name,
        "success": success,
        "output": {},
        "execution_time_ms": 1.0,
        "step_id": "step-0",
    }


def test_detects_failed_tool_executions() -> None:
    findings = analyze_tool_failures(
        make_trace([tool_record(result("search", success=False))]), 0
    )

    assert findings[0].message == "Failed tool executions"


def test_detects_missing_tool_results() -> None:
    findings = analyze_tool_failures(make_trace([tool_record(None)]), 0)

    assert findings[0].message == "Missing tool results"


def test_detects_tool_call_result_mismatches() -> None:
    findings = analyze_tool_failures(
        make_trace([tool_record(result("browser", success=True))]), 0
    )

    assert findings[0].message == "Tool call/result mismatches"
