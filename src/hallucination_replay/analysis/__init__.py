"""Failure analysis package."""

from hallucination_replay.analysis.confidence import (
    ConfidenceScore,
    score_finding_confidence,
    score_findings,
)
from hallucination_replay.analysis.contributing_factors import (
    ContributingFactorAnalysis,
    analyze_contributing_factors,
)
from hallucination_replay.analysis.intent import analyze_intent_failures
from hallucination_replay.analysis.memory import analyze_memory_failures
from hallucination_replay.analysis.output import analyze_output_failures
from hallucination_replay.analysis.ranking import RankedRootCause, rank_root_causes
from hallucination_replay.analysis.reasoning import analyze_reasoning_failures
from hallucination_replay.analysis.retrieval import analyze_retrieval_failures
from hallucination_replay.analysis.summaries import (
    generate_detailed_failure_summary,
    generate_short_failure_summary,
)
from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.analysis.tools import analyze_tool_failures
from hallucination_replay.analysis.validation import analyze_validation_failures

__all__ = [
    "ConfidenceScore",
    "ContributingFactorAnalysis",
    "FailureFinding",
    "FailureType",
    "RankedRootCause",
    "analyze_contributing_factors",
    "analyze_intent_failures",
    "analyze_memory_failures",
    "analyze_output_failures",
    "analyze_reasoning_failures",
    "analyze_retrieval_failures",
    "analyze_tool_failures",
    "analyze_validation_failures",
    "generate_detailed_failure_summary",
    "generate_short_failure_summary",
    "rank_root_causes",
    "score_finding_confidence",
    "score_findings",
]
