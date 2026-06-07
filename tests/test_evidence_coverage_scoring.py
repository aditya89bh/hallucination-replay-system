from __future__ import annotations

from hallucination_replay.hallucination import (
    Claim,
    EvidenceMatch,
    score_evidence_coverage,
)

TOTAL_CLAIMS = 2
EXPECTED_COVERAGE = 0.5


def test_score_evidence_coverage_counts_supported_claims() -> None:
    claim = Claim(
        claim_id="c1", text="A supported claim", source_step=1, confidence=0.8
    )
    score = score_evidence_coverage(
        [
            EvidenceMatch(claim=claim, support_score=0.7),
            EvidenceMatch(claim=claim, support_score=0.2),
        ]
    )

    assert score.total_claims == TOTAL_CLAIMS
    assert score.supported_claims == 1
    assert score.coverage_score == EXPECTED_COVERAGE


def test_score_evidence_coverage_handles_empty_claims() -> None:
    assert score_evidence_coverage([]).coverage_score == 1.0
