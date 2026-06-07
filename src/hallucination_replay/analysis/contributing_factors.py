"""Contributing factor analysis for ranked failures."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.analysis.ranking import RankedRootCause, rank_root_causes
from hallucination_replay.analysis.taxonomy import FailureFinding
from hallucination_replay.models.base import TraceModel


class ContributingFactorAnalysis(TraceModel):
    """Structured primary, secondary, and contributing factors."""

    primary_failure: RankedRootCause | None = None
    secondary_failures: list[RankedRootCause] = Field(default_factory=list)
    contributing_factors: list[FailureFinding] = Field(default_factory=list)


def analyze_contributing_factors(
    findings: list[FailureFinding],
) -> ContributingFactorAnalysis:
    """Classify ranked findings into primary, secondary, and contributing groups."""
    ranked = rank_root_causes(findings)
    if not ranked:
        return ContributingFactorAnalysis()
    primary = ranked[0]
    secondary = [
        item
        for item in ranked[1:]
        if item.finding.severity >= primary.finding.severity - 1
    ]
    secondary_messages = {item.finding.message for item in secondary}
    contributing = [
        item.finding
        for item in ranked[1:]
        if item.finding.message not in secondary_messages
    ]
    return ContributingFactorAnalysis(
        primary_failure=primary,
        secondary_failures=secondary,
        contributing_factors=contributing,
    )
