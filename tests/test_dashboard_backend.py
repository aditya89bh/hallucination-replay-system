from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from hallucination_replay.dashboard import DashboardService
from hallucination_replay.models import RunTrace
from hallucination_replay.replay import ReplayController
from hallucination_replay.storage import FilesystemTraceRepository


def test_dashboard_service_aggregates_platform_state(tmp_path: Path) -> None:
    repository = FilesystemTraceRepository(tmp_path)
    trace = RunTrace(
        run_id="dashboard-run",
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
            ]
        },
    )
    repository.save_trace(trace)
    service = DashboardService(repository)
    replay = ReplayController.create(trace, "session-1")

    overview = service.overview(
        replay_sessions={"session-1": replay},
        analysis_reports={"analysis-1": {"run_id": "dashboard-run", "findings": [{}]}},
        hallucination_reports={
            "hallucination-1": {
                "run_id": "dashboard-run",
                "severity": "medium",
                "contradictions": [{}],
            }
        },
    )

    traces = cast(dict[str, object], overview["traces"])
    replay_overview = cast(dict[str, object], overview["replay"])
    analysis = cast(dict[str, object], overview["analysis"])
    hallucinations = cast(dict[str, object], overview["hallucinations"])
    replay_sessions = cast(list[dict[str, object]], replay_overview["sessions"])
    analysis_reports = cast(list[dict[str, object]], analysis["reports"])
    hallucination_reports = cast(list[dict[str, object]], hallucinations["reports"])

    assert traces["total"] == 1
    assert replay_sessions[0]["step_count"] == 1
    assert analysis_reports[0]["finding_count"] == 1
    assert hallucination_reports[0]["severity"] == "medium"
