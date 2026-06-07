from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import analyze_validation_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(metadata: dict[str, object]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="validation",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="validation",
    )
    base_metadata = steps_to_metadata([step])
    base_metadata.update(metadata)
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=base_metadata,
    )


def validation_record(name: str, *, passed: bool) -> dict[str, object]:
    return {
        "step_index": 0,
        "event": {
            "validator_name": name,
            "passed": passed,
            "findings": ["bad"] if not passed else [],
            "timestamp": "2026-01-01T00:00:00Z",
        },
    }


def test_detects_validation_never_executed() -> None:
    findings = analyze_validation_failures(make_trace({}), 0)

    assert findings[0].message == "Validation never executed"


def test_detects_failed_validations_ignored() -> None:
    trace = make_trace(
        {
            "validations": [validation_record("schema", passed=False)],
            "ignored_validations": ["schema"],
        }
    )

    findings = analyze_validation_failures(trace, 0)

    assert findings[0].message == "Failed validations ignored"


def test_detects_validation_coverage_gaps() -> None:
    trace = make_trace(
        {
            "validations": [validation_record("schema", passed=True)],
            "validation_requirements": ["safety"],
        }
    )

    findings = analyze_validation_failures(trace, 0)

    assert findings[0].message == "Validation coverage gaps"
