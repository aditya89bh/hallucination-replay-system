from __future__ import annotations

from hallucination_replay.analysis import (
    FailureFinding,
    FailureType,
    score_finding_confidence,
    score_findings,
)

EXPECTED_CONFIDENCE_SCORE = 0.832


def make_finding() -> FailureFinding:
    return FailureFinding(
        failure_type=FailureType.TOOL_FAILURE,
        message="Tool failed",
        severity=4,
        confidence=0.7,
        evidence=["failed once", "missing retry"],
    )


def test_score_finding_confidence_is_deterministic() -> None:
    score = score_finding_confidence(make_finding())

    assert score.score == EXPECTED_CONFIDENCE_SCORE
    assert score.components == {
        "base_confidence": 0.7,
        "evidence_bonus": 0.1,
        "severity_bonus": 0.032,
    }


def test_score_finding_confidence_caps_at_one() -> None:
    finding = FailureFinding(
        failure_type=FailureType.UNKNOWN_FAILURE,
        message="Very certain",
        severity=5,
        confidence=0.95,
        evidence=["a", "b", "c", "d", "e"],
    )

    assert score_finding_confidence(finding).score == 1.0


def test_score_findings_preserves_order() -> None:
    scores = score_findings([make_finding(), make_finding()])

    assert [score.finding_message for score in scores] == ["Tool failed", "Tool failed"]
