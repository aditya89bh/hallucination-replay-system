from __future__ import annotations

from hallucination_replay.hallucination import (
    Claim,
    Evidence,
    match_claim_to_evidence,
    match_claims_to_evidence,
)


def test_match_claim_to_evidence_scores_token_overlap() -> None:
    claim = Claim(
        claim_id="c1", text="Paris is in France", source_step=1, confidence=0.8
    )
    evidence = [
        Evidence(
            evidence_id="e1",
            text="France contains Paris",
            source="retrieval",
            source_step=1,
        )
    ]

    match = match_claim_to_evidence(claim, evidence)

    assert match.support_score == 1.0
    assert match.matched_evidence == evidence


def test_match_claims_to_evidence_handles_no_support() -> None:
    claim = Claim(
        claim_id="c1", text="Paris is in France", source_step=1, confidence=0.8
    )
    evidence = [
        Evidence(
            evidence_id="e1",
            text="Tokyo is in Japan",
            source="retrieval",
            source_step=1,
        )
    ]

    matches = match_claims_to_evidence([claim], evidence)

    assert matches[0].support_score == 0.0
