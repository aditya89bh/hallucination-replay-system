from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.storage import TraceFilter, TraceIndexEntry, filter_traces


def make_entries() -> list[TraceIndexEntry]:
    return [
        TraceIndexEntry(
            run_id="run-1",
            status="completed",
            started_at=datetime(2026, 1, 1, tzinfo=UTC),
            agent_name="agent-a",
            tags=["smoke", "retrieval"],
        ),
        TraceIndexEntry(
            run_id="run-2",
            status="failed",
            started_at=datetime(2026, 1, 2, tzinfo=UTC),
            agent_name="agent-b",
            tags=["memory"],
        ),
    ]


def test_trace_filter_matches_status_agent_and_tags() -> None:
    trace_filter = TraceFilter(
        status="completed",
        agent_name="agent-a",
        tags=frozenset({"retrieval"}),
    )

    results = filter_traces(make_entries(), trace_filter)

    assert [entry.run_id for entry in results] == ["run-1"]


def test_trace_filter_matches_started_after() -> None:
    trace_filter = TraceFilter(started_after=datetime(2026, 1, 1, 12, tzinfo=UTC))

    results = filter_traces(make_entries(), trace_filter)

    assert [entry.run_id for entry in results] == ["run-2"]


def test_trace_filter_matches_started_before() -> None:
    trace_filter = TraceFilter(started_before=datetime(2026, 1, 2, tzinfo=UTC))

    results = filter_traces(make_entries(), trace_filter)

    assert [entry.run_id for entry in results] == ["run-1"]


def test_trace_filter_returns_empty_when_tags_do_not_match() -> None:
    trace_filter = TraceFilter(tags=frozenset({"missing"}))

    assert filter_traces(make_entries(), trace_filter) == []
