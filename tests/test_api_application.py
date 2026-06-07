from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app


def test_fastapi_app_exposes_health_and_version() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    version = client.get("/version")

    assert health.status_code == status.HTTP_200_OK
    assert health.json() == {"status": "ok"}
    assert version.status_code == status.HTTP_200_OK
    assert version.json()["name"] == "hallucination-replay-system"
    assert isinstance(version.json()["version"], str)
