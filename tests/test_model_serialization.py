from __future__ import annotations

import json
from datetime import UTC, datetime

from hallucination_replay.models import RunTrace, ToolCall


def test_model_to_dict_returns_json_compatible_dictionary() -> None:
    started_at = datetime(2026, 1, 1, tzinfo=UTC)
    trace = RunTrace(run_id="run-1", started_at=started_at, status="running")

    payload = trace.to_dict()

    assert payload == {
        "run_id": "run-1",
        "started_at": "2026-01-01T00:00:00Z",
        "completed_at": None,
        "status": "running",
        "metadata": {},
    }


def test_model_to_json_returns_json_string() -> None:
    invocation_time = datetime(2026, 1, 1, tzinfo=UTC)
    call = ToolCall(
        tool_name="search",
        arguments={"query": "trace"},
        invocation_time=invocation_time,
        step_id="step-1",
    )

    payload = json.loads(call.to_json())

    assert payload == {
        "tool_name": "search",
        "arguments": {"query": "trace"},
        "invocation_time": "2026-01-01T00:00:00Z",
        "step_id": "step-1",
    }
