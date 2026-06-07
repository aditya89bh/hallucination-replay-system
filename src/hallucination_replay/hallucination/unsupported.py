"""Unsupported claim detection."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hallucination_replay.hallucination.matching import EvidenceMatch
from hallucination_replay.models.base import TraceModel

SUPPORT_THRESHOLD = 0.6
WEAK_SUPPORT_THRESHOLD = 0.3


class UnsupportedClaimFinding(TraceModel):
    """A claim with missing or weak evidence support."""

    claim_id: str
    claim_text: str
    finding_type: Literal["unsupported_claim", "weakly_supported_claim"]
    support_score: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


def detect_unsupported_claims(
    matches: list[EvidenceMatch],
) -> list[UnsupportedClaimFinding]:
    """Detect claims without enough supporting evidence."""
    findings: list[UnsupportedClaimFinding] = []
    for match in matches:
        if match.support_score < WEAK_SUPPORT_THRESHOLD:
            finding_type: Literal["unsupported_claim", "weakly_supported_claim"] = (
                "unsupported_claim"
            )
        elif match.support_score < SUPPORT_THRESHOLD:
            finding_type = "weakly_supported_claim"
        else:
            continue
        findings.append(
            UnsupportedClaimFinding(
                claim_id=match.claim.claim_id,
                claim_text=match.claim.text,
                finding_type=finding_type,
                support_score=match.support_score,
                evidence_ids=[item.evidence_id for item in match.matched_evidence],
            )
        )
    return findings
