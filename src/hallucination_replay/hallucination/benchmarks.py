"""Benchmark trace loading for hallucination detection."""

from __future__ import annotations

from pathlib import Path

from hallucination_replay.models import RunTrace

DEFAULT_BENCHMARK_DIRECTORY = Path("benchmarks/hallucination")


def load_hallucination_benchmark_traces(
    directory: Path = DEFAULT_BENCHMARK_DIRECTORY,
) -> list[RunTrace]:
    """Load hallucination benchmark traces from JSON files in sorted order."""
    return [
        RunTrace.from_json(path.read_text())
        for path in sorted(directory.glob("*.json"))
    ]
