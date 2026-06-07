from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_state
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
        {"key": "task", "value": "answer", "source": "fixture", "step_index": 0}
    ]
    metadata["prompts"] = [{"step_index": 0, "user_prompt": "Question"}]
    metadata["memory"] = [
        {
            "step_index": 1,
            "event": {
                "event_type": "write",
                "key": "summary",
                "value": "done",
                "timestamp": "2026-01-01T00:01:00Z",
            },
        }
    ]
    metadata["retrievals"] = []
    metadata["tools"] = []
    metadata["validations"] = []
    metadata["reasoning"] = []
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruct_state_aggregates_reconstruction_sections() -> None:
    state = reconstruct_state(make_trace(), 1)

    assert state.trace_id == "run-1"
    assert state.context.current_step.step_id == "step-2"
    assert state.prompt.current_prompt is not None
    assert state.prompt.current_prompt.user_prompt == "Question"
    assert state.memory.state == {"summary": "done"}
    assert state.retrieval.events == []
    assert state.tools.calls == []
    assert state.validation.records == []
    assert state.reasoning.summaries == []


def test_reconstructed_state_is_serializable() -> None:
    state = reconstruct_state(make_trace(), 1)

    assert "run-1" in state.to_json()
