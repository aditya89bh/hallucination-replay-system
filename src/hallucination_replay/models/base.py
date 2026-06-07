"""Shared base model helpers for trace schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class TraceModel(BaseModel):
    """Base model with common serialization helpers."""

    model_config = ConfigDict(extra="forbid")

    def to_dict(self) -> dict[str, Any]:
        """Serialize the model to a JSON-compatible dictionary."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialize the model to a JSON string."""
        return self.model_dump_json()
