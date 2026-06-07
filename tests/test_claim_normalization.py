from __future__ import annotations

from hallucination_replay.hallucination import (
    Claim,
    normalize_claim,
    normalize_claims,
    normalize_text,
)


def test_normalize_text_removes_case_punctuation_and_extra_whitespace() -> None:
    assert normalize_text("  Paris,   FRANCE!!! ") == "paris france"


def test_normalize_claim_preserves_metadata() -> None:
    claim = Claim(claim_id="c1", text="Paris, France!", source_step=1, confidence=0.8)

    normalized = normalize_claim(claim)

    assert normalized.claim_id == "c1"
    assert normalized.text == "paris france"
    assert normalized.source_step == 1


def test_normalize_claims() -> None:
    claims = [Claim(claim_id="c1", text="A B.", source_step=1, confidence=0.8)]

    assert [claim.text for claim in normalize_claims(claims)] == ["a b"]
