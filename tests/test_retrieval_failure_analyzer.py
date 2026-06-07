from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import FailureType, analyze_retrieval_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(metadata: dict[str, object]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="retrieval",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="retrieve",
    )
    base_metadata = steps_to_metadata([step])
    base_metadata.update(metadata)
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=base_metadata,
    )


def retrieval_record(documents: list[dict[str, object]]) -> dict[str, object]:
    return {
        "step_index": 0,
        "event": {
            "query": "project requirements",
            "retrieved_documents": documents,
            "retrieval_time_ms": 5.0,
            "source": "fixture",
        },
    }


def test_detects_no_retrieval_events() -> None:
    findings = analyze_retrieval_failures(make_trace({}), 0)

    assert findings[0].failure_type is FailureType.RETRIEVAL_FAILURE
    assert findings[0].message == "No retrieval events executed"


def test_detects_empty_retrieval_results() -> None:
    trace = make_trace({"retrievals": [retrieval_record([])]})

    findings = analyze_retrieval_failures(trace, 0)

    assert findings[0].message == "Empty retrieval results"


def test_detects_retrieval_coverage_gaps() -> None:
    trace = make_trace(
        {
            "retrievals": [
                retrieval_record([{"title": "Phase 6", "body": "analysis"}])
            ],
            "retrieval_requirements": ["memory evidence"],
        }
    )

    findings = analyze_retrieval_failures(trace, 0)

    assert findings[0].message == "Retrieval coverage gaps"
    assert findings[0].evidence == ["Missing required coverage: memory evidence"]
