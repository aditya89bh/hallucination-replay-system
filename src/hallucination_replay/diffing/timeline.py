"""Timeline comparison for replay executions."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.replay import ReplayTimeline


class TimelineDiff(TraceModel):
    """Diff between two execution timelines."""

    missing_steps: list[str] = Field(default_factory=list)
    additional_steps: list[str] = Field(default_factory=list)
    order_changed: bool
    run_a_order: list[str] = Field(default_factory=list)
    run_b_order: list[str] = Field(default_factory=list)


def diff_timelines(run_a: RunTrace, run_b: RunTrace) -> TimelineDiff:
    """Compare execution order, missing steps, and additional steps."""
    order_a = [item.step_id for item in ReplayTimeline(run_a).items()]
    order_b = [item.step_id for item in ReplayTimeline(run_b).items()]
    shared_a = [step_id for step_id in order_a if step_id in set(order_b)]
    shared_b = [step_id for step_id in order_b if step_id in set(order_a)]
    return TimelineDiff(
        missing_steps=sorted(set(order_a) - set(order_b)),
        additional_steps=sorted(set(order_b) - set(order_a)),
        order_changed=shared_a != shared_b,
        run_a_order=order_a,
        run_b_order=order_b,
    )
