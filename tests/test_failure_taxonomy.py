from __future__ import annotations

import pytest
from pydantic import ValidationError

from hallucination_replay.analysis import FailureFinding, FailureType


def test_failure_type_values_are_stable() -> None:
    assert [failure_type.value for failure_type in FailureType] == [
        "intent_failure",
        "retrieval_failure",
        "memory_failure",
        "tool_failure",
        "validation_failure",
        "reasoning_failure",
        "output_failure",
        "unknown_failure",
    ]


def test_failure_finding_model_serializes() -> None:
    finding = FailureFinding(
        failure_type=FailureType.INTENT_FAILURE,
        message="Missing user objective",
        severity=4,
        confidence=0.75,
        evidence=["No user prompt was captured"],
        step_index=2,
        metadata={"analyzer": "intent"},
    )

    assert finding.to_dict()["failure_type"] == "intent_failure"
    assert finding.evidence == ["No user prompt was captured"]


def test_failure_finding_validates_bounds() -> None:
    with pytest.raises(ValidationError):
        FailureFinding(
            failure_type=FailureType.UNKNOWN_FAILURE,
            message="",
            severity=6,
            confidence=1.5,
        )
