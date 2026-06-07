from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import (
    diff_replay_positions,
    generate_markdown_report,
    reconstruct_state,
)
from hallucination_replay.replay import ReplayController, steps_to_metadata

STEP_ONE = 1


def make_step(
    step_id: str,
    index: int,
    step_type: Literal[
        "model", "tool", "retrieval", "memory", "validation", "reasoning"
    ] = "model",
) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type=step_type,
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata(
        [
            make_step("step-0", 0),
            make_step("step-1", 1, "memory"),
        ]
    )
    metadata["context"] = [
        {"key": "goal", "value": "answer", "source": "fixture", "step_index": 0}
    ]
    metadata["memory"] = [
        {
            "step_index": 1,
            "event": {
                "event_type": "write",
                "key": "answer",
                "value": "42",
                "timestamp": "2026-01-01T00:01:00Z",
            },
        }
    ]
    metadata["prompts"] = [{"step_index": 0, "user_prompt": "What is known?"}]
    return RunTrace(
        run_id="integration-run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_reconstruction_end_to_end(tmp_path: Path) -> None:
    trace = make_trace()
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(trace.to_json(), encoding="utf-8")
    loaded_trace = RunTrace.from_json(trace_path.read_text(encoding="utf-8"))

    controller = ReplayController.create(loaded_trace, "reconstruction-session")
    controller.move_forward()
    assert controller.session.current_position == STEP_ONE

    state = reconstruct_state(loaded_trace, STEP_ONE)
    diff = diff_replay_positions(loaded_trace, 0, STEP_ONE)
    report = generate_markdown_report(state)

    assert state.memory.state == {"answer": "42"}
    assert [section.section for section in diff.changed_sections]
    assert "# Reconstruction Report: integration-run" in report
    assert json.loads(state.to_json())["trace_id"] == "integration-run"
