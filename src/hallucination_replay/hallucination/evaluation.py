"""Evaluation suite for hallucination benchmark traces."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from hallucination_replay.hallucination.benchmarks import (
    DEFAULT_BENCHMARK_DIRECTORY,
    load_hallucination_benchmark_traces,
)
from hallucination_replay.hallucination.claims import extract_claims_from_outputs
from hallucination_replay.hallucination.contradictions import detect_contradictions
from hallucination_replay.hallucination.coverage import score_evidence_coverage
from hallucination_replay.hallucination.evidence import extract_evidence
from hallucination_replay.hallucination.matching import match_claims_to_evidence
from hallucination_replay.hallucination.unsupported import detect_unsupported_claims
from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel

POSITIVE_EXPECTATIONS = {
    "contradiction",
    "partially_supported_claim",
    "unsupported_claim",
}
DEFAULT_MIN_SUPPORT_COVERAGE = 0.0
DEFAULT_MAX_SUPPORT_COVERAGE = 1.0


class HallucinationBenchmarkResult(TraceModel):
    """Evaluation result for one benchmark trace."""

    run_id: str
    expected: str
    detected_hallucination: bool
    detected_contradiction: bool
    support_coverage: float = Field(ge=0.0, le=1.0)
    expected_min_support_coverage: float = Field(ge=0.0, le=1.0)
    expected_max_support_coverage: float = Field(ge=0.0, le=1.0)
    within_expected_support_threshold: bool


class HallucinationEvaluationMetrics(TraceModel):
    """Aggregate deterministic hallucination benchmark metrics."""

    total_traces: int
    detection_rate: float = Field(ge=0.0, le=1.0)
    contradiction_rate: float = Field(ge=0.0, le=1.0)
    support_coverage: float = Field(ge=0.0, le=1.0)
    threshold_pass_rate: float = Field(ge=0.0, le=1.0)
    results: list[HallucinationBenchmarkResult]


def evaluate_hallucination_benchmarks(
    directory: Path = DEFAULT_BENCHMARK_DIRECTORY,
) -> HallucinationEvaluationMetrics:
    """Load and evaluate hallucination benchmark traces."""
    return evaluate_hallucination_traces(load_hallucination_benchmark_traces(directory))


def evaluate_hallucination_traces(
    traces: list[RunTrace],
) -> HallucinationEvaluationMetrics:
    """Evaluate already-loaded hallucination benchmark traces."""
    results = [_evaluate_trace(trace) for trace in traces]
    positive_results = [
        result for result in results if result.expected in POSITIVE_EXPECTATIONS
    ]
    contradiction_results = [
        result for result in results if result.expected == "contradiction"
    ]
    detection_rate = _rate(
        sum(1 for result in positive_results if result.detected_hallucination),
        len(positive_results),
    )
    contradiction_rate = _rate(
        sum(1 for result in contradiction_results if result.detected_contradiction),
        len(contradiction_results),
    )
    support_coverage = _rate(
        sum(result.support_coverage for result in results),
        len(results),
    )
    threshold_pass_rate = _rate(
        sum(1 for result in results if result.within_expected_support_threshold),
        len(results),
    )
    return HallucinationEvaluationMetrics(
        total_traces=len(results),
        detection_rate=detection_rate,
        contradiction_rate=contradiction_rate,
        support_coverage=support_coverage,
        threshold_pass_rate=threshold_pass_rate,
        results=results,
    )


def _evaluate_trace(trace: RunTrace) -> HallucinationBenchmarkResult:
    claims = extract_claims_from_outputs(_output_records(trace))
    evidence = extract_evidence(
        trace, step_index=max((claim.source_step for claim in claims), default=0)
    )
    matches = match_claims_to_evidence(claims, evidence)
    unsupported = detect_unsupported_claims(matches)
    contradictions = detect_contradictions(claims, evidence)
    coverage = score_evidence_coverage(matches)
    min_support_coverage = _threshold(trace, "expected_support_coverage_min")
    max_support_coverage = _threshold(trace, "expected_support_coverage_max")
    return HallucinationBenchmarkResult(
        run_id=trace.run_id,
        expected=_expected(trace),
        detected_hallucination=bool(unsupported or contradictions),
        detected_contradiction=bool(contradictions),
        support_coverage=coverage.coverage_score,
        expected_min_support_coverage=min_support_coverage,
        expected_max_support_coverage=max_support_coverage,
        within_expected_support_threshold=(
            min_support_coverage <= coverage.coverage_score <= max_support_coverage
        ),
    )


def _output_records(trace: RunTrace) -> list[dict[str, object]]:
    outputs = trace.metadata.get("outputs", [])
    return (
        [record for record in outputs if isinstance(record, dict)]
        if isinstance(outputs, list)
        else []
    )


def _expected(trace: RunTrace) -> str:
    expected = trace.metadata.get("expected_hallucination", "unknown")
    return expected if isinstance(expected, str) else "unknown"


def _threshold(trace: RunTrace, key: str) -> float:
    value = trace.metadata.get(key)
    if isinstance(value, int | float):
        return max(
            DEFAULT_MIN_SUPPORT_COVERAGE,
            min(DEFAULT_MAX_SUPPORT_COVERAGE, float(value)),
        )
    if key.endswith("_min"):
        return DEFAULT_MIN_SUPPORT_COVERAGE
    return DEFAULT_MAX_SUPPORT_COVERAGE


def _rate(numerator: float, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
