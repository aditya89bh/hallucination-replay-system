from __future__ import annotations

from hallucination_replay.hallucination import Claim, Evidence, detect_contradictions

TOOL_CONTRADICTION_SEVERITY = 5


def test_detect_contradictions_finds_claim_conflict_with_tool_result() -> None:
    claim = Claim(
        claim_id="c1", text="The payment succeeded", source_step=2, confidence=0.9
    )
    evidence = [
        Evidence(evidence_id="e1", text="payment failed", source="tool", source_step=1)
    ]

    findings = detect_contradictions([claim], evidence)

    assert findings[0].conflict_reason == "negation_mismatch"
    assert findings[0].evidence_source == "tool"
    assert findings[0].severity == TOOL_CONTRADICTION_SEVERITY


def test_detect_contradictions_ignores_non_overlapping_evidence() -> None:
    claim = Claim(
        claim_id="c1", text="The payment succeeded", source_step=2, confidence=0.9
    )
    evidence = [
        Evidence(
            evidence_id="e1", text="weather failed", source="memory", source_step=1
        )
    ]

    assert detect_contradictions([claim], evidence) == []
