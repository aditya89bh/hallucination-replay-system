from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from hallucination_replay.analysis import (
    analyze_memory_failures,
    analyze_output_failures,
    analyze_tool_failures,
    generate_failure_json_report,
    generate_failure_markdown_report,
    rank_root_causes,
)
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.reconstruction import reconstruct_state
from hallucination_replay.replay import ReplayController, steps_to_metadata

STEP_ONE = 1


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="tool" if index == STEP_ONE else "model",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def make_trace() -> RunTrace:
    metadata = steps_to_metadata([make_step("step-0", 0), make_step("step-1", 1)])
    metadata["memory_expected_reads"] = ["profile"]
    metadata["tools"] = [
        {
            "step_index": 1,
            "call": {
                "tool_name": "search",
                "arguments": {"query": "profile"},
                "invocation_time": "2026-01-01T00:01:00Z",
                "step_id": "step-1",
            },
            "result": {
                "tool_name": "search",
                "success": False,
                "output": {"error": "timeout"},
                "execution_time_ms": 10.0,
                "step_id": "step-1",
            },
        }
    ]
    metadata["outputs"] = [{"step_index": 1, "content": "draft"}]
    return RunTrace(
        run_id="analysis-integration-run",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=metadata,
    )


def test_failure_analysis_end_to_end(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(make_trace().to_json(), encoding="utf-8")
    trace = RunTrace.from_json(trace_path.read_text(encoding="utf-8"))

    controller = ReplayController.create(trace, "analysis-session")
    controller.move_forward()
    assert controller.session.current_position == STEP_ONE

    state = reconstruct_state(trace, STEP_ONE)
    findings = [
        *analyze_memory_failures(trace, state.step_index),
        *analyze_tool_failures(trace, state.step_index),
        *analyze_output_failures(trace, state.step_index),
    ]
    ranked = rank_root_causes(findings)
    markdown_report = generate_failure_markdown_report(findings)
    json_report = json.loads(generate_failure_json_report(findings))

    assert state.trace_id == "analysis-integration-run"
    assert [finding.message for finding in findings] == [
        "Missing memory reads",
        "Failed tool executions",
        "Missing final response artifacts",
    ]
    assert ranked[0].finding.message == "Missing final response artifacts"
    assert "# Failure Analysis Report" in markdown_report
    assert json_report["ranking"][0]["finding"]["message"] == ranked[0].finding.message
