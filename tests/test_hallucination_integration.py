from __future__ import annotations

from pathlib import Path

from hallucination_replay.hallucination import (
    HallucinationSeverity,
    detect_contradictions,
    detect_unsupported_claims,
    extract_claims_from_outputs,
    extract_evidence,
    generate_hallucination_json_report,
    generate_hallucination_markdown_report,
    match_claims_to_evidence,
    rank_hallucination_severity,
    score_evidence_coverage,
    score_hallucinations,
)
from hallucination_replay.models import RunTrace
from hallucination_replay.replay import ReplayTraceLoader

BENCHMARK_PATH = Path("benchmarks/hallucination/contradiction.json")
EXPECTED_SUPPORT_SCORE = 0.6667
EXPECTED_SCORE = 0.4


def test_hallucination_detection_end_to_end_from_benchmark_trace() -> None:
    trace = RunTrace.from_json(BENCHMARK_PATH.read_text())
    loaded_trace = ReplayTraceLoader().load_from_object(trace)

    claims = extract_claims_from_outputs(_outputs(loaded_trace))
    evidence = extract_evidence(loaded_trace, step_index=claims[0].source_step)
    matches = match_claims_to_evidence(claims, evidence)
    unsupported = detect_unsupported_claims(matches)
    contradictions = detect_contradictions(claims, evidence)
    coverage = score_evidence_coverage(matches)
    score = score_hallucinations(unsupported, contradictions, coverage)
    severity = rank_hallucination_severity(score)
    markdown = generate_hallucination_markdown_report(
        claims,
        evidence,
        matches,
        contradictions,
        score,
        severity,
    )
    json_report = generate_hallucination_json_report(
        claims,
        evidence,
        matches,
        contradictions,
        score,
        severity,
    )

    assert loaded_trace.run_id == "hallucination-contradiction"
    assert len(claims) == 1
    assert len(evidence) == 1
    assert matches[0].support_score == EXPECTED_SUPPORT_SCORE
    assert unsupported == []
    assert len(contradictions) == 1
    assert score.score == EXPECTED_SCORE
    assert severity is HallucinationSeverity.MEDIUM
    assert "## Contradictions" in markdown
    assert '"severity": "medium"' in json_report


def _outputs(trace: RunTrace) -> list[dict[str, object]]:
    outputs = trace.metadata.get("outputs", [])
    return (
        [output for output in outputs if isinstance(output, dict)]
        if isinstance(outputs, list)
        else []
    )
