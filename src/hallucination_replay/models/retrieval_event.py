"""Retrieval event schema model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetrievalEvent(BaseModel):
    """Evidence retrieved for an agent step."""

    query: str
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_time_ms: float = Field(ge=0)
    source: str
