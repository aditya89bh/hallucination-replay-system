from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_memory_state
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_memory

STEP = {
    "step_id": "s1",
    "step_index": 1,
    "step_type": "memory",
    "timestamp": "2026-01-01T00:00:01Z",
    "description": "memory",
}


def test_diff_memory_state_compares_reads_writes_and_state() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "memory": [
                {
                    "step_index": 1,
                    "event": {
                        "event_type": "write",
                        "key": "city",
                        "value": "Paris",
                        "timestamp": "2026-01-01T00:00:01Z",
                    },
                }
            ],
        },
    )
    run_b = RunTrace(
        run_id="b",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "memory": [
                {
                    "step_index": 1,
                    "event": {
                        "event_type": "read",
                        "key": "city",
                        "value": "Paris",
                        "timestamp": "2026-01-01T00:00:01Z",
                    },
                },
                {
                    "step_index": 1,
                    "event": {
                        "event_type": "write",
                        "key": "city",
                        "value": "Berlin",
                        "timestamp": "2026-01-01T00:00:02Z",
                    },
                },
            ],
        },
    )

    diff = diff_memory_state(reconstruct_memory(run_a, 1), reconstruct_memory(run_b, 1))

    assert diff.reads_added == ["read|city|Paris"]
    assert diff.writes_added == ["write|city|Berlin"]
    assert diff.writes_removed == ["write|city|Paris"]
    assert diff.state_modified == ["city"]
