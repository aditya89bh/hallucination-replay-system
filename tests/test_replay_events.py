from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.replay import (
    CheckpointCreated,
    ReplayEventStream,
    SnapshotCreated,
    StepEntered,
    StepExited,
)

EVENT_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def test_replay_event_stream_records_events_in_order() -> None:
    stream = ReplayEventStream()
    entered = StepEntered(
        session_id="session-1",
        trace_id="run-1",
        position=0,
        timestamp=EVENT_TIME,
        step_id="step-1",
    )
    exited = StepExited(
        session_id="session-1",
        trace_id="run-1",
        position=0,
        timestamp=EVENT_TIME,
        step_id="step-1",
    )

    stream.emit(entered)
    stream.emit(exited)

    assert stream.list_events() == [entered, exited]


def test_checkpoint_created_event() -> None:
    event = CheckpointCreated(
        session_id="session-1",
        trace_id="run-1",
        position=0,
        timestamp=EVENT_TIME,
        checkpoint_id="checkpoint-1",
    )

    assert event.event_type == "checkpoint_created"
    assert event.checkpoint_id == "checkpoint-1"


def test_snapshot_created_event() -> None:
    event = SnapshotCreated(
        session_id="session-1",
        trace_id="run-1",
        position=0,
        timestamp=EVENT_TIME,
        snapshot_id="snapshot-1",
    )

    assert event.event_type == "snapshot_created"
    assert event.snapshot_id == "snapshot-1"
