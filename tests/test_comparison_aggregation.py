from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from hallucination_replay.diffing import compare_executions
from hallucination_replay.models import RunTrace


def test_compare_executions_aggregates_all_diff_sections() -> None:
    run_a = _trace("a", "completed", "safe")
    run_b = _trace("b", "failed", "fast")

    comparison = compare_executions(run_a, run_b)

    assert comparison.trace_diff.status_changed is True
    assert comparison.context_diff.context_modified == ["mode"]
    assert comparison.timeline_diff.run_a_order == ["s1"]
    assert comparison.state_diff.run_b_id == "b"


def _trace(run_id: str, status: Literal["completed", "failed"], mode: str) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=status,
        metadata={
            "steps": [
                {
                    "step_id": "s1",
                    "step_index": 1,
                    "step_type": "model",
                    "timestamp": "2026-01-01T00:00:01Z",
                    "description": "answer",
                }
            ],
            "context": [{"step_index": 1, "key": "mode", "value": mode}],
        },
    )
