from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository


def test_failure_analysis_api_runs_and_returns_report(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(_trace())
    client = TestClient(create_app(repository=repository))

    response = client.post(
        "/analysis/run",
        json={"run_id": "analysis-run", "step_index": 1, "report_id": "report-1"},
    )
    report = client.get("/analysis/report", params={"report_id": "report-1"})

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    messages = {finding["message"] for finding in payload["findings"]}
    assert "No retrieval events executed" in messages
    assert "# Failure Analysis Report" in payload["markdown_report"]
    assert report.status_code == status.HTTP_200_OK
    assert report.json()["report_id"] == "report-1"


def _trace() -> RunTrace:
    return RunTrace(
        run_id="analysis-run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="failed",
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
            "memory_expected_reads": ["profile"],
            "outputs": [{"step_index": 1, "content": "draft"}],
        },
    )
