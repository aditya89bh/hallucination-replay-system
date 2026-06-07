from __future__ import annotations

import json

from hallucination_replay.analysis import (
    FailureFinding,
    FailureType,
    generate_failure_json_report,
    generate_failure_markdown_report,
)


def make_findings() -> list[FailureFinding]:
    return [
        FailureFinding(
            failure_type=FailureType.OUTPUT_FAILURE,
            message="Missing final response",
            severity=5,
            confidence=0.9,
            evidence=["No final artifact"],
        )
    ]


def test_generate_failure_markdown_report() -> None:
    report = generate_failure_markdown_report(make_findings())

    assert report.startswith("# Failure Analysis Report")
    assert "## Ranked Root Causes" in report
    assert "Missing final response" in report


def test_generate_failure_json_report() -> None:
    report = json.loads(generate_failure_json_report(make_findings()))

    assert report["findings"][0]["failure_type"] == "output_failure"
    assert report["ranking"][0]["rank"] == 1
    assert report["confidence"][0]["finding_message"] == "Missing final response"
    assert report["contributing_factors"]["primary_failure"] is not None
