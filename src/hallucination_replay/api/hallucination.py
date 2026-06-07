"""Hallucination analysis API endpoints."""

from __future__ import annotations

import json
from typing import cast
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from hallucination_replay.api.traces import get_trace_repository
from hallucination_replay.hallucination import (
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

router = APIRouter(prefix="/hallucination", tags=["hallucination"])


class HallucinationRunRequest(BaseModel):
    """Request for deterministic hallucination analysis."""

    run_id: str
    step_index: int = Field(ge=0)
    report_id: str | None = None


class HallucinationRunResponse(BaseModel):
    """Structured hallucination analysis response."""

    report_id: str
    run_id: str
    step_index: int
    claims: list[dict[str, object]]
    evidence: list[dict[str, object]]
    support_scores: list[dict[str, object]]
    unsupported_claims: list[dict[str, object]]
    contradictions: list[dict[str, object]]
    score: dict[str, object]
    severity: str
    markdown_report: str
    json_report: dict[str, object]


@router.post("/run", response_model=HallucinationRunResponse)
def run_hallucination_analysis(
    request_body: HallucinationRunRequest, request: Request
) -> HallucinationRunResponse:
    """Run deterministic hallucination detection for a stored trace."""
    trace = _load_trace(request_body.run_id, request)
    claims = extract_claims_from_outputs(_outputs(trace))
    evidence = extract_evidence(trace, request_body.step_index)
    matches = match_claims_to_evidence(claims, evidence)
    unsupported = detect_unsupported_claims(matches)
    contradictions = detect_contradictions(claims, evidence)
    coverage = score_evidence_coverage(matches)
    score = score_hallucinations(unsupported, contradictions, coverage)
    severity = rank_hallucination_severity(score)
    report_id = request_body.report_id or str(uuid4())
    response = HallucinationRunResponse(
        report_id=report_id,
        run_id=trace.run_id,
        step_index=request_body.step_index,
        claims=[claim.to_dict() for claim in claims],
        evidence=[item.to_dict() for item in evidence],
        support_scores=[match.to_dict() for match in matches],
        unsupported_claims=[finding.to_dict() for finding in unsupported],
        contradictions=[finding.to_dict() for finding in contradictions],
        score=score.to_dict(),
        severity=severity.value,
        markdown_report=generate_hallucination_markdown_report(
            claims, evidence, matches, contradictions, score, severity
        ),
        json_report=cast(
            dict[str, object],
            json.loads(
                generate_hallucination_json_report(
                    claims, evidence, matches, contradictions, score, severity
                )
            ),
        ),
    )
    _reports(request)[report_id] = response
    return response


@router.get("/report", response_model=HallucinationRunResponse)
def get_hallucination_report(
    request: Request, report_id: str = Query(min_length=1)
) -> HallucinationRunResponse:
    """Return a previously generated hallucination report."""
    report = _reports(request).get(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hallucination report '{report_id}' was not found",
        )
    return report


def _outputs(trace: RunTrace) -> list[dict[str, object]]:
    outputs = trace.metadata.get("outputs", [])
    return (
        [output for output in outputs if isinstance(output, dict)]
        if isinstance(outputs, list)
        else []
    )


def _reports(request: Request) -> dict[str, HallucinationRunResponse]:
    reports = getattr(request.app.state, "hallucination_reports", None)
    if reports is None:
        reports = {}
        request.app.state.hallucination_reports = reports
    return cast(dict[str, HallucinationRunResponse], reports)


def _load_trace(run_id: str, request: Request) -> RunTrace:
    repository = get_trace_repository(request)
    if not repository.exists(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{run_id}' was not found",
        )
    return repository.load_trace(run_id)
