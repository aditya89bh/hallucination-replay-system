from __future__ import annotations

from datetime import UTC, datetime

import pytest

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_prompt
from hallucination_replay.replay import steps_to_metadata


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-1", 0), make_step("step-2", 1)])
    metadata["context"] = [
        {"key": "goal", "value": "summarize", "source": "fixture", "step_index": 0},
    ]
    metadata["prompts"] = [
        {
            "step_index": 0,
            "system_prompt": "You are concise.",
            "user_prompt": "Summarize this.",
            "inputs": {"topic": "trace"},
        },
        {
            "step_index": 1,
            "system_prompt": "You are precise.",
            "user_prompt": "Refine summary.",
            "inputs": {"draft": "short"},
        },
    ]
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_prompt_returns_historical_prompt_state() -> None:
    prompt = reconstruct_prompt(make_trace(), 1)

    assert prompt.current_prompt is not None
    assert prompt.current_prompt.system_prompt == "You are precise."
    assert prompt.current_prompt.inputs == {"draft": "short"}
    assert [item.user_prompt for item in prompt.prompt_history] == [
        "Summarize this.",
        "Refine summary.",
    ]
    assert prompt.context_keys == ["goal"]


def test_reconstruct_prompt_supports_empty_prompt_history() -> None:
    trace = make_trace()
    trace.metadata["prompts"] = []

    prompt = reconstruct_prompt(trace, 0)

    assert prompt.current_prompt is None
    assert prompt.prompt_history == []


def test_reconstruct_prompt_rejects_invalid_prompt_metadata() -> None:
    trace = make_trace()
    trace.metadata["prompts"] = "invalid"

    with pytest.raises(ReplayError, match="prompts"):
        reconstruct_prompt(trace, 0)
