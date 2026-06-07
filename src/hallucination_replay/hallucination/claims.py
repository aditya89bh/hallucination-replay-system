"""Deterministic claim extraction helpers."""

from __future__ import annotations

import re

from pydantic import Field

from hallucination_replay.models.base import TraceModel

MIN_CLAIM_WORDS = 3
DEFAULT_CLAIM_CONFIDENCE = 0.85
LIKELY_CLAIM_CONFIDENCE = 0.7
CERTAIN_CLAIM_CONFIDENCE = 0.95


class Claim(TraceModel):
    """A factual-looking statement emitted by an agent."""

    claim_id: str
    text: str
    source_step: int
    confidence: float = Field(ge=0.0, le=1.0)


def extract_claims_from_text(text: str, source_step: int) -> list[Claim]:
    """Extract deterministic sentence-level claims from text."""
    statements = [part.strip() for part in re.split(r"[.!?]+", text) if part.strip()]
    return [
        Claim(
            claim_id=f"claim-{source_step}-{index}",
            text=statement,
            source_step=source_step,
            confidence=_claim_confidence(statement),
        )
        for index, statement in enumerate(statements)
        if _is_claim(statement)
    ]


def extract_claims_from_outputs(outputs: list[dict[str, object]]) -> list[Claim]:
    """Extract claims from serialized output records."""
    claims: list[Claim] = []
    for output in outputs:
        content = output.get("content")
        step_index = output.get("step_index", output.get("source_step", 0))
        if isinstance(content, str) and isinstance(step_index, int):
            claims.extend(extract_claims_from_text(content, step_index))
    return claims


def _is_claim(statement: str) -> bool:
    words = statement.split()
    if len(words) < MIN_CLAIM_WORDS:
        return False
    lowered = statement.lower()
    non_claim_prefixes = ("maybe ", "perhaps ", "i think ", "could ", "would ")
    return not lowered.startswith(non_claim_prefixes)


def _claim_confidence(statement: str) -> float:
    lowered = statement.lower()
    if any(
        token in lowered for token in ("definitely", "always", "never", "certainly")
    ):
        return CERTAIN_CLAIM_CONFIDENCE
    if any(token in lowered for token in ("likely", "probably", "appears")):
        return LIKELY_CLAIM_CONFIDENCE
    return DEFAULT_CLAIM_CONFIDENCE
