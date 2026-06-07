"""Trace search utilities backed by the persistent index."""

from __future__ import annotations

from collections.abc import Iterable

from hallucination_replay.storage.index import TraceIndex, TraceIndexEntry


class TraceSearch:
    """Search indexed traces by common metadata fields."""

    def __init__(self, index: TraceIndex) -> None:
        """Create a search helper for an index."""
        self._index = index

    def by_run_id_substring(self, substring: str) -> list[TraceIndexEntry]:
        """Return traces whose run identifier contains the substring."""
        normalized_substring = substring.lower()
        return self._sorted_entries(
            entry
            for entry in self._index.entries.values()
            if normalized_substring in entry.run_id.lower()
        )

    def by_agent_name(self, agent_name: str) -> list[TraceIndexEntry]:
        """Return traces produced by an agent name."""
        return self._sorted_entries(
            entry
            for entry in self._index.entries.values()
            if entry.agent_name == agent_name
        )

    def by_tag(self, tag: str) -> list[TraceIndexEntry]:
        """Return traces containing a tag."""
        return self._sorted_entries(
            entry for entry in self._index.entries.values() if tag in entry.tags
        )

    def by_status(self, status: str) -> list[TraceIndexEntry]:
        """Return traces matching a run status."""
        return self._sorted_entries(
            entry for entry in self._index.entries.values() if entry.status == status
        )

    @staticmethod
    def _sorted_entries(entries: Iterable[TraceIndexEntry]) -> list[TraceIndexEntry]:
        return sorted(entries, key=lambda entry: entry.run_id)
