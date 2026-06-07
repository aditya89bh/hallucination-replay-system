from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import analyze_output_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(metadata: dict[str, object]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="output",
    )
    base_metadata = steps_to_metadata([step])
    base_metadata.update(metadata)
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=base_metadata,
    )


def test_detects_empty_outputs() -> None:
    trace = make_trace({"outputs": [{"step_index": 0, "content": "", "final": True}]})

    findings = analyze_output_failures(trace, 0)

    assert findings[0].message == "Empty outputs"


def test_detects_incomplete_outputs() -> None:
    trace = make_trace(
        {
            "outputs": [{"step_index": 0, "content": "partial", "final": True}],
            "incomplete_outputs": ["Missing requested citations"],
        }
    )

    findings = analyze_output_failures(trace, 0)

    assert findings[0].message == "Incomplete outputs"


def test_detects_missing_final_response_artifacts() -> None:
    trace = make_trace({"outputs": [{"step_index": 0, "content": "draft"}]})

    findings = analyze_output_failures(trace, 0)

    assert findings[0].message == "Missing final response artifacts"
