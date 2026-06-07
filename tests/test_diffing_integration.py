from __future__ import annotations

import json
from pathlib import Path

from hallucination_replay.diffing import (
    compare_executions,
    diff_timelines,
    generate_comparison_json_report,
    generate_comparison_markdown_report,
)
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_state
from hallucination_replay.replay import ReplayTraceLoader


def test_diffing_integration_loads_reconstructs_compares_and_reports() -> None:
    payload = json.loads(Path("examples/diffing/retrieval_regression.json").read_text())
    run_a = RunTrace.model_validate(payload["run_a"])
    run_b = RunTrace.model_validate(payload["run_b"])

    steps_a = ReplayTraceLoader().get_steps(run_a)
    steps_b = ReplayTraceLoader().get_steps(run_b)
    state_a = reconstruct_state(run_a, steps_a[-1].step_index)
    state_b = reconstruct_state(run_b, steps_b[-1].step_index)
    timeline_diff = diff_timelines(run_a, run_b)
    comparison = compare_executions(run_a, run_b)
    markdown_report = generate_comparison_markdown_report(comparison)
    json_report = generate_comparison_json_report(comparison)
    json_payload = json.loads(json_report)

    assert state_a.trace_id == "retrieval-good"
    assert state_b.trace_id == "retrieval-regression"
    assert timeline_diff.run_a_order == ["s1"]
    assert comparison.retrieval_diff.documents_removed == ["policy-doc"]
    assert "## Detailed Diff" in markdown_report
    assert json_payload["comparison"]["retrieval_diff"]["documents_removed"] == [
        "policy-doc"
    ]
