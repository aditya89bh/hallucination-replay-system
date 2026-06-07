"""HTML hallucination analysis viewer."""

from __future__ import annotations

from html import escape

from hallucination_replay.hallucination import (
    ContradictionFinding,
    HallucinationSeverity,
    UnsupportedClaimFinding,
)


def render_hallucination_viewer(
    unsupported_claims: list[UnsupportedClaimFinding],
    contradictions: list[ContradictionFinding],
    severity: HallucinationSeverity,
) -> str:
    """Render unsupported claims, contradictions, and severity as HTML."""
    unsupported_items = "\n".join(
        f'<li data-claim-id="{escape(finding.claim_id)}" '
        f'data-support-score="{finding.support_score:.4f}">'
        f"{escape(finding.claim_text)}</li>"
        for finding in unsupported_claims
    )
    contradiction_items = "\n".join(
        f'<li data-claim-id="{escape(finding.claim_id)}" '
        f'data-evidence-id="{escape(finding.evidence_id)}" '
        f'data-severity="{finding.severity}">'
        f"{escape(finding.conflict_reason)}</li>"
        for finding in contradictions
    )
    return (
        '<section class="hallucination-viewer">\n'
        f'<h1 data-severity="{escape(severity.value)}">Hallucination: '
        f"{escape(severity.value)}</h1>\n"
        f'<ul class="unsupported-claims" data-count="{len(unsupported_claims)}">\n'
        f"{unsupported_items}\n</ul>\n"
        f'<ul class="contradictions" data-count="{len(contradictions)}">\n'
        f"{contradiction_items}\n</ul>\n"
        "</section>"
    )
