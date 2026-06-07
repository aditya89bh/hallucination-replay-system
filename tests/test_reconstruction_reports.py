from __future__ import annotations

import json
from datetime import UTC, datetime

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import (
    generate_json_report,
    generate_markdown_report,
    generate_state_summary_report,
    reconstruct_state,
)
from hallucination_replay.replay import steps_to_metadata


def make_step() -> AgentStep:
    return AgentStep(
        step_id="step-1",
        step_index=0,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="step-1",
    )


def make_trace() -> RunTrace:
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata([make_step()]),
    )


def test_generate_markdown_report() -> None:
    report = generate_markdown_report(reconstruct_state(make_trace(), 0))

    assert report.startswith("# Reconstruction Report: run-1")
    assert "Current step: step-1" in report


def test_generate_json_report() -> None:
    report = generate_json_report(reconstruct_state(make_trace(), 0))

    assert json.loads(report)["trace_id"] == "run-1"


def test_generate_state_summary_report() -> None:
    report = generate_state_summary_report(reconstruct_state(make_trace(), 0))

    assert report == {
        "trace_id": "run-1",
        "step_index": 0,
        "current_step_id": "step-1",
        "context_entry_count": 0,
        "memory_key_count": 0,
        "retrieval_document_count": 0,
        "tool_call_count": 0,
        "validation_count": 0,
        "reasoning_summary_count": 0,
    }
