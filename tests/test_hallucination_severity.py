from __future__ import annotations

from hallucination_replay.hallucination import (
    HallucinationScore,
    HallucinationSeverity,
    rank_hallucination_severity,
)


def score(value: float) -> HallucinationScore:
    return HallucinationScore(
        unsupported_count=0, contradiction_count=0, evidence_coverage=1.0, score=value
    )


def test_rank_hallucination_severity_thresholds() -> None:
    assert rank_hallucination_severity(score(0.1)) is HallucinationSeverity.LOW
    assert rank_hallucination_severity(score(0.3)) is HallucinationSeverity.MEDIUM
    assert rank_hallucination_severity(score(0.6)) is HallucinationSeverity.HIGH
    assert rank_hallucination_severity(score(0.8)) is HallucinationSeverity.CRITICAL
