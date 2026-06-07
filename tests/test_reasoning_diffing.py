from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_reasoning_state
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_reasoning

EXPECTED_CONFIDENCE_DELTA = -0.3

STEP = {
    "step_id": "s1",
    "step_index": 1,
    "step_type": "reasoning",
    "timestamp": "2026-01-01T00:00:01Z",
    "description": "reasoning",
}


def test_diff_reasoning_state_compares_summaries_and_confidence_only() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "reasoning": [
                {
                    "step_index": 1,
                    "event": {
                        "reasoning_type": "planning",
                        "summary": "Use retrieved facts",
                        "confidence": 0.8,
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
            "reasoning": [
                {
                    "step_index": 1,
                    "event": {
                        "reasoning_type": "decision",
                        "summary": "Proceed despite missing evidence",
                        "confidence": 0.5,
                        "timestamp": "2026-01-01T00:00:01Z",
                    },
                }
            ],
        },
    )

    diff = diff_reasoning_state(
        reconstruct_reasoning(run_a, 1), reconstruct_reasoning(run_b, 1)
    )

    assert diff.event_types_added == ["decision"]
    assert diff.event_types_removed == ["planning"]
    assert diff.confidence_delta == EXPECTED_CONFIDENCE_DELTA
