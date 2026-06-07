"""Domain exception hierarchy for hallucination replay workflows."""

from __future__ import annotations


class HallucinationReplayError(Exception):
    """Base exception for all package-specific errors."""


class StorageError(HallucinationReplayError):
    """Raised when trace storage cannot be read, written, or validated."""


class ReplayError(HallucinationReplayError):
    """Raised when an execution trace cannot be replayed safely."""


class AnalysisError(HallucinationReplayError):
    """Raised when root-cause analysis cannot be completed."""
