"""Shared base model helpers for trace schemas."""

from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, ConfigDict


class TraceModel(BaseModel):
    """Base model with common serialization and deserialization helpers."""

    model_config = ConfigDict(extra="forbid")

    def to_dict(self) -> dict[str, Any]:
        """Serialize the model to a JSON-compatible dictionary."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialize the model to a JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Deserialize a model from a dictionary payload."""
        return cls.model_validate(payload)

    @classmethod
    def from_json(cls, payload: str | bytes | bytearray) -> Self:
        """Deserialize a model from a JSON payload."""
        return cls.model_validate_json(payload)
