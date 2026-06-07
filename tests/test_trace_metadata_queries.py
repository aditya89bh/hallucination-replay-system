from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.storage import TraceIndex, TraceIndexEntry


def make_index() -> TraceIndex:
    return TraceIndex(
        entries={
            "run-1": TraceIndexEntry(
                run_id="run-1",
                status="completed",
                started_at=datetime(2026, 1, 1, tzinfo=UTC),
                agent_name="agent-a",
                tags=["retrieval", "smoke"],
            ),
            "run-2": TraceIndexEntry(
                run_id="run-2",
                status="failed",
                started_at=datetime(2026, 1, 2, tzinfo=UTC),
                agent_name="agent-a",
                tags=["memory"],
            ),
            "run-3": TraceIndexEntry(
                run_id="run-3",
                status="failed",
                started_at=datetime(2026, 1, 3, tzinfo=UTC),
                agent_name="agent-b",
                tags=["retrieval"],
            ),
        }
    )


def test_count_by_status() -> None:
    assert make_index().count_by_status() == {"completed": 1, "failed": 2}


def test_count_by_agent_name() -> None:
    assert make_index().count_by_agent_name() == {"agent-a": 2, "agent-b": 1}


def test_list_unique_tags() -> None:
    assert make_index().list_unique_tags() == ["memory", "retrieval", "smoke"]


def test_list_unique_agents() -> None:
    assert make_index().list_unique_agents() == ["agent-a", "agent-b"]
