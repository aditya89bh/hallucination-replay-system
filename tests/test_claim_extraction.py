from __future__ import annotations

from hallucination_replay.hallucination import (
    Claim,
    extract_claims_from_outputs,
    extract_claims_from_text,
)

DEFAULT_CONFIDENCE = 0.85
OUTPUT_STEP = 4


def test_claim_model_serializes() -> None:
    claim = Claim(
        claim_id="c1", text="Paris is in France", source_step=2, confidence=0.9
    )

    assert claim.to_dict() == {
        "claim_id": "c1",
        "text": "Paris is in France",
        "source_step": 2,
        "confidence": 0.9,
    }


def test_extract_claims_from_text_is_sentence_based_and_deterministic() -> None:
    claims = extract_claims_from_text(
        "Paris is in France. Maybe it rains. The sky is blue!", 3
    )

    assert [claim.claim_id for claim in claims] == ["claim-3-0", "claim-3-2"]
    assert [claim.text for claim in claims] == ["Paris is in France", "The sky is blue"]
    assert claims[0].confidence == DEFAULT_CONFIDENCE


def test_extract_claims_from_outputs() -> None:
    claims = extract_claims_from_outputs(
        [
            {"step_index": OUTPUT_STEP, "content": "Tool returned success."},
            {"step_index": 5, "content": 42},
        ]
    )

    assert len(claims) == 1
    assert claims[0].source_step == OUTPUT_STEP
