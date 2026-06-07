from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository


def test_trace_api_endpoints_store_list_and_load_traces(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    client = TestClient(create_app(repository=repository))
    trace = RunTrace(
        run_id="api-run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata={"steps": []},
    )

    created = client.post("/traces", json=trace.to_dict())
    listed = client.get("/traces")
    loaded = client.get("/traces/api-run")
    missing = client.get("/traces/missing")

    assert created.status_code == status.HTTP_201_CREATED
    assert created.json() == {"run_id": "api-run"}
    assert listed.status_code == status.HTTP_200_OK
    assert listed.json() == {"run_ids": ["api-run"]}
    assert loaded.status_code == status.HTTP_200_OK
    assert loaded.json()["run_id"] == "api-run"
    assert missing.status_code == status.HTTP_404_NOT_FOUND
