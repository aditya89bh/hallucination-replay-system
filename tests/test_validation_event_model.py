from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models.validation_event import ValidationEvent


def test_validation_event_accepts_required_fields() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    event = ValidationEvent(
        validator_name="citation-checker",
        passed=False,
        findings=["Missing support for claim"],
        timestamp=timestamp,
    )

    assert event.validator_name == "citation-checker"
    assert event.passed is False
    assert event.findings == ["Missing support for claim"]
    assert event.timestamp == timestamp


def test_validation_event_defaults_findings() -> None:
    event = ValidationEvent(
        validator_name="schema-checker",
        passed=True,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert event.findings == []


def test_validation_event_rejects_invalid_passed_type() -> None:
    payload = {
        "validator_name": "schema-checker",
        "passed": "true",
        "findings": [],
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
    }

    with pytest.raises(ValidationError, match="passed"):
        ValidationEvent.model_validate(payload)
