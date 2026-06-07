from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.analysis import analyze_memory_failures
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata


def make_trace(metadata: dict[str, object]) -> RunTrace:
    step = AgentStep(
        step_id="step-0",
        step_index=0,
        step_type="memory",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        description="memory",
    )
    base_metadata = steps_to_metadata([step])
    base_metadata.update(metadata)
    return RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=base_metadata,
    )


def memory_event(event_type: str, key: str, value: object) -> dict[str, object]:
    return {
        "step_index": 0,
        "event": {
            "event_type": event_type,
            "key": key,
            "value": value,
            "timestamp": "2026-01-01T00:00:00Z",
        },
    }


def test_detects_missing_memory_reads() -> None:
    trace = make_trace({"memory_expected_reads": ["profile"]})

    findings = analyze_memory_failures(trace, 0)

    assert findings[0].message == "Missing memory reads"


def test_detects_stale_memory_access() -> None:
    trace = make_trace(
        {
            "memory": [memory_event("read", "profile", "old")],
            "stale_memory_keys": ["profile"],
        }
    )

    findings = analyze_memory_failures(trace, 0)

    assert findings[0].message == "Stale memory access"


def test_detects_memory_state_inconsistencies() -> None:
    trace = make_trace(
        {
            "memory": [memory_event("write", "answer", "41")],
            "memory_expected_state": {"answer": "42"},
        }
    )

    findings = analyze_memory_failures(trace, 0)

    assert findings[0].message == "Memory state inconsistencies"
    assert "expected '42'" in findings[0].evidence[0]
