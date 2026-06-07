from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_traces
from hallucination_replay.models import RunTrace


def test_diff_traces_compares_metadata_status_and_step_counts() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={"steps": [{"step_index": 0}], "model": "small"},
    )
    run_b = RunTrace(
        run_id="b",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="failed",
        metadata={"steps": [{"step_index": 0}, {"step_index": 1}], "model": "large"},
    )

    diff = diff_traces(run_a, run_b)

    assert diff.run_a_id == "a"
    assert diff.run_b_id == "b"
    assert diff.status_changed is True
    assert diff.step_count_delta == 1
    assert list(diff.metadata_changes) == ["model", "steps"]
    assert diff.metadata_changes["model"] == {"run_a": "small", "run_b": "large"}
