from __future__ import annotations

from hallucination_replay.analysis import (
    FailureFinding,
    FailureType,
    generate_detailed_failure_summary,
    generate_short_failure_summary,
)


def finding(message: str, failure_type: FailureType, severity: int) -> FailureFinding:
    return FailureFinding(
        failure_type=failure_type,
        message=message,
        severity=severity,
        confidence=0.8,
        evidence=[message],
    )


def test_generate_short_failure_summary() -> None:
    summary = generate_short_failure_summary(
        [finding("Missing final response", FailureType.OUTPUT_FAILURE, 5)]
    )

    assert summary == "Primary failure: Missing final response (output_failure)."


def test_generate_detailed_failure_summary() -> None:
    summary = generate_detailed_failure_summary(
        [
            finding("Missing final response", FailureType.OUTPUT_FAILURE, 5),
            finding("Tool failed", FailureType.TOOL_FAILURE, 4),
            finding("No retrieval", FailureType.RETRIEVAL_FAILURE, 2),
        ]
    )

    assert "Secondary failures:" in summary
    assert "- Tool failed (tool_failure)" in summary
    assert "- No retrieval (retrieval_failure)" in summary


def test_summaries_handle_no_findings() -> None:
    assert generate_short_failure_summary([]) == "No failure findings were identified."
    assert (
        generate_detailed_failure_summary([]) == "No failure findings were identified."
    )
