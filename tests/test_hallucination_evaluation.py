from __future__ import annotations

from hallucination_replay.hallucination import evaluate_hallucination_benchmarks

EXPECTED_TRACE_COUNT = 4
EXPECTED_DETECTION_RATE = 1.0
EXPECTED_CONTRADICTION_RATE = 1.0
EXPECTED_THRESHOLD_PASS_RATE = 1.0
EXPECTED_PARTIAL_COVERAGE = 0.5


def test_evaluate_hallucination_benchmarks_reports_metrics() -> None:
    metrics = evaluate_hallucination_benchmarks()

    assert metrics.total_traces == EXPECTED_TRACE_COUNT
    assert metrics.detection_rate == EXPECTED_DETECTION_RATE
    assert metrics.contradiction_rate == EXPECTED_CONTRADICTION_RATE
    assert metrics.threshold_pass_rate == EXPECTED_THRESHOLD_PASS_RATE
    assert {result.expected for result in metrics.results} == {
        "contradiction",
        "fully_supported_claim",
        "partially_supported_claim",
        "unsupported_claim",
    }
    assert metrics.support_coverage < 1.0


def test_partially_supported_benchmark_has_explicit_thresholds() -> None:
    metrics = evaluate_hallucination_benchmarks()
    partial = next(
        result
        for result in metrics.results
        if result.expected == "partially_supported_claim"
    )

    assert partial.detected_hallucination is True
    assert partial.support_coverage == EXPECTED_PARTIAL_COVERAGE
    assert partial.expected_min_support_coverage == EXPECTED_PARTIAL_COVERAGE
    assert partial.expected_max_support_coverage == EXPECTED_PARTIAL_COVERAGE
    assert partial.within_expected_support_threshold is True
