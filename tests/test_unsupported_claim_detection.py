from __future__ import annotations

from hallucination_replay.hallucination import (
    Claim,
    EvidenceMatch,
    detect_unsupported_claims,
)


def test_detect_unsupported_claims_finds_missing_evidence() -> None:
    claim = Claim(
        claim_id="c1", text="Paris is in Spain", source_step=1, confidence=0.9
    )
    findings = detect_unsupported_claims(
        [EvidenceMatch(claim=claim, support_score=0.0)]
    )

    assert findings[0].finding_type == "unsupported_claim"
    assert findings[0].claim_id == "c1"


def test_detect_unsupported_claims_finds_weak_support_and_ignores_strong_support() -> (
    None
):
    weak = Claim(
        claim_id="c1", text="Paris is in France", source_step=1, confidence=0.9
    )
    strong = Claim(
        claim_id="c2", text="Tokyo is in Japan", source_step=1, confidence=0.9
    )

    findings = detect_unsupported_claims(
        [
            EvidenceMatch(claim=weak, support_score=0.4),
            EvidenceMatch(claim=strong, support_score=0.8),
        ]
    )

    assert [finding.finding_type for finding in findings] == ["weakly_supported_claim"]
