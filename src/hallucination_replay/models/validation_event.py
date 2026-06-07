"""Validation event schema model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, StrictBool


class ValidationEvent(BaseModel):
    """Result from a validation check over an agent step or trace."""

    validator_name: str
    passed: StrictBool
    findings: list[str] = Field(default_factory=list)
    timestamp: datetime
