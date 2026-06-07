from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import RunTrace, ToolCall


def test_model_from_dict_deserializes_payload() -> None:
    trace = RunTrace.from_dict(
        {
            "run_id": "run-1",
            "started_at": "2026-01-01T00:00:00Z",
            "completed_at": None,
            "status": "completed",
            "metadata": {"owner": "eval-team"},
        }
    )

    assert trace.run_id == "run-1"
    assert trace.started_at == datetime(2026, 1, 1, tzinfo=UTC)
    assert trace.status == "completed"
    assert trace.metadata == {"owner": "eval-team"}


def test_model_from_json_deserializes_payload() -> None:
    call = ToolCall.from_json(
        '{"tool_name":"search","arguments":{"query":"trace"},'
        '"invocation_time":"2026-01-01T00:00:00Z","step_id":"step-1"}'
    )

    assert call.tool_name == "search"
    assert call.arguments == {"query": "trace"}
    assert call.invocation_time == datetime(2026, 1, 1, tzinfo=UTC)
    assert call.step_id == "step-1"
