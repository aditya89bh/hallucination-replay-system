"""HTML failure analysis viewer."""

from __future__ import annotations

from html import escape

from hallucination_replay.analysis import rank_root_causes, score_findings
from hallucination_replay.analysis.taxonomy import FailureFinding


def render_failure_analysis_viewer(findings: list[FailureFinding]) -> str:
    """Render findings, root causes, and confidence scores as deterministic HTML."""
    finding_items = "\n".join(
        f'<li data-type="{escape(finding.failure_type.value)}">'
        f"{escape(finding.message)}</li>"
        for finding in findings
    )
    root_cause_items = "\n".join(
        f'<li data-rank="{item.rank}" data-confidence="{item.confidence_score:.4f}">'
        f"{escape(item.finding.message)}</li>"
        for item in rank_root_causes(findings)
    )
    confidence_items = "\n".join(
        f'<li data-score="{score.score:.4f}">{escape(score.finding_message)}</li>'
        for score in score_findings(findings)
    )
    return (
        '<section class="failure-analysis-viewer">\n'
        "<h1>Failure Analysis</h1>\n"
        f'<ul class="findings" data-count="{len(findings)}">\n{finding_items}\n</ul>\n'
        f'<ol class="root-causes">\n{root_cause_items}\n</ol>\n'
        f'<ul class="confidence">\n{confidence_items}\n</ul>\n'
        "</section>"
    )
