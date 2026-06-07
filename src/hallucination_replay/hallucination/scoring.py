"""Aggregate hallucination scoring."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.hallucination.contradictions import ContradictionFinding
from hallucination_replay.hallucination.coverage import EvidenceCoverageScore
from hallucination_replay.hallucination.unsupported import UnsupportedClaimFinding
from hallucination_replay.models.base import TraceModel


class HallucinationScore(TraceModel):
    """Aggregate deterministic hallucination score."""

    unsupported_count: int
    contradiction_count: int
    evidence_coverage: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=1.0)


def score_hallucinations(
    unsupported_claims: list[UnsupportedClaimFinding],
    contradictions: list[ContradictionFinding],
    coverage: EvidenceCoverageScore,
) -> HallucinationScore:
    """Aggregate unsupported claims, contradictions, and coverage into one score."""
    claim_count = max(coverage.total_claims, 1)
    unsupported_component = len(unsupported_claims) / claim_count
    contradiction_component = min(len(contradictions) / claim_count, 1.0)
    coverage_gap = 1.0 - coverage.coverage_score
    score = round(
        min(
            (unsupported_component * 0.4)
            + (contradiction_component * 0.4)
            + (coverage_gap * 0.2),
            1.0,
        ),
        4,
    )
    return HallucinationScore(
        unsupported_count=len(unsupported_claims),
        contradiction_count=len(contradictions),
        evidence_coverage=coverage.coverage_score,
        score=score,
    )
