"""HTML replay viewer."""

from __future__ import annotations

from html import escape

from hallucination_replay.replay import ReplayController
from hallucination_replay.replay.snapshots import create_replay_snapshot


def render_replay_viewer(controller: ReplayController) -> str:
    """Render current replay position, current step, and snapshot summary."""
    current_step = controller.current_step()
    snapshot = create_replay_snapshot(
        controller.session,
        current_step,
        snapshot_id=f"{controller.session.session_id}:{controller.session.current_position}",
    )
    step_summary = (
        "No current step"
        if current_step is None
        else f"{current_step.step_id} ({current_step.step_type})"
    )
    return (
        '<section class="replay-viewer">\n'
        f"<h1>Replay {escape(controller.session.session_id)}</h1>\n"
        f'<p data-run-id="{escape(controller.trace.run_id)}" '
        f'data-position="{controller.session.current_position}" '
        f'data-step-count="{controller.step_count}">'
        f"Position {controller.session.current_position} of {controller.step_count}"
        "</p>\n"
        f'<div class="current-step">{escape(step_summary)}</div>\n'
        f'<div class="snapshot" data-snapshot-id="{escape(snapshot.snapshot_id)}" '
        f'data-trace-id="{escape(snapshot.trace_id)}">'
        f"Snapshot at position {snapshot.current_position}"
        "</div>\n"
        "</section>"
    )
