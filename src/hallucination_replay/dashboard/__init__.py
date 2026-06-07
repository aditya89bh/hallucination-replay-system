"""Lightweight dashboard backend and renderers."""

from hallucination_replay.dashboard.failure import render_failure_analysis_viewer
from hallucination_replay.dashboard.replay import render_replay_viewer
from hallucination_replay.dashboard.service import DashboardService
from hallucination_replay.dashboard.timeline import render_timeline_viewer

__all__ = [
    "DashboardService",
    "render_failure_analysis_viewer",
    "render_replay_viewer",
    "render_timeline_viewer",
]
