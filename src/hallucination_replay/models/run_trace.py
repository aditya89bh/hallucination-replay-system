"""Run trace schema model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RunStatus = Literal["running", "completed", "failed"]


class RunTrace(BaseModel):
    """Top-level execution trace for a single agent run."""

    run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: RunStatus
    metadata: dict[str, Any] = Field(default_factory=dict)
