"""Retrieval failure analysis."""

from __future__ import annotations

from typing import Any

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_retrieval


def analyze_retrieval_failures(
    trace: RunTrace, step_index: int
) -> list[FailureFinding]:
    """Detect retrieval absence, empty results, and coverage gaps."""
    retrieval = reconstruct_retrieval(trace, step_index)
    findings: list[FailureFinding] = []

    if not retrieval.events:
        findings.append(
            FailureFinding(
                failure_type=FailureType.RETRIEVAL_FAILURE,
                message="No retrieval events executed",
                severity=4,
                confidence=0.9,
                evidence=["No retrieval records were available at this step"],
                step_index=step_index,
                metadata={"reason": "no_retrieval_events"},
            )
        )
        return findings

    empty_queries = [
        record.event.query
        for record in retrieval.events
        if not record.event.retrieved_documents
    ]
    if empty_queries:
        findings.append(
            FailureFinding(
                failure_type=FailureType.RETRIEVAL_FAILURE,
                message="Empty retrieval results",
                severity=3,
                confidence=0.85,
                evidence=[
                    f"Query returned no documents: {query}" for query in empty_queries
                ],
                step_index=step_index,
                metadata={"reason": "empty_retrieval_results"},
            )
        )

    missing_requirements = _missing_requirements(
        retrieval.retrieved_documents,
        _required_retrieval_coverage(trace, step_index),
    )
    if missing_requirements:
        findings.append(
            FailureFinding(
                failure_type=FailureType.RETRIEVAL_FAILURE,
                message="Retrieval coverage gaps",
                severity=3,
                confidence=0.8,
                evidence=[
                    f"Missing required coverage: {item}"
                    for item in missing_requirements
                ],
                step_index=step_index,
                metadata={"reason": "retrieval_coverage_gaps"},
            )
        )

    return findings


def _required_retrieval_coverage(trace: RunTrace, step_index: int) -> list[str]:
    raw_requirements = trace.metadata.get("retrieval_requirements", [])
    if not isinstance(raw_requirements, list):
        return []
    requirements: list[str] = []
    for item in raw_requirements:
        if isinstance(item, dict):
            item_step = item.get("step_index", 0)
            value = item.get("value", item.get("query", item.get("document", "")))
            if (
                isinstance(item_step, int)
                and item_step <= step_index
                and isinstance(value, str)
            ):
                requirements.append(value)
        elif isinstance(item, str):
            requirements.append(item)
    return sorted(requirement for requirement in requirements if requirement.strip())


def _missing_requirements(
    documents: list[dict[str, Any]], requirements: list[str]
) -> list[str]:
    searchable_documents = "\n".join(
        " ".join(str(value) for value in document.values()) for document in documents
    ).lower()
    return [
        requirement
        for requirement in requirements
        if requirement.lower() not in searchable_documents
    ]
