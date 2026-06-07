"""Compatibility exports for dashboard modules."""

from hallucination_replay.dashboard import (
    DashboardService,
    render_failure_analysis_viewer,
    render_hallucination_viewer,
    render_replay_viewer,
    render_timeline_viewer,
)

__all__ = [
    "DashboardService",
    "render_failure_analysis_viewer",
    "render_hallucination_viewer",
    "render_replay_viewer",
    "render_timeline_viewer",
]
