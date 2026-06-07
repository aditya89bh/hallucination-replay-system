from __future__ import annotations

import pytest
from pydantic import ValidationError

from hallucination_replay.models.trace_metadata import TraceMetadata


def test_trace_metadata_accepts_required_fields() -> None:
    metadata = TraceMetadata(
        agent_name="research-agent",
        agent_version="1.2.3",
        framework="langgraph",
        environment="production",
        tags=["retrieval", "incident-42"],
    )

    assert metadata.agent_name == "research-agent"
    assert metadata.agent_version == "1.2.3"
    assert metadata.framework == "langgraph"
    assert metadata.environment == "production"
    assert metadata.tags == ["retrieval", "incident-42"]


def test_trace_metadata_defaults_tags() -> None:
    metadata = TraceMetadata(
        agent_name="research-agent",
        agent_version="1.2.3",
        framework="langgraph",
        environment="test",
    )

    assert metadata.tags == []


def test_trace_metadata_rejects_invalid_environment() -> None:
    payload = {
        "agent_name": "research-agent",
        "agent_version": "1.2.3",
        "framework": "langgraph",
        "environment": "sandbox",
        "tags": [],
    }

    with pytest.raises(ValidationError, match="environment"):
        TraceMetadata.model_validate(payload)
