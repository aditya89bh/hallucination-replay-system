from __future__ import annotations

from hallucination_replay.dashboard import render_hallucination_viewer
from hallucination_replay.hallucination import (
    ContradictionFinding,
    HallucinationSeverity,
    UnsupportedClaimFinding,
)


def test_hallucination_viewer_displays_findings_and_severity() -> None:
    html = render_hallucination_viewer(
        unsupported_claims=[
            UnsupportedClaimFinding(
                claim_id="claim-1",
                claim_text="The account is active.",
                finding_type="unsupported_claim",
                support_score=0.2,
                evidence_ids=[],
            )
        ],
        contradictions=[
            ContradictionFinding(
                claim_id="claim-2",
                claim_text="The account is not active.",
                evidence_id="evidence-1",
                evidence_text="The account is active.",
                evidence_source="tool",
                conflict_reason="negation_mismatch",
                severity=5,
            )
        ],
        severity=HallucinationSeverity.HIGH,
    )

    assert 'data-severity="high"' in html
    assert 'class="unsupported-claims" data-count="1"' in html
    assert 'data-support-score="0.2000"' in html
    assert 'class="contradictions" data-count="1"' in html
    assert "negation_mismatch" in html
