from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hallucination_replay.models import (
    AgentStep,
    MemoryEvent,
    ReasoningEvent,
    RunTrace,
    ToolCall,
    ToolResult,
    TraceMetadata,
    ValidationEvent,
)
from hallucination_replay.models.base import TraceModel

ValidationCase = tuple[type[TraceModel], dict[str, object], str]

REQUIRED_FIELD_CASES: list[ValidationCase] = [
    (
        RunTrace,
        {"started_at": datetime(2026, 1, 1, tzinfo=UTC), "status": "running"},
        "run_id",
    ),
    (
        AgentStep,
        {
            "step_id": "step-1",
            "step_type": "tool",
            "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
            "description": "Missing index",
        },
        "step_index",
    ),
    (
        ToolCall,
        {
            "tool_name": "search",
            "arguments": {},
            "invocation_time": datetime(2026, 1, 1, tzinfo=UTC),
        },
        "step_id",
    ),
]

INVALID_TYPE_CASES: list[ValidationCase] = [
    (
        ToolCall,
        {
            "tool_name": "search",
            "arguments": ["not-a-dict"],
            "invocation_time": datetime(2026, 1, 1, tzinfo=UTC),
            "step_id": "step-1",
        },
        "arguments",
    ),
    (
        ToolResult,
        {
            "tool_name": "search",
            "success": "true",
            "output": "done",
            "execution_time_ms": 1,
            "step_id": "step-1",
        },
        "success",
    ),
    (
        ValidationEvent,
        {
            "validator_name": "schema-checker",
            "passed": "false",
            "findings": [],
            "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        },
        "passed",
    ),
]

INVALID_ENUM_CASES: list[ValidationCase] = [
    (
        RunTrace,
        {
            "run_id": "run-1",
            "started_at": datetime(2026, 1, 1, tzinfo=UTC),
            "status": "bad",
        },
        "status",
    ),
    (
        AgentStep,
        {
            "step_id": "step-1",
            "step_index": 0,
            "step_type": "bad",
            "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
            "description": "Invalid enum",
        },
        "step_type",
    ),
    (
        MemoryEvent,
        {
            "event_type": "delete",
            "key": "memory-key",
            "value": None,
            "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        },
        "event_type",
    ),
    (
        ReasoningEvent,
        {
            "reasoning_type": "chain_of_thought",
            "summary": "Invalid enum",
            "confidence": 0.5,
            "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        },
        "reasoning_type",
    ),
    (
        TraceMetadata,
        {
            "agent_name": "agent",
            "agent_version": "1.0.0",
            "framework": "custom",
            "environment": "sandbox",
            "tags": [],
        },
        "environment",
    ),
]


@pytest.mark.parametrize(("model_type", "payload", "field_name"), REQUIRED_FIELD_CASES)
def test_required_fields_are_validated(
    model_type: type[TraceModel], payload: dict[str, object], field_name: str
) -> None:
    with pytest.raises(ValidationError, match=field_name):
        model_type.model_validate(payload)


@pytest.mark.parametrize(("model_type", "payload", "field_name"), INVALID_TYPE_CASES)
def test_invalid_types_are_validated(
    model_type: type[TraceModel], payload: dict[str, object], field_name: str
) -> None:
    with pytest.raises(ValidationError, match=field_name):
        model_type.model_validate(payload)


@pytest.mark.parametrize(("model_type", "payload", "field_name"), INVALID_ENUM_CASES)
def test_invalid_enums_are_validated(
    model_type: type[TraceModel], payload: dict[str, object], field_name: str
) -> None:
    with pytest.raises(ValidationError, match=field_name):
        model_type.model_validate(payload)
