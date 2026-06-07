from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.replay import ReplaySession


def test_replay_session_accepts_required_fields() -> None:
    created_at = datetime(2026, 1, 1, tzinfo=UTC)

    session = ReplaySession(
        session_id="session-1",
        trace_id="run-1",
        current_position=0,
        created_at=created_at,
    )

    assert session.session_id == "session-1"
    assert session.trace_id == "run-1"
    assert session.current_position == 0
    assert session.created_at == created_at


def test_replay_session_defaults_current_position() -> None:
    session = ReplaySession(
        session_id="session-1",
        trace_id="run-1",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert session.current_position == 0


def test_replay_session_rejects_negative_position() -> None:
    payload = {
        "session_id": "session-1",
        "trace_id": "run-1",
        "current_position": -1,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }

    with pytest.raises(ValidationError, match="current_position"):
        ReplaySession.model_validate(payload)
