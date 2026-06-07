"""Deterministic text normalization for claims and evidence."""

from __future__ import annotations

import re
import string

from hallucination_replay.hallucination.claims import Claim

_WHITESPACE_RE = re.compile(r"\s+")
_TRANSLATION = str.maketrans("", "", string.punctuation)


def normalize_text(text: str) -> str:
    """Normalize casing, punctuation, and whitespace."""
    without_punctuation = text.translate(_TRANSLATION)
    compact = _WHITESPACE_RE.sub(" ", without_punctuation.lower())
    return compact.strip()


def normalize_claim(claim: Claim) -> Claim:
    """Return a copy of a claim with normalized text."""
    return claim.model_copy(update={"text": normalize_text(claim.text)})


def normalize_claims(claims: list[Claim]) -> list[Claim]:
    """Normalize multiple claims."""
    return [normalize_claim(claim) for claim in claims]
