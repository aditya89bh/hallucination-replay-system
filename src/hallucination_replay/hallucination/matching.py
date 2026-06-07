"""Deterministic claim-to-evidence matching."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.hallucination.claims import Claim
from hallucination_replay.hallucination.evidence import Evidence
from hallucination_replay.hallucination.normalization import normalize_text
from hallucination_replay.models.base import TraceModel

STOPWORDS = {"a", "an", "and", "are", "in", "is", "of", "the", "to"}


class EvidenceMatch(TraceModel):
    """Support evidence and score for one claim."""

    claim: Claim
    matched_evidence: list[Evidence] = Field(default_factory=list)
    support_score: float = Field(ge=0.0, le=1.0)


def match_claim_to_evidence(claim: Claim, evidence: list[Evidence]) -> EvidenceMatch:
    """Match one claim to supporting evidence by normalized token overlap."""
    scored = [(item, _support_score(claim.text, item.text)) for item in evidence]
    matches = [item for item, score in scored if score > 0.0]
    score = max((score for _, score in scored), default=0.0)
    return EvidenceMatch(claim=claim, matched_evidence=matches, support_score=score)


def match_claims_to_evidence(
    claims: list[Claim], evidence: list[Evidence]
) -> list[EvidenceMatch]:
    """Match many claims to evidence."""
    return [match_claim_to_evidence(claim, evidence) for claim in claims]


def _support_score(claim_text: str, evidence_text: str) -> float:
    claim_tokens = _content_tokens(claim_text)
    evidence_tokens = _content_tokens(evidence_text)
    if not claim_tokens or not evidence_tokens:
        return 0.0
    overlap = claim_tokens & evidence_tokens
    return round(len(overlap) / len(claim_tokens), 4)


def _content_tokens(text: str) -> set[str]:
    return {token for token in normalize_text(text).split() if token not in STOPWORDS}
