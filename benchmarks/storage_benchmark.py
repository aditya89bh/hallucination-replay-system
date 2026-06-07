"""Lightweight deterministic benchmark for trace storage operations."""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository, TraceSearch

TRACE_COUNT = 25


def make_trace(index: int) -> RunTrace:
    """Create a deterministic benchmark trace."""
    started_at = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index)
    return RunTrace(
        run_id=f"run-{index:03d}",
        started_at=started_at,
        completed_at=started_at + timedelta(seconds=1),
        status="completed" if index % 2 == 0 else "failed",
        metadata={
            "agent_name": "benchmark-agent",
            "tags": ["benchmark", f"bucket-{index % 3}"],
        },
    )


def run_storage_benchmark(
    base_path: Path, trace_count: int = TRACE_COUNT
) -> dict[str, Any]:
    """Run deterministic storage benchmarks and return timing results."""
    repository = FilesystemTraceRepository(base_path)
    traces = [make_trace(index) for index in range(trace_count)]

    save_start = perf_counter()
    for trace in traces:
        repository.save_trace(trace)
    save_seconds = perf_counter() - save_start

    load_start = perf_counter()
    for trace in traces:
        repository.load_trace(trace.run_id)
    load_seconds = perf_counter() - load_start

    list_start = perf_counter()
    listed_traces = repository.list_traces()
    list_seconds = perf_counter() - list_start

    search_start = perf_counter()
    search_results = TraceSearch(repository.index).by_tag("benchmark")
    search_seconds = perf_counter() - search_start

    return {
        "trace_count": trace_count,
        "save_seconds": save_seconds,
        "load_seconds": load_seconds,
        "list_seconds": list_seconds,
        "search_seconds": search_seconds,
        "listed_count": len(listed_traces),
        "search_result_count": len(search_results),
    }


def main() -> None:
    """Run the benchmark in a temporary directory and emit JSON."""
    with tempfile.TemporaryDirectory() as temporary_directory:
        results = run_storage_benchmark(Path(temporary_directory))
    json.dump(results, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
