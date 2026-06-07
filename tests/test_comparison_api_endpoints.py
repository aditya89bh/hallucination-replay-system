from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository


def test_comparison_api_compares_and_returns_report(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    repository.save_trace(_trace("run-a", "completed", "safe"))
    repository.save_trace(_trace("run-b", "failed", "fast"))
    client = TestClient(create_app(repository=repository))

    response = client.post(
        "/compare",
        json={"run_a_id": "run-a", "run_b_id": "run-b", "report_id": "compare-1"},
    )
    report = client.get("/compare/report", params={"report_id": "compare-1"})

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["json_report"]["status_changed"] is True
    assert "# Execution Comparison Report" in payload["markdown_report"]
    assert report.status_code == status.HTTP_200_OK
    assert report.json()["report_id"] == "compare-1"


def _trace(
    run_id: str, status_value: Literal["completed", "failed"], mode: str
) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=status_value,
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
            "context": [{"step_index": 1, "key": "mode", "value": mode}],
        },
    )
