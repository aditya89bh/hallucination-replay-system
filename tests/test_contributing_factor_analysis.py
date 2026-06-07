from __future__ import annotations

from hallucination_replay.analysis import (
    FailureFinding,
    FailureType,
    analyze_contributing_factors,
)


def finding(message: str, severity: int) -> FailureFinding:
    return FailureFinding(
        failure_type=FailureType.UNKNOWN_FAILURE,
        message=message,
        severity=severity,
        confidence=0.8,
        evidence=[message],
    )


def test_analyze_contributing_factors_identifies_primary_and_secondary() -> None:
    analysis = analyze_contributing_factors(
        [finding("minor", 2), finding("primary", 5), finding("secondary", 4)]
    )

    assert analysis.primary_failure is not None
    assert analysis.primary_failure.finding.message == "primary"
    assert [item.finding.message for item in analysis.secondary_failures] == [
        "secondary"
    ]
    assert [item.message for item in analysis.contributing_factors] == ["minor"]


def test_analyze_contributing_factors_handles_empty_findings() -> None:
    analysis = analyze_contributing_factors([])

    assert analysis.primary_failure is None
    assert analysis.secondary_failures == []
    assert analysis.contributing_factors == []
