"""Trace metadata schema model."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TraceEnvironment = Literal["development", "test", "staging", "production"]


class TraceMetadata(BaseModel):
    """Descriptive metadata for an agent execution trace."""

    agent_name: str
    agent_version: str
    framework: str
    environment: TraceEnvironment
    tags: list[str] = Field(default_factory=list)
