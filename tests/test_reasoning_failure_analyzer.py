from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import analyze_reasoning_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(metadata: dict[str, object]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="reasoning",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="reasoning",
    )
    base_metadata = steps_to_metadata([step])
    base_metadata.update(metadata)
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=base_metadata,
    )


def reasoning_record(index: int, confidence: float, summary: str) -> dict[str, object]:
    return {
        "step_index": index,
        "event": {
            "reasoning_type": "decision",
            "summary": summary,
            "confidence": confidence,
            "timestamp": f"2026-01-01T00:0{index}:00Z",
        },
    }


def test_detects_missing_reasoning_records() -> None:
    findings = analyze_reasoning_failures(make_trace({}), 0)

    assert findings[0].message == "Missing reasoning records"


def test_detects_confidence_collapse() -> None:
    trace = make_trace(
        {"reasoning": [reasoning_record(0, 0.9, "ok"), reasoning_record(0, 0.3, "bad")]}
    )

    findings = analyze_reasoning_failures(trace, 0)

    assert findings[0].message == "Confidence collapse"


def test_detects_inconsistent_reasoning_summaries_without_chain_of_thought() -> None:
    trace = make_trace(
        {
            "reasoning": [reasoning_record(0, 0.8, "summary only")],
            "inconsistent_reasoning_summaries": [
                "Summary contradicts earlier decision"
            ],
        }
    )

    findings = analyze_reasoning_failures(trace, 0)

    assert findings[0].message == "Inconsistent reasoning summaries"
    assert "chain" not in findings[0].metadata
