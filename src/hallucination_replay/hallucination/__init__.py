"""Hallucination detection package."""

from hallucination_replay.hallucination.claims import (
    Claim,
    extract_claims_from_outputs,
    extract_claims_from_text,
)

__all__ = [
    "Claim",
    "extract_claims_from_outputs",
    "extract_claims_from_text",
]
