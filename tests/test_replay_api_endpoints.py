from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository


def test_replay_api_loads_navigates_and_jumps(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(_trace())
    client = TestClient(create_app(repository=repository))

    loaded = client.post(
        "/replay/load", json={"run_id": "replay-run", "session_id": "s"}
    )
    next_response = client.post("/replay/next", json={"session_id": "s"})
    previous = client.post("/replay/previous", json={"session_id": "s"})
    jumped = client.post("/replay/jump", json={"session_id": "s", "step_index": 1})

    assert loaded.status_code == status.HTTP_200_OK
    assert loaded.json()["current_position"] == 0
    assert next_response.status_code == status.HTTP_200_OK
    assert next_response.json()["current_step"]["step_id"] == "s2"
    assert previous.json()["current_step"]["step_id"] == "s1"
    assert jumped.json()["current_position"] == 1


def _trace() -> RunTrace:
    return RunTrace(
        run_id="replay-run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [
                {
                    "step_id": "s1",
                    "step_index": 1,
                    "step_type": "model",
                    "timestamp": "2026-01-01T00:00:01Z",
                    "description": "first",
                },
                {
                    "step_id": "s2",
                    "step_index": 2,
                    "step_type": "tool",
                    "timestamp": "2026-01-01T00:00:02Z",
                    "description": "second",
                },
            ]
        },
    )
