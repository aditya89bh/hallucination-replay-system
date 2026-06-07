"""Lightweight deterministic benchmark for replay operations."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from time import perf_counter
from typing import Any

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import (
    ReplayController,
    ReplayTimeline,
    steps_to_metadata,
)

STEP_COUNT = 50


def make_step(index: int) -> AgentStep:
    """Create a deterministic benchmark step."""
    return AgentStep(
        step_id=f"step-{index:03d}",
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=index),
        description=f"Benchmark step {index}",
    )


def make_trace(step_count: int = STEP_COUNT) -> RunTrace:
    """Create a deterministic benchmark trace."""
    started_at = datetime(2026, 1, 1, tzinfo=UTC)
    steps = [make_step(index) for index in range(step_count)]
    return RunTrace(
        run_id="replay-benchmark-run",
        started_at=started_at,
        completed_at=started_at + timedelta(seconds=step_count),
        status="completed",
        metadata=steps_to_metadata(steps),
    )


def run_replay_benchmark(step_count: int = STEP_COUNT) -> dict[str, Any]:
    """Run deterministic replay benchmarks and return timing results."""
    trace = make_trace(step_count)

    load_start = perf_counter()
    controller = ReplayController.create(trace, "benchmark-session")
    load_seconds = perf_counter() - load_start

    navigation_start = perf_counter()
    while controller.has_next():
        controller.move_forward()
    while controller.has_previous():
        controller.move_backward()
    navigation_seconds = perf_counter() - navigation_start

    snapshot_start = perf_counter()
    snapshot = controller.create_snapshot("benchmark-snapshot")
    snapshot_seconds = perf_counter() - snapshot_start

    timeline_start = perf_counter()
    timeline = ReplayTimeline(trace).export()
    timeline_seconds = perf_counter() - timeline_start

    return {
        "step_count": step_count,
        "load_seconds": load_seconds,
        "navigation_seconds": navigation_seconds,
        "snapshot_seconds": snapshot_seconds,
        "timeline_seconds": timeline_seconds,
        "snapshot_position": snapshot.current_position,
        "timeline_step_count": timeline.summary.step_count,
    }


def main() -> None:
    """Run the benchmark and emit JSON."""
    json.dump(run_replay_benchmark(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
