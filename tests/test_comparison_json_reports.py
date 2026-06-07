from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Literal

from hallucination_replay.diffing import (
    compare_executions,
    generate_comparison_json_report,
)
from hallucination_replay.models import RunTrace


def test_generate_comparison_json_report_exports_structured_deterministic_payload() -> (
    None
):
    report = generate_comparison_json_report(
        compare_executions(_trace("a", "completed"), _trace("b", "failed"))
    )
    payload = json.loads(report)

    assert payload["report_type"] == "execution_comparison"
    assert payload["run_a_id"] == "a"
    assert payload["run_b_id"] == "b"
    assert payload["status_changed"] is True
    assert sorted(payload["change_counts"]) == sorted(payload["comparison"])
    assert report == generate_comparison_json_report(
        compare_executions(_trace("a", "completed"), _trace("b", "failed"))
    )


def _trace(run_id: str, status: Literal["completed", "failed"]) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=status,
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
