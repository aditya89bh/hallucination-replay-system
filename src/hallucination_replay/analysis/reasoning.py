"""Reasoning failure analysis without chain-of-thought inference."""

from __future__ import annotations

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_reasoning

MIN_CONFIDENCE_POINTS = 2
COLLAPSE_DROP_THRESHOLD = 0.4
HIGH_CONFIDENCE_THRESHOLD = 0.5
LOW_CONFIDENCE_THRESHOLD = 0.25


def analyze_reasoning_failures(
    trace: RunTrace, step_index: int
) -> list[FailureFinding]:
    """Detect missing summaries, confidence collapse, and inconsistencies."""
    reasoning = reconstruct_reasoning(trace, step_index)
    findings: list[FailureFinding] = []

    if not reasoning.summaries:
        findings.append(
            FailureFinding(
                failure_type=FailureType.REASONING_FAILURE,
                message="Missing reasoning records",
                severity=3,
                confidence=0.9,
                evidence=["No reasoning summaries were available at this step"],
                step_index=step_index,
                metadata={"reason": "missing_reasoning_records"},
            )
        )
        return findings

    collapse = _confidence_collapse(
        [point.confidence for point in reasoning.confidence_evolution]
    )
    if collapse is not None:
        findings.append(
            FailureFinding(
                failure_type=FailureType.REASONING_FAILURE,
                message="Confidence collapse",
                severity=4,
                confidence=0.85,
                evidence=[collapse],
                step_index=step_index,
                metadata={"reason": "confidence_collapse"},
            )
        )

    inconsistencies = _strings_by_step(
        trace.metadata.get("inconsistent_reasoning_summaries", []), step_index
    )
    if inconsistencies:
        findings.append(
            FailureFinding(
                failure_type=FailureType.REASONING_FAILURE,
                message="Inconsistent reasoning summaries",
                severity=4,
                confidence=0.8,
                evidence=inconsistencies,
                step_index=step_index,
                metadata={"reason": "inconsistent_reasoning_summaries"},
            )
        )

    return findings


def _confidence_collapse(confidences: list[float]) -> str | None:
    if len(confidences) < MIN_CONFIDENCE_POINTS:
        return None
    peak = confidences[0]
    for confidence in confidences[1:]:
        peak = max(peak, confidence)
        if peak - confidence >= COLLAPSE_DROP_THRESHOLD or (
            peak >= HIGH_CONFIDENCE_THRESHOLD and confidence <= LOW_CONFIDENCE_THRESHOLD
        ):
            return f"Confidence dropped from {peak:.2f} to {confidence:.2f}"
    return None


def _strings_by_step(raw_items: object, step_index: int) -> list[str]:
    if not isinstance(raw_items, list):
        return []
    values: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            item_step = item.get("step_index", 0)
            value = item.get("summary", item.get("value", ""))
            if (
                isinstance(item_step, int)
                and item_step <= step_index
                and isinstance(value, str)
            ):
                values.append(value)
        elif isinstance(item, str):
            values.append(item)
    return sorted(value for value in values if value.strip())
