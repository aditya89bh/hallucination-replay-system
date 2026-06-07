from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import ContextSnapshot, diff_context_state
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import (
    reconstruct_context,
    reconstruct_conversation,
    reconstruct_prompt,
)

STEP = {
    "step_id": "s1",
    "step_index": 1,
    "step_type": "model",
    "timestamp": "2026-01-01T00:00:01Z",
    "description": "answer",
}


def test_diff_context_state_compares_context_prompt_and_conversation() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "context": [{"step_index": 1, "key": "mode", "value": "safe"}],
            "prompts": [{"step_index": 1, "system_prompt": "be careful"}],
            "conversation": [
                {
                    "step_index": 1,
                    "role": "user",
                    "content": "hello",
                    "timestamp": "2026-01-01T00:00:01Z",
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
            "context": [
                {"step_index": 1, "key": "mode", "value": "fast"},
                {"step_index": 1, "key": "region", "value": "EU"},
            ],
            "prompts": [{"step_index": 1, "system_prompt": "be fast"}],
            "conversation": [],
        },
    )

    diff = diff_context_state(
        ContextSnapshot(
            context=reconstruct_context(run_a, 1),
            prompt=reconstruct_prompt(run_a, 1),
            conversation=reconstruct_conversation(run_a, 1),
        ),
        ContextSnapshot(
            context=reconstruct_context(run_b, 1),
            prompt=reconstruct_prompt(run_b, 1),
            conversation=reconstruct_conversation(run_b, 1),
        ),
    )

    assert diff.context_added == ["region"]
    assert diff.context_modified == ["mode"]
    assert diff.prompt_changed is True
    assert diff.conversation_removed == ["1|user|hello"]
