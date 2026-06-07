from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_timelines
from hallucination_replay.models import RunTrace


def test_diff_timelines_compares_order_missing_and_additional_steps() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [
                _step("s1", 1),
                _step("s2", 2),
                _step("s3", 3),
            ]
        },
    )
    run_b = RunTrace(
        run_id="b",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="failed",
        metadata={
            "steps": [
                _step("s2", 1),
                _step("s1", 2),
                _step("s4", 3),
            ]
        },
    )

    diff = diff_timelines(run_a, run_b)

    assert diff.missing_steps == ["s3"]
    assert diff.additional_steps == ["s4"]
    assert diff.order_changed is True
    assert diff.run_b_order == ["s2", "s1", "s4"]


def _step(step_id: str, step_index: int) -> dict[str, object]:
    return {
        "step_id": step_id,
        "step_index": step_index,
        "step_type": "model",
        "timestamp": "2026-01-01T00:00:01Z",
        "description": step_id,
    }
