from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_reconstructed_states
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_state


def test_diff_reconstructed_states_reports_deterministic_changes() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
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
            "context": [{"step_index": 1, "key": "mode", "value": "safe"}],
        },
    )
    run_b = RunTrace(
        run_id="b",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
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
            "context": [
                {"step_index": 1, "key": "mode", "value": "fast"},
                {"step_index": 1, "key": "region", "value": "EU"},
            ],
        },
    )

    diff = diff_reconstructed_states(
        reconstruct_state(run_a, 1), reconstruct_state(run_b, 1)
    )

    assert diff.run_a_id == "a"
    assert diff.run_b_id == "b"
    assert [change.path for change in diff.modifications]
    assert [change.path for change in diff.additions]
    assert diff.removals == []
