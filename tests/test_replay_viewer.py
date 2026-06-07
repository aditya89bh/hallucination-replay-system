from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.dashboard import render_replay_viewer
from hallucination_replay.models import RunTrace
from hallucination_replay.replay import ReplayController


def test_replay_viewer_displays_current_step_position_and_snapshot() -> None:
    controller = ReplayController.create(_trace(), "replay-session")
    controller.move_forward()

    html = render_replay_viewer(controller)

    assert 'data-position="1"' in html
    assert 'data-step-count="2"' in html
    assert "s2 (tool)" in html
    assert 'data-snapshot-id="replay-session:1"' in html


def _trace() -> RunTrace:
    return RunTrace(
        run_id="replay-viewer-run",
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
