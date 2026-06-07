"""Deterministic hallucination severity ranking."""

from __future__ import annotations

from enum import StrEnum

from hallucination_replay.hallucination.scoring import HallucinationScore

CRITICAL_THRESHOLD = 0.8
HIGH_THRESHOLD = 0.6
MEDIUM_THRESHOLD = 0.3


class HallucinationSeverity(StrEnum):
    """Severity levels for hallucination risk."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def rank_hallucination_severity(score: HallucinationScore) -> HallucinationSeverity:
    """Rank hallucination severity using deterministic thresholds."""
    if score.score >= CRITICAL_THRESHOLD:
        return HallucinationSeverity.CRITICAL
    if score.score >= HIGH_THRESHOLD:
        return HallucinationSeverity.HIGH
    if score.score >= MEDIUM_THRESHOLD:
        return HallucinationSeverity.MEDIUM
    return HallucinationSeverity.LOW
