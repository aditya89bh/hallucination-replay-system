"""Deterministic confidence scoring for analysis findings."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.analysis.taxonomy import FailureFinding
from hallucination_replay.models.base import TraceModel

MAX_SEVERITY = 5
EVIDENCE_WEIGHT = 0.05
MAX_EVIDENCE_BONUS = 0.2
SEVERITY_WEIGHT = 0.04


class ConfidenceScore(TraceModel):
    """Confidence score with explainable components."""

    finding_message: str
    score: float = Field(ge=0.0, le=1.0)
    evidence_count: int = Field(ge=0)
    severity: int = Field(ge=1, le=MAX_SEVERITY)
    components: dict[str, float] = Field(default_factory=dict)


def score_finding_confidence(finding: FailureFinding) -> ConfidenceScore:
    """Score a finding deterministically from base confidence and evidence."""
    evidence_bonus = min(len(finding.evidence) * EVIDENCE_WEIGHT, MAX_EVIDENCE_BONUS)
    severity_bonus = (finding.severity / MAX_SEVERITY) * SEVERITY_WEIGHT
    score = min(1.0, finding.confidence + evidence_bonus + severity_bonus)
    return ConfidenceScore(
        finding_message=finding.message,
        score=round(score, 4),
        evidence_count=len(finding.evidence),
        severity=finding.severity,
        components={
            "base_confidence": finding.confidence,
            "evidence_bonus": round(evidence_bonus, 4),
            "severity_bonus": round(severity_bonus, 4),
        },
    )


def score_findings(findings: list[FailureFinding]) -> list[ConfidenceScore]:
    """Score findings in input order."""
    return [score_finding_confidence(finding) for finding in findings]
