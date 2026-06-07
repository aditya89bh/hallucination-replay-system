from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import diff_retrieval_state
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_retrieval

STEP = {
    "step_id": "s1",
    "step_index": 1,
    "step_type": "retrieval",
    "timestamp": "2026-01-01T00:00:01Z",
    "description": "retrieve",
}


def test_diff_retrieval_state_compares_queries_documents_and_coverage() -> None:
    run_a = RunTrace(
        run_id="a",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "retrievals": [
                {
                    "step_index": 1,
                    "event": {
                        "query": "refund policy",
                        "retrieved_documents": [
                            {"id": "doc-1", "text": "Refunds allowed"}
                        ],
                        "retrieval_time_ms": 5,
                        "source": "kb",
                    },
                }
            ],
        },
    )
    run_b = RunTrace(
        run_id="b",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [STEP],
            "retrievals": [
                {
                    "step_index": 1,
                    "event": {
                        "query": "refund deadline",
                        "retrieved_documents": [
                            {"id": "doc-2", "text": "Refunds close in 30 days"},
                            {"id": "doc-3", "text": "Escalations need approval"},
                        ],
                        "retrieval_time_ms": 6,
                        "source": "kb",
                    },
                }
            ],
        },
    )

    diff = diff_retrieval_state(
        reconstruct_retrieval(run_a, 1), reconstruct_retrieval(run_b, 1)
    )

    assert diff.queries_added == ["refund deadline"]
    assert diff.queries_removed == ["refund policy"]
    assert diff.documents_added == ["doc-2", "doc-3"]
    assert diff.documents_removed == ["doc-1"]
    assert diff.coverage_delta == 1
