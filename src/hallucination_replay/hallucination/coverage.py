"""Evidence coverage scoring for claim sets."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.hallucination.matching import EvidenceMatch
from hallucination_replay.models.base import TraceModel


class EvidenceCoverageScore(TraceModel):
    """Coverage metrics for claim support."""

    total_claims: int
    supported_claims: int
    coverage_score: float = Field(ge=0.0, le=1.0)


def score_evidence_coverage(
    matches: list[EvidenceMatch], support_threshold: float = 0.6
) -> EvidenceCoverageScore:
    """Score the share of claims covered by sufficient evidence."""
    if not matches:
        return EvidenceCoverageScore(
            total_claims=0, supported_claims=0, coverage_score=1.0
        )
    supported = sum(1 for match in matches if match.support_score >= support_threshold)
    return EvidenceCoverageScore(
        total_claims=len(matches),
        supported_claims=supported,
        coverage_score=round(supported / len(matches), 4),
    )
