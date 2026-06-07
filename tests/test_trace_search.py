from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.storage import TraceIndex, TraceIndexEntry, TraceSearch


def make_index() -> TraceIndex:
    return TraceIndex(
        entries={
            "alpha-run": TraceIndexEntry(
                run_id="alpha-run",
                status="completed",
                started_at=datetime(2026, 1, 1, tzinfo=UTC),
                agent_name="agent-a",
                tags=["smoke", "retrieval"],
            ),
            "beta-run": TraceIndexEntry(
                run_id="beta-run",
                status="failed",
                started_at=datetime(2026, 1, 2, tzinfo=UTC),
                agent_name="agent-b",
                tags=["memory"],
            ),
        }
    )


def test_search_by_run_id_substring() -> None:
    search = TraceSearch(make_index())

    results = search.by_run_id_substring("ALPHA")

    assert [entry.run_id for entry in results] == ["alpha-run"]


def test_search_by_agent_name() -> None:
    search = TraceSearch(make_index())

    results = search.by_agent_name("agent-b")

    assert [entry.run_id for entry in results] == ["beta-run"]


def test_search_by_tag() -> None:
    search = TraceSearch(make_index())

    results = search.by_tag("retrieval")

    assert [entry.run_id for entry in results] == ["alpha-run"]


def test_search_by_status() -> None:
    search = TraceSearch(make_index())

    results = search.by_status("failed")

    assert [entry.run_id for entry in results] == ["beta-run"]
