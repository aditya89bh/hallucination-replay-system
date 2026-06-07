"""Human-readable failure summaries."""

from __future__ import annotations

from hallucination_replay.analysis.contributing_factors import (
    ContributingFactorAnalysis,
    analyze_contributing_factors,
)
from hallucination_replay.analysis.taxonomy import FailureFinding


def generate_short_failure_summary(findings: list[FailureFinding]) -> str:
    """Generate a concise failure summary."""
    analysis = analyze_contributing_factors(findings)
    if analysis.primary_failure is None:
        return "No failure findings were identified."
    primary = analysis.primary_failure.finding
    return f"Primary failure: {primary.message} ({primary.failure_type.value})."


def generate_detailed_failure_summary(findings: list[FailureFinding]) -> str:
    """Generate a detailed human-readable failure summary."""
    analysis = analyze_contributing_factors(findings)
    if analysis.primary_failure is None:
        return "No failure findings were identified."

    lines = [generate_short_failure_summary(findings)]
    lines.extend(_secondary_lines(analysis))
    lines.extend(_contributing_lines(analysis))
    return "\n".join(lines)


def _secondary_lines(analysis: ContributingFactorAnalysis) -> list[str]:
    if not analysis.secondary_failures:
        return ["Secondary failures: none."]
    return [
        "Secondary failures:",
        *[
            f"- {item.finding.message} ({item.finding.failure_type.value})"
            for item in analysis.secondary_failures
        ],
    ]


def _contributing_lines(analysis: ContributingFactorAnalysis) -> list[str]:
    if not analysis.contributing_factors:
        return ["Contributing factors: none."]
    return [
        "Contributing factors:",
        *[
            f"- {finding.message} ({finding.failure_type.value})"
            for finding in analysis.contributing_factors
        ],
    ]
