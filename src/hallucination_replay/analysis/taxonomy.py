"""Failure taxonomy and shared analysis models."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from hallucination_replay.models.base import TraceModel


class FailureType(StrEnum):
    """High-level categories for root-cause findings."""

    INTENT_FAILURE = "intent_failure"
    RETRIEVAL_FAILURE = "retrieval_failure"
    MEMORY_FAILURE = "memory_failure"
    TOOL_FAILURE = "tool_failure"
    VALIDATION_FAILURE = "validation_failure"
    REASONING_FAILURE = "reasoning_failure"
    OUTPUT_FAILURE = "output_failure"
    UNKNOWN_FAILURE = "unknown_failure"


class FailureFinding(TraceModel):
    """Structured finding produced by failure analyzers."""

    failure_type: FailureType
    message: str = Field(min_length=1)
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    step_index: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
