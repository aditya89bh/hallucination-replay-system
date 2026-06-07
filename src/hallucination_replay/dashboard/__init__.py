"""Lightweight dashboard backend and renderers."""

from hallucination_replay.dashboard.service import DashboardService
from hallucination_replay.dashboard.timeline import render_timeline_viewer

__all__ = ["DashboardService", "render_timeline_viewer"]
