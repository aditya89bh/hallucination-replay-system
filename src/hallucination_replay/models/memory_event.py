"""Memory event schema model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from hallucination_replay.models.base import TraceModel

MemoryEventType = Literal["read", "write"]


class MemoryEvent(TraceModel):
    """A memory read or write observed during an agent run."""

    event_type: MemoryEventType
    key: str
    value: Any = None
    timestamp: datetime
