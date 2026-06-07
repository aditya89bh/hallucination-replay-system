from __future__ import annotations

from hallucination_replay.analysis import FailureFinding, FailureType, rank_root_causes


def finding(
    failure_type: FailureType,
    message: str,
    *,
    severity: int,
    confidence: float,
    evidence_count: int,
) -> FailureFinding:
    return FailureFinding(
        failure_type=failure_type,
        message=message,
        severity=severity,
        confidence=confidence,
        evidence=[f"evidence-{index}" for index in range(evidence_count)],
    )


def test_rank_root_causes_orders_by_severity_first() -> None:
    ranked = rank_root_causes(
        [
            finding(
                FailureType.TOOL_FAILURE,
                "tool",
                severity=3,
                confidence=1.0,
                evidence_count=5,
            ),
            finding(
                FailureType.OUTPUT_FAILURE,
                "output",
                severity=5,
                confidence=0.4,
                evidence_count=1,
            ),
        ]
    )

    assert [item.finding.message for item in ranked] == ["output", "tool"]
    assert [item.rank for item in ranked] == [1, 2]


def test_rank_root_causes_uses_confidence_and_evidence_as_tiebreakers() -> None:
    ranked = rank_root_causes(
        [
            finding(
                FailureType.MEMORY_FAILURE,
                "low",
                severity=4,
                confidence=0.5,
                evidence_count=1,
            ),
            finding(
                FailureType.RETRIEVAL_FAILURE,
                "high",
                severity=4,
                confidence=0.7,
                evidence_count=2,
            ),
        ]
    )

    assert ranked[0].finding.message == "high"
    assert ranked[0].confidence_score > ranked[1].confidence_score
