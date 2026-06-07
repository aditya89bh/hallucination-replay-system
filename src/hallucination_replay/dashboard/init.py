"""Compatibility exports for dashboard modules."""

from hallucination_replay.dashboard import (
    DashboardService,
    render_replay_viewer,
    render_timeline_viewer,
)

__all__ = ["DashboardService", "render_replay_viewer", "render_timeline_viewer"]
