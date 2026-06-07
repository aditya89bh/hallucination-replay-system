"""Trace-level diffing for execution comparisons."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel


class TraceDiff(TraceModel):
    """Deterministic diff between two run traces."""

    run_a_id: str
    run_b_id: str
    status_a: str
    status_b: str
    status_changed: bool
    step_count_a: int = Field(ge=0)
    step_count_b: int = Field(ge=0)
    step_count_delta: int
    metadata_changes: dict[str, dict[str, Any]] = Field(default_factory=dict)


def diff_traces(run_a: RunTrace, run_b: RunTrace) -> TraceDiff:
    """Compare run metadata, step counts, and statuses."""
    step_count_a = _step_count(run_a)
    step_count_b = _step_count(run_b)
    return TraceDiff(
        run_a_id=run_a.run_id,
        run_b_id=run_b.run_id,
        status_a=run_a.status,
        status_b=run_b.status,
        status_changed=run_a.status != run_b.status,
        step_count_a=step_count_a,
        step_count_b=step_count_b,
        step_count_delta=step_count_b - step_count_a,
        metadata_changes=_metadata_changes(run_a.metadata, run_b.metadata),
    )


def _step_count(trace: RunTrace) -> int:
    steps = trace.metadata.get("steps", [])
    return len(steps) if isinstance(steps, list) else 0


def _metadata_changes(
    metadata_a: dict[str, Any], metadata_b: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    changes: dict[str, dict[str, Any]] = {}
    for key in sorted(set(metadata_a) | set(metadata_b)):
        value_a = metadata_a.get(key)
        value_b = metadata_b.get(key)
        if value_a != value_b:
            changes[key] = {"run_a": value_a, "run_b": value_b}
    return changes
