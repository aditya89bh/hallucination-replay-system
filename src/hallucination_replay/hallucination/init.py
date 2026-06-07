"""Hallucination detection package."""

from hallucination_replay.hallucination.claims import (
    Claim,
    extract_claims_from_outputs,
    extract_claims_from_text,
)
from hallucination_replay.hallucination.evidence import Evidence, extract_evidence
from hallucination_replay.hallucination.matching import (
    EvidenceMatch,
    match_claim_to_evidence,
    match_claims_to_evidence,
)
from hallucination_replay.hallucination.normalization import (
    normalize_claim,
    normalize_claims,
    normalize_evidence,
    normalize_evidence_records,
    normalize_text,
)
from hallucination_replay.hallucination.unsupported import (
    UnsupportedClaimFinding,
    detect_unsupported_claims,
)

__all__ = [
    "Claim",
    "Evidence",
    "EvidenceMatch",
    "UnsupportedClaimFinding",
    "detect_unsupported_claims",
    "extract_claims_from_outputs",
    "extract_claims_from_text",
    "extract_evidence",
    "match_claim_to_evidence",
    "match_claims_to_evidence",
    "normalize_claim",
    "normalize_claims",
    "normalize_evidence",
    "normalize_evidence_records",
    "normalize_text",
]
