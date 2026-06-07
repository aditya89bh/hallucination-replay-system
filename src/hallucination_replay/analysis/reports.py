"""Failure analysis report generation."""

from __future__ import annotations

import json
from typing import Any

from hallucination_replay.analysis.confidence import score_findings
from hallucination_replay.analysis.contributing_factors import (
    analyze_contributing_factors,
)
from hallucination_replay.analysis.ranking import rank_root_causes
from hallucination_replay.analysis.summaries import generate_detailed_failure_summary
from hallucination_replay.analysis.taxonomy import FailureFinding


def generate_failure_markdown_report(findings: list[FailureFinding]) -> str:
    """Generate a markdown failure analysis report."""
    ranked = rank_root_causes(findings)
    confidence_scores = score_findings(findings)
    factors = analyze_contributing_factors(findings)
    lines = [
        "# Failure Analysis Report",
        "",
        "## Summary",
        generate_detailed_failure_summary(findings),
        "",
        "## Ranked Root Causes",
    ]
    if not ranked:
        lines.append("No ranked root causes.")
    else:
        lines.extend(
            f"{item.rank}. {item.finding.message} "
            f"[{item.finding.failure_type.value}] "
            f"confidence={item.confidence_score:.4f}"
            for item in ranked
        )
    lines.extend(["", "## Confidence Scores"])
    if not confidence_scores:
        lines.append("No confidence scores.")
    else:
        lines.extend(
            f"- {score.finding_message}: {score.score:.4f}"
            for score in confidence_scores
        )
    lines.extend(["", "## Contributing Factors"])
    if factors.primary_failure is None:
        lines.append("No primary failure identified.")
    else:
        lines.append(f"Primary: {factors.primary_failure.finding.message}")
        lines.extend(
            f"Secondary: {item.finding.message}" for item in factors.secondary_failures
        )
        lines.extend(
            f"Contributing: {finding.message}"
            for finding in factors.contributing_factors
        )
    return "\n".join(lines)


def generate_failure_json_report(findings: list[FailureFinding]) -> str:
    """Generate a deterministic JSON failure analysis report."""
    payload: dict[str, Any] = {
        "findings": [finding.to_dict() for finding in findings],
        "ranking": [item.to_dict() for item in rank_root_causes(findings)],
        "confidence": [score.to_dict() for score in score_findings(findings)],
        "contributing_factors": analyze_contributing_factors(findings).to_dict(),
    }
    return json.dumps(payload, sort_keys=True)
