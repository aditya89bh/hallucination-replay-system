from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models.run_trace import RunTrace


def test_run_trace_accepts_required_fields() -> None:
    started_at = datetime(2026, 1, 1, tzinfo=UTC)

    trace = RunTrace(run_id="run-1", started_at=started_at, status="running")

    assert trace.run_id == "run-1"
    assert trace.started_at == started_at
    assert trace.completed_at is None
    assert trace.status == "running"
    assert trace.metadata == {}


def test_run_trace_rejects_invalid_status() -> None:
    started_at = datetime(2026, 1, 1, tzinfo=UTC)

    payload = {"run_id": "run-1", "started_at": started_at, "status": "unknown"}

    with pytest.raises(ValidationError, match="status"):
        RunTrace.model_validate(payload)
