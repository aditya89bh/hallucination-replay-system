from __future__ import annotations

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.dashboard import render_failure_analysis_viewer


def test_failure_analysis_viewer_displays_findings_root_causes_and_confidence() -> None:
    findings = [
        FailureFinding(
            failure_type=FailureType.TOOL_FAILURE,
            message="Tool timeout",
            severity=4,
            confidence=0.8,
            evidence=["search timed out"],
            step_index=1,
        ),
        FailureFinding(
            failure_type=FailureType.OUTPUT_FAILURE,
            message="Missing final answer",
            severity=5,
            confidence=0.9,
            evidence=["no final output"],
            step_index=1,
        ),
    ]

    html = render_failure_analysis_viewer(findings)

    assert 'class="findings" data-count="2"' in html
    assert "Tool timeout" in html
    assert "Missing final answer" in html
    assert 'class="root-causes"' in html
    assert 'class="confidence"' in html
