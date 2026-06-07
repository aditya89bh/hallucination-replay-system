from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import FailureType, analyze_intent_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(metadata: dict[str, object]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="step",
    )
    base_metadata = steps_to_metadata([step])
    base_metadata.update(metadata)
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=base_metadata,
    )


def test_detects_missing_user_objective() -> None:
    findings = analyze_intent_failures(make_trace({}), 0)

    assert findings[0].failure_type is FailureType.INTENT_FAILURE
    assert findings[0].message == "Missing user objective"


def test_detects_conflicting_objectives() -> None:
    trace = make_trace(
        {
            "prompts": [{"step_index": 0, "user_prompt": "Summarize A"}],
            "intent": {"conflicts": ["User asked for A and B simultaneously"]},
        }
    )

    findings = analyze_intent_failures(trace, 0)

    assert [finding.message for finding in findings] == [
        "Conflicting objectives captured"
    ]


def test_detects_incomplete_intent_capture() -> None:
    trace = make_trace(
        {
            "intent": {
                "objectives": ["Summarize the trace"],
                "incomplete": [{"step_index": 0, "value": "Missing output format"}],
            }
        }
    )

    findings = analyze_intent_failures(trace, 0)

    assert findings[0].message == "Incomplete intent capture"
    assert findings[0].evidence == ["Missing output format"]
