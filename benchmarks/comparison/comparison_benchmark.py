"""Deterministic Phase 8 comparison benchmarks."""

from __future__ import annotations

import json
from pathlib import Path

from hallucination_replay.diffing import (
    compare_executions,
    generate_comparison_json_report,
    generate_comparison_markdown_report,
)
from hallucination_replay.diffing.examples import (
    memory_regression_runs,
    retrieval_regression_runs,
    successful_vs_failed_runs,
)


def run_comparison_benchmark() -> dict[str, object]:
    """Measure deterministic diff and report generation work units."""
    cases = {
        "memory_regression": memory_regression_runs(),
        "retrieval_regression": retrieval_regression_runs(),
        "successful_vs_failed": successful_vs_failed_runs(),
    }
    results: dict[str, object] = {}
    for name in sorted(cases):
        run_a, run_b = cases[name]
        comparison = compare_executions(run_a, run_b)
        markdown = generate_comparison_markdown_report(comparison)
        json_report = generate_comparison_json_report(comparison)
        results[name] = {
            "diff_sections": len(comparison.to_dict()),
            "json_report_bytes": len(json_report.encode()),
            "markdown_report_lines": len(markdown.splitlines()),
            "total_change_count": _total_change_count(json_report),
        }
    return results


def write_benchmark_summary(path: Path) -> None:
    """Write benchmark results with deterministic key ordering."""
    path.write_text(
        json.dumps(run_comparison_benchmark(), sort_keys=True, indent=2) + "\n"
    )


def _total_change_count(json_report: str) -> int:
    payload = json.loads(json_report)
    counts = payload["change_counts"]
    if not isinstance(counts, dict):
        return 0
    return sum(value for value in counts.values() if isinstance(value, int))


if __name__ == "__main__":
    write_benchmark_summary(Path("benchmarks/comparison/summary.json"))
