from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.hallucination import Evidence, extract_evidence
from hallucination_replay.models import RunTrace


def test_evidence_model_serializes() -> None:
    evidence = Evidence(
        evidence_id="e1", text="Paris is in France", source="retrieval", source_step=1
    )

    assert evidence.to_dict()["source"] == "retrieval"


def test_extract_evidence_from_retrieval_tool_and_memory() -> None:
    trace = RunTrace(
        run_id="run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "retrievals": [
                {"step_index": 1, "results": [{"text": "Paris is in France"}]}
            ],
            "tools": [{"step_index": 2, "result": {"output": "weather: sunny"}}],
            "memory": [{"step_index": 3, "value": "User lives in Paris"}],
        },
    )

    evidence = extract_evidence(trace, step_index=2)

    assert [item.source for item in evidence] == ["retrieval", "tool"]
    assert [item.text for item in evidence] == ["Paris is in France", "weather: sunny"]
