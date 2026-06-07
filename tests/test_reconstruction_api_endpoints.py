from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository


def test_reconstruction_api_returns_context_memory_and_full_state(
    tmp_path: Path,
) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(_trace())
    client = TestClient(create_app(repository=repository))
    payload = {"run_id": "reconstruct-run", "step_index": 1}

    context = client.post("/reconstruction/context", json=payload)
    memory = client.post("/reconstruction/memory", json=payload)
    state_response = client.post("/reconstruction/state", json=payload)

    assert context.status_code == status.HTTP_200_OK
    assert context.json()["entries"][0]["key"] == "topic"
    assert memory.status_code == status.HTTP_200_OK
    assert memory.json()["state"] == {"topic": "refunds"}
    assert state_response.status_code == status.HTTP_200_OK
    assert state_response.json()["trace_id"] == "reconstruct-run"


def _trace() -> RunTrace:
    return RunTrace(
        run_id="reconstruct-run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={
            "steps": [
                {
                    "step_id": "s1",
                    "step_index": 1,
                    "step_type": "model",
                    "timestamp": "2026-01-01T00:00:01Z",
                    "description": "answer",
                }
            ],
            "context": [{"step_index": 1, "key": "topic", "value": "refunds"}],
            "memory": [
                {
                    "step_index": 1,
                    "event": {
                        "event_type": "write",
                        "key": "topic",
                        "value": "refunds",
                        "timestamp": "2026-01-01T00:00:01Z",
                    },
                }
            ],
        },
    )
