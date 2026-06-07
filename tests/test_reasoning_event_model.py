from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models.reasoning_event import ReasoningEvent

CONFIDENCE = 0.8


def test_reasoning_event_accepts_summary_without_chain_of_thought() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    event = ReasoningEvent(
        reasoning_type="decision",
        summary="The agent selected the highest-ranked retrieval result.",
        confidence=CONFIDENCE,
        timestamp=timestamp,
    )

    assert event.reasoning_type == "decision"
    assert event.summary == "The agent selected the highest-ranked retrieval result."
    assert event.confidence == CONFIDENCE
    assert event.timestamp == timestamp


def test_reasoning_event_rejects_invalid_reasoning_type() -> None:
    payload = {
        "reasoning_type": "chain_of_thought",
        "summary": "Do not store hidden reasoning.",
        "confidence": CONFIDENCE,
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
    }

    with pytest.raises(ValidationError, match="reasoning_type"):
        ReasoningEvent.model_validate(payload)


def test_reasoning_event_rejects_confidence_outside_range() -> None:
    payload = {
        "reasoning_type": "decision",
        "summary": "Invalid confidence.",
        "confidence": 1.5,
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
    }

    with pytest.raises(ValidationError, match="confidence"):
        ReasoningEvent.model_validate(payload)
