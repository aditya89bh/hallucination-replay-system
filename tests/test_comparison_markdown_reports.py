from __future__ import annotations

from datetime import UTC, datetime

from hallucination_replay.diffing import (
    compare_executions,
    generate_comparison_markdown_report,
)
from hallucination_replay.models import RunTrace


def test_generate_comparison_markdown_report_has_summary_counts_and_details() -> None:
    report = generate_comparison_markdown_report(
        compare_executions(_trace("a", "completed"), _trace("b", "failed"))
    )

    assert "# Execution Comparison Report" in report
    assert "## Summary" in report
    assert "- Run A: a (completed)" in report
    assert "## Change Counts" in report
    assert "## Detailed Diff" in report
    assert "### trace_diff" in report


def _trace(run_id: str, status: str) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=status,  # type: ignore[arg-type]
        metadata={
            "steps": [
                {
                    "step_id": "s1",
                    "step_index": 1,
                    "step_type": "model",
                    "timestamp": "2026-01-01T00:00:01Z",
                    "description": "answer",
                }
            ]
        },
    )
