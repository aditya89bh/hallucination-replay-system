from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_state, visualize_state
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="memory",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description=step_id,
    )


def test_visualize_state_returns_deterministic_summary() -> None:
    metadata = steps_to_metadata([make_step("step-1", 0)])
    metadata["memory"] = [
        {
            "step_index": 0,
            "event": {
                "event_type": "write",
                "key": "answer",
                "value": "42",
                "timestamp": "2026-01-01T00:00:00Z",
            },
        }
    ]
    trace = RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )
    state = reconstruct_state(trace, 0)

    rendered = visualize_state(state)

    assert rendered == "\n".join(
        [
            "Reconstructed State: run-1 @ step 0",
            "Current step: step-1",
            "Context entries: 0",
            "Prompt history: 0",
            "Memory keys: answer",
            "Retrieval documents: 0",
            "Tool calls: 0",
            "Validation checks: 0",
            "Reasoning summaries: 0",
        ]
    )
