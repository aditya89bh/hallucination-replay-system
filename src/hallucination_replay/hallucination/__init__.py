"""Hallucination detection package."""

from hallucination_replay.hallucination.claims import (
    Claim,
    extract_claims_from_outputs,
    extract_claims_from_text,
)
from hallucination_replay.hallucination.evidence import Evidence, extract_evidence
from hallucination_replay.hallucination.normalization import (
    normalize_claim,
    normalize_claims,
    normalize_evidence,
    normalize_evidence_records,
    normalize_text,
)

__all__ = [
    "Claim",
    "Evidence",
    "extract_claims_from_outputs",
    "extract_claims_from_text",
    "extract_evidence",
    "normalize_claim",
    "normalize_claims",
    "normalize_evidence",
    "normalize_evidence_records",
    "normalize_text",
]
