"""Deterministic comparison examples for diffing documentation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from hallucination_replay.models import RunTrace


def successful_vs_failed_runs() -> tuple[RunTrace, RunTrace]:
    """Return a successful run and a failed run with changed tool outcome."""
    return (
        _base_trace("successful-run", "completed", "Search succeeded", success=True),
        _base_trace("failed-run", "failed", "Search timed out", success=False),
    )


def retrieval_regression_runs() -> tuple[RunTrace, RunTrace]:
    """Return traces where retrieved evidence disappears in run B."""
    run_a = _base_trace("retrieval-good", "completed", "Evidence found", success=True)
    run_b = _base_trace(
        "retrieval-regression", "failed", "Evidence missing", success=True
    )
    run_a.metadata["retrievals"] = [
        {
            "step_index": 1,
            "event": {
                "query": "refund policy",
                "retrieved_documents": [
                    {"id": "policy-doc", "text": "Refunds close in 30 days."}
                ],
                "retrieval_time_ms": 5,
                "source": "knowledge-base",
            },
        }
    ]
    run_b.metadata["retrievals"] = [
        {
            "step_index": 1,
            "event": {
                "query": "refund policy",
                "retrieved_documents": [],
                "retrieval_time_ms": 5,
                "source": "knowledge-base",
            },
        }
    ]
    return run_a, run_b


def memory_regression_runs() -> tuple[RunTrace, RunTrace]:
    """Return traces where a required memory value changes in run B."""
    run_a = _base_trace("memory-good", "completed", "Used account memory", success=True)
    run_b = _base_trace(
        "memory-regression", "failed", "Used stale account memory", success=True
    )
    run_a.metadata["memory"] = [
        _memory_record("account_tier", "enterprise"),
    ]
    run_b.metadata["memory"] = [
        _memory_record("account_tier", "free"),
    ]
    return run_a, run_b


def _base_trace(
    run_id: str,
    status: Literal["completed", "failed"],
    description: str,
    *,
    success: bool,
) -> RunTrace:
    return RunTrace(
        run_id=run_id,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=status,
        metadata={
            "steps": [
                {
                    "step_id": "s1",
                    "step_index": 1,
                    "step_type": "tool",
                    "timestamp": "2026-01-01T00:00:01Z",
                    "description": description,
                }
            ],
            "tools": [
                {
                    "step_index": 1,
                    "call": {
                        "tool_name": "search",
                        "arguments": {"query": "policy"},
                        "invocation_time": "2026-01-01T00:00:01Z",
                        "step_id": "tool-1",
                    },
                    "result": {
                        "tool_name": "search",
                        "success": success,
                        "output": "ok" if success else "timeout",
                        "execution_time_ms": 5,
                        "step_id": "tool-1",
                    },
                }
            ],
        },
    )


def _memory_record(key: str, value: str) -> dict[str, object]:
    return {
        "step_index": 1,
        "event": {
            "event_type": "write",
            "key": key,
            "value": value,
            "timestamp": "2026-01-01T00:00:01Z",
        },
    }
