"""Rule-based contradiction detection."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.hallucination.claims import Claim
from hallucination_replay.hallucination.evidence import Evidence
from hallucination_replay.hallucination.matching import match_claim_to_evidence
from hallucination_replay.hallucination.normalization import normalize_text
from hallucination_replay.models.base import TraceModel

NEGATION_TOKENS = {"no", "not", "never", "without", "failed", "false"}
CONTRADICTION_SUPPORT_THRESHOLD = 0.5


class ContradictionFinding(TraceModel):
    """A claim that conflicts with available evidence."""

    claim_id: str
    claim_text: str
    evidence_id: str
    evidence_text: str
    evidence_source: str
    conflict_reason: str
    severity: int = Field(ge=1, le=5)


def detect_contradictions(
    claims: list[Claim], evidence: list[Evidence]
) -> list[ContradictionFinding]:
    """Detect negation conflicts between claims and evidence."""
    findings: list[ContradictionFinding] = []
    for claim in claims:
        claim_negated = _has_negation(claim.text)
        for item in evidence:
            if (
                match_claim_to_evidence(claim, [item]).support_score
                < CONTRADICTION_SUPPORT_THRESHOLD
            ):
                continue
            evidence_negated = _has_negation(item.text)
            if claim_negated != evidence_negated:
                findings.append(
                    ContradictionFinding(
                        claim_id=claim.claim_id,
                        claim_text=claim.text,
                        evidence_id=item.evidence_id,
                        evidence_text=item.text,
                        evidence_source=item.source,
                        conflict_reason="negation_mismatch",
                        severity=_source_severity(item.source),
                    )
                )
    return findings


def _has_negation(text: str) -> bool:
    return bool(set(normalize_text(text).split()) & NEGATION_TOKENS)


def _source_severity(source: str) -> int:
    if source == "tool":
        return 5
    if source == "memory":
        return 4
    return 3
