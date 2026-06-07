"""Persistent trace index for storage backends."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from hallucination_replay.models import RunTrace


class TraceIndexEntry(BaseModel):
    """Searchable summary for a stored run trace."""

    run_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    agent_name: str | None = None
    tags: list[str] = Field(default_factory=list)


class TraceIndex(BaseModel):
    """Persistent mapping from run identifiers to trace summaries."""

    entries: dict[str, TraceIndexEntry] = Field(default_factory=dict)

    @classmethod
    def load(cls, index_path: Path) -> TraceIndex:
        """Load an index from disk or return an empty index."""
        if not index_path.exists():
            return cls()
        payload: Any = json.loads(index_path.read_text(encoding="utf-8"))
        return cls.model_validate(payload)

    def save(self, index_path: Path) -> None:
        """Persist the index as readable JSON."""
        index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = index_path.with_suffix(".json.tmp")
        temporary_path.write_text(
            json.dumps(self.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(index_path)

    def update_trace(self, trace: RunTrace) -> None:
        """Create or replace the index entry for a trace."""
        self.entries[trace.run_id] = TraceIndexEntry(
            run_id=trace.run_id,
            status=trace.status,
            started_at=trace.started_at,
            completed_at=trace.completed_at,
            agent_name=self._agent_name(trace),
            tags=self._tags(trace),
        )

    def remove_trace(self, run_id: str) -> None:
        """Remove a trace from the index if present."""
        self.entries.pop(run_id, None)

    def list_run_ids(self) -> list[str]:
        """Return indexed run identifiers."""
        return sorted(self.entries)

    def count_by_status(self) -> dict[str, int]:
        """Count indexed traces by status."""
        counts: dict[str, int] = {}
        for entry in self.entries.values():
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return dict(sorted(counts.items()))

    def count_by_agent_name(self) -> dict[str, int]:
        """Count indexed traces by agent name."""
        counts: dict[str, int] = {}
        for entry in self.entries.values():
            if entry.agent_name is not None:
                counts[entry.agent_name] = counts.get(entry.agent_name, 0) + 1
        return dict(sorted(counts.items()))

    def list_unique_tags(self) -> list[str]:
        """Return all unique tags in the index."""
        return sorted({tag for entry in self.entries.values() for tag in entry.tags})

    def list_unique_agents(self) -> list[str]:
        """Return all unique agent names in the index."""
        return sorted(
            {entry.agent_name for entry in self.entries.values() if entry.agent_name}
        )

    @staticmethod
    def _agent_name(trace: RunTrace) -> str | None:
        agent_name = trace.metadata.get("agent_name")
        if isinstance(agent_name, str):
            return agent_name
        nested_metadata = trace.metadata.get("trace_metadata")
        if isinstance(nested_metadata, dict):
            nested_agent_name = nested_metadata.get("agent_name")
            if isinstance(nested_agent_name, str):
                return nested_agent_name
        return None

    @staticmethod
    def _tags(trace: RunTrace) -> list[str]:
        tags = trace.metadata.get("tags")
        if isinstance(tags, list):
            return [tag for tag in tags if isinstance(tag, str)]
        nested_metadata = trace.metadata.get("trace_metadata")
        if isinstance(nested_metadata, dict):
            nested_tags = nested_metadata.get("tags")
            if isinstance(nested_tags, list):
                return [tag for tag in nested_tags if isinstance(tag, str)]
        return []
