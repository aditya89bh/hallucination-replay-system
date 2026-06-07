"""Hallucination report generation."""

from __future__ import annotations

import json
from typing import Any

from hallucination_replay.hallucination.claims import Claim
from hallucination_replay.hallucination.contradictions import ContradictionFinding
from hallucination_replay.hallucination.evidence import Evidence
from hallucination_replay.hallucination.matching import EvidenceMatch
from hallucination_replay.hallucination.scoring import HallucinationScore
from hallucination_replay.hallucination.severity import HallucinationSeverity


def generate_hallucination_markdown_report(  # noqa: PLR0913
    claims: list[Claim],
    evidence: list[Evidence],
    matches: list[EvidenceMatch],
    contradictions: list[ContradictionFinding],
    score: HallucinationScore,
    severity: HallucinationSeverity,
) -> str:
    """Generate a human-readable hallucination report."""
    lines = [
        "# Hallucination Report",
        "",
        f"Severity: {severity.value}",
        f"Score: {score.score:.4f}",
        "",
        "## Claims",
        *[f"- {claim.claim_id}: {claim.text}" for claim in claims],
        "",
        "## Evidence",
        *[f"- {item.evidence_id} ({item.source}): {item.text}" for item in evidence],
        "",
        "## Support Scores",
        *[f"- {match.claim.claim_id}: {match.support_score:.4f}" for match in matches],
        "",
        "## Contradictions",
    ]
    lines.extend(
        [
            f"- {finding.claim_id} conflicts with {finding.evidence_id}"
            for finding in contradictions
        ]
        or ["No contradictions detected."]
    )
    return "\n".join(lines)


def generate_hallucination_json_report(  # noqa: PLR0913
    claims: list[Claim],
    evidence: list[Evidence],
    matches: list[EvidenceMatch],
    contradictions: list[ContradictionFinding],
    score: HallucinationScore,
    severity: HallucinationSeverity,
) -> str:
    """Generate a deterministic JSON hallucination report."""
    payload: dict[str, Any] = {
        "claims": [claim.to_dict() for claim in claims],
        "contradictions": [finding.to_dict() for finding in contradictions],
        "evidence": [item.to_dict() for item in evidence],
        "severity": severity.value,
        "score": score.to_dict(),
        "support_scores": [match.to_dict() for match in matches],
    }
    return json.dumps(payload, sort_keys=True)
