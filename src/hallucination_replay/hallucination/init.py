"""Hallucination detection package."""

from hallucination_replay.hallucination.claims import (
    Claim,
    extract_claims_from_outputs,
    extract_claims_from_text,
)
from hallucination_replay.hallucination.evidence import Evidence, extract_evidence

__all__ = [
    "Claim",
    "Evidence",
    "extract_claims_from_outputs",
    "extract_claims_from_text",
    "extract_evidence",
]
