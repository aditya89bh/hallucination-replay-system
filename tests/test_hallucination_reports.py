from __future__ import annotations

import json

from hallucination_replay.hallucination import (
    Claim,
    Evidence,
    EvidenceMatch,
    HallucinationScore,
    HallucinationSeverity,
    generate_hallucination_json_report,
    generate_hallucination_markdown_report,
)


def test_generate_hallucination_reports_include_core_sections() -> None:
    claim = Claim(
        claim_id="c1", text="Paris is in France", source_step=1, confidence=0.8
    )
    evidence = Evidence(
        evidence_id="e1", text="Paris is in France", source="retrieval", source_step=1
    )
    match = EvidenceMatch(claim=claim, matched_evidence=[evidence], support_score=1.0)
    score = HallucinationScore(
        unsupported_count=0, contradiction_count=0, evidence_coverage=1.0, score=0.0
    )

    markdown = generate_hallucination_markdown_report(
        [claim], [evidence], [match], [], score, HallucinationSeverity.LOW
    )
    payload = json.loads(
        generate_hallucination_json_report(
            [claim], [evidence], [match], [], score, HallucinationSeverity.LOW
        )
    )

    assert markdown.startswith("# Hallucination Report")
    assert "## Support Scores" in markdown
    assert payload["severity"] == "low"
    assert payload["claims"][0]["claim_id"] == "c1"
