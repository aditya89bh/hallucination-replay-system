from __future__ import annotations

from hallucination_replay.hallucination import (
    Evidence,
    normalize_evidence,
    normalize_evidence_records,
)

SOURCE_STEP = 2


def test_normalize_evidence_preserves_metadata() -> None:
    evidence = Evidence(
        evidence_id="e1",
        text="  Paris, FRANCE! ",
        source="tool",
        source_step=SOURCE_STEP,
    )

    normalized = normalize_evidence(evidence)

    assert normalized.evidence_id == "e1"
    assert normalized.text == "paris france"
    assert normalized.source == "tool"
    assert normalized.source_step == SOURCE_STEP


def test_normalize_evidence_records() -> None:
    records = [Evidence(evidence_id="e1", text="A, B.", source="memory", source_step=1)]

    assert [item.text for item in normalize_evidence_records(records)] == ["a b"]
