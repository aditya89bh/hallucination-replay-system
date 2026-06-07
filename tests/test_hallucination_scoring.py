from __future__ import annotations

from hallucination_replay.hallucination import (
    EvidenceCoverageScore,
    UnsupportedClaimFinding,
    score_hallucinations,
)

EXPECTED_COVERAGE = 0.5
EXPECTED_SCORE = 0.3


def test_score_hallucinations_aggregates_inputs() -> None:
    unsupported = [
        UnsupportedClaimFinding(
            claim_id="c1",
            claim_text="x",
            finding_type="unsupported_claim",
            support_score=0.0,
        )
    ]
    coverage = EvidenceCoverageScore(
        total_claims=2, supported_claims=1, coverage_score=EXPECTED_COVERAGE
    )

    score = score_hallucinations(unsupported, [], coverage)

    assert score.unsupported_count == 1
    assert score.contradiction_count == 0
    assert score.evidence_coverage == EXPECTED_COVERAGE
    assert score.score == EXPECTED_SCORE
