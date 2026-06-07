from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.dashboard import render_timeline_viewer
from hallucination_replay.models import RunTrace


def test_timeline_viewer_renders_ordered_steps_and_navigation_metadata() -> None:
    html = render_timeline_viewer(
        RunTrace(
            run_id="timeline-run",
            started_at=datetime(2026, 1, 1, tzinfo=UTC),
            status="completed",
            metadata={
                "steps": [
                    {
                        "step_id": "s2",
                        "step_index": 2,
                        "step_type": "tool",
                        "timestamp": "2026-01-01T00:00:02Z",
                        "description": "second",
                    },
                    {
                        "step_id": "s1",
                        "step_index": 1,
                        "step_type": "model",
                        "timestamp": "2026-01-01T00:00:01Z",
                        "description": "first",
                    },
                ]
            },
        )
    )

    assert html.index("s1") < html.index("s2")
    assert 'data-step-count="2"' in html
    assert 'data-previous="None" data-next="1"' in html
    assert 'data-previous="0" data-next="None"' in html
