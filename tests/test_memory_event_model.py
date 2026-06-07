from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models.memory_event import MemoryEvent


def test_memory_read_event_accepts_required_fields() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    event = MemoryEvent(
        event_type="read",
        key="user.preference",
        value="concise",
        timestamp=timestamp,
    )

    assert event.event_type == "read"
    assert event.key == "user.preference"
    assert event.value == "concise"
    assert event.timestamp == timestamp


def test_memory_write_event_accepts_required_fields() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    event = MemoryEvent(
        event_type="write",
        key="task.status",
        value={"state": "completed"},
        timestamp=timestamp,
    )

    assert event.event_type == "write"
    assert event.value == {"state": "completed"}


def test_memory_event_rejects_invalid_event_type() -> None:
    payload = {
        "event_type": "delete",
        "key": "task.status",
        "value": None,
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
    }

    with pytest.raises(ValidationError, match="event_type"):
        MemoryEvent.model_validate(payload)
