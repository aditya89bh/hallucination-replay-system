"""HTML timeline viewer for replay steps."""

from __future__ import annotations

from html import escape

from hallucination_replay.models import RunTrace
from hallucination_replay.replay import ReplayTraceLoader


def render_timeline_viewer(trace: RunTrace) -> str:
    """Render ordered replay steps and navigation metadata as deterministic HTML."""
    steps = sorted(
        ReplayTraceLoader().get_steps(trace), key=lambda step: step.step_index
    )
    items = "\n".join(
        _render_step(
            position, len(steps), step.step_id, step.step_index, step.step_type
        )
        for position, step in enumerate(steps)
    )
    return (
        '<section class="timeline-viewer">\n'
        f"<h1>Timeline for {escape(trace.run_id)}</h1>\n"
        f'<p data-step-count="{len(steps)}">{len(steps)} replay steps</p>\n'
        '<ol class="timeline-steps">\n'
        f"{items}\n"
        "</ol>\n"
        "</section>"
    )


def _render_step(
    position: int, step_count: int, step_id: str, step_index: int, step_type: str
) -> str:
    previous_index = position - 1 if position > 0 else None
    next_index = position + 1 if position + 1 < step_count else None
    return (
        f'<li data-position="{position}" data-step-index="{step_index}" '
        f'data-previous="{previous_index}" data-next="{next_index}">'
        f'<span class="step-id">{escape(step_id)}</span> '
        f'<span class="step-type">{escape(step_type)}</span>'
        "</li>"
    )
