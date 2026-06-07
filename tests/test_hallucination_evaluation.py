from __future__ import annotations

from hallucination_replay.hallucination import evaluate_hallucination_benchmarks

EXPECTED_TRACE_COUNT = 4
EXPECTED_DETECTION_RATE = 1.0
EXPECTED_CONTRADICTION_RATE = 1.0


def test_evaluate_hallucination_benchmarks_reports_metrics() -> None:
    metrics = evaluate_hallucination_benchmarks()

    assert metrics.total_traces == EXPECTED_TRACE_COUNT
    assert metrics.detection_rate == EXPECTED_DETECTION_RATE
    assert metrics.contradiction_rate == EXPECTED_CONTRADICTION_RATE
    assert {result.expected for result in metrics.results} == {
        "contradiction",
        "fully_supported_claim",
        "partially_supported_claim",
        "unsupported_claim",
    }
    assert metrics.support_coverage < 1.0
