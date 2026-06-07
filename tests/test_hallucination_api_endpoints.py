from __future__ import annotations

from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository

BENCHMARK_PATH = Path("benchmarks/hallucination/contradiction.json")


def test_hallucination_api_runs_and_returns_report(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    trace = RunTrace.from_json(BENCHMARK_PATH.read_text())
    repository.save_trace(trace)
    client = TestClient(create_app(repository=repository))

    response = client.post(
        "/hallucination/run",
        json={
            "run_id": "hallucination-contradiction",
            "step_index": 3,
            "report_id": "hallucination-report",
        },
    )
    report = client.get(
        "/hallucination/report", params={"report_id": "hallucination-report"}
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["severity"] == "medium"
    assert len(payload["contradictions"]) == 1
    assert "# Hallucination Report" in payload["markdown_report"]
    assert report.status_code == status.HTTP_200_OK
    assert report.json()["report_id"] == "hallucination-report"
