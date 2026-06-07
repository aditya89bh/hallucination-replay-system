from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.storage import (
    TraceIndex,
    TraceIndexEntry,
    TraceRetentionPolicy,
)


def make_index() -> TraceIndex:
    return TraceIndex(
        entries={
            "old": TraceIndexEntry(
                run_id="old",
                status="completed",
                started_at=datetime(2026, 1, 1, tzinfo=UTC),
            ),
            "middle": TraceIndexEntry(
                run_id="middle",
                status="completed",
                started_at=datetime(2026, 1, 5, tzinfo=UTC),
            ),
            "new": TraceIndexEntry(
                run_id="new",
                status="completed",
                started_at=datetime(2026, 1, 10, tzinfo=UTC),
            ),
        }
    )


def test_retention_policy_selects_traces_by_max_age() -> None:
    policy = TraceRetentionPolicy(max_age_days=7)

    selected = policy.select_traces_for_deletion(
        make_index(), datetime(2026, 1, 10, tzinfo=UTC)
    )

    assert selected == ["old"]


def test_retention_policy_selects_oldest_traces_over_max_traces() -> None:
    policy = TraceRetentionPolicy(max_traces=2)

    selected = policy.select_traces_for_deletion(
        make_index(), datetime(2026, 1, 10, tzinfo=UTC)
    )

    assert selected == ["old"]


def test_retention_policy_combines_age_and_count_selection() -> None:
    policy = TraceRetentionPolicy(max_age_days=3, max_traces=1, dry_run=False)

    selected = policy.select_traces_for_deletion(
        make_index(), datetime(2026, 1, 10, tzinfo=UTC)
    )

    assert selected == ["middle", "old"]
    assert policy.dry_run is False
