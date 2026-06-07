"""Root-cause ranking for failure findings."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.analysis.confidence import score_finding_confidence
from hallucination_replay.analysis.taxonomy import FailureFinding
from hallucination_replay.models.base import TraceModel


class RankedRootCause(TraceModel):
    """A ranked candidate root cause."""

    rank: int = Field(ge=1)
    finding: FailureFinding
    ranking_score: float = Field(ge=0.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    evidence_count: int = Field(ge=0)


def rank_root_causes(findings: list[FailureFinding]) -> list[RankedRootCause]:
    """Rank findings by severity, confidence, and evidence count."""
    ranked_inputs = sorted(
        findings,
        key=lambda finding: (
            -finding.severity,
            -score_finding_confidence(finding).score,
            -len(finding.evidence),
            finding.failure_type.value,
            finding.message,
        ),
    )
    ranked: list[RankedRootCause] = []
    for index, finding in enumerate(ranked_inputs, start=1):
        confidence = score_finding_confidence(finding).score
        ranking_score = finding.severity + confidence + (len(finding.evidence) / 100)
        ranked.append(
            RankedRootCause(
                rank=index,
                finding=finding,
                ranking_score=round(ranking_score, 4),
                confidence_score=confidence,
                evidence_count=len(finding.evidence),
            )
        )
    return ranked
