from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi import status
from fastapi.testclient import TestClient

from hallucination_replay.api import create_app
from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository

BENCHMARK_PATH = Path("benchmarks/hallucination/contradiction.json")


def test_platform_api_end_to_end_debugging_workflow(tmp_path: Path) -> None:
    client = TestClient(create_app(repository=FilesystemTraceRepository(tmp_path)))
    trace = _platform_trace()
    comparison_trace = trace.model_copy(
        update={"run_id": "hallucination-contradiction-comparison", "status": "failed"}
    )

    upload_a = client.post("/traces", json=trace.to_dict())
    upload_b = client.post("/traces", json=comparison_trace.to_dict())
    replay = client.post(
        "/replay/load",
        json={"run_id": trace.run_id, "session_id": "platform-replay"},
    )
    next_replay = client.post("/replay/next", json={"session_id": "platform-replay"})
    state = client.post(
        "/reconstruction/state", json={"run_id": trace.run_id, "step_index": 1}
    )
    analysis = client.post(
        "/analysis/run",
        json={
            "run_id": trace.run_id,
            "step_index": 3,
            "report_id": "platform-analysis",
        },
    )
    hallucination = client.post(
        "/hallucination/run",
        json={
            "run_id": trace.run_id,
            "step_index": 3,
            "report_id": "platform-hallucination",
        },
    )
    comparison = client.post(
        "/compare",
        json={
            "run_a_id": trace.run_id,
            "run_b_id": comparison_trace.run_id,
            "report_id": "platform-comparison",
        },
    )

    assert upload_a.status_code == status.HTTP_201_CREATED
    assert upload_b.status_code == status.HTTP_201_CREATED
    assert replay.status_code == status.HTTP_200_OK
    assert next_replay.status_code == status.HTTP_200_OK
    assert state.status_code == status.HTTP_200_OK
    assert analysis.status_code == status.HTTP_200_OK
    assert hallucination.status_code == status.HTTP_200_OK
    assert comparison.status_code == status.HTTP_200_OK

    state_payload = state.json()
    hallucination_payload = hallucination.json()
    comparison_payload = comparison.json()
    analysis_payload = analysis.json()

    assert state_payload["trace_id"] == trace.run_id
    assert analysis_payload["report_id"] == "platform-analysis"
    assert hallucination_payload["severity"] == "medium"
    assert len(cast(list[object], hallucination_payload["contradictions"])) == 1
    assert comparison_payload["json_report"]["status_changed"] is True


def _platform_trace() -> RunTrace:
    trace = RunTrace.from_json(BENCHMARK_PATH.read_text(encoding="utf-8"))
    metadata = dict(trace.metadata)
    metadata["steps"] = [
        {
            "step_id": "retrieve-account",
            "step_index": 1,
            "step_type": "retrieval",
            "timestamp": "2026-01-01T00:01:01Z",
            "description": "Retrieve account evidence.",
        },
        {
            "step_id": "call-account-tool",
            "step_index": 2,
            "step_type": "tool",
            "timestamp": "2026-01-01T00:01:02Z",
            "description": "Fetch account status from a tool.",
        },
        {
            "step_id": "answer-account-status",
            "step_index": 3,
            "step_type": "model",
            "timestamp": "2026-01-01T00:01:03Z",
            "description": "Generate account status answer.",
        },
    ]
    metadata["context"] = [
        {"step_index": 3, "key": "question", "value": "Is the account active?"}
    ]
    metadata["tools"] = [
        {
            "step_index": 2,
            "call": {
                "tool_name": "account_status",
                "arguments": {"account_id": "acct-1"},
                "invocation_time": "2026-01-01T00:01:02Z",
                "step_id": "call-account-tool",
            },
            "result": {
                "tool_name": "account_status",
                "success": True,
                "output": "The account is active.",
                "execution_time_ms": 12.0,
                "step_id": "call-account-tool",
            },
        }
    ]
    metadata["memory"] = []
    return trace.model_copy(update={"metadata": metadata})
