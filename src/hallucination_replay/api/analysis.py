"""Failure analysis API endpoints."""

from __future__ import annotations

import json
from typing import cast
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from hallucination_replay.analysis import (
    analyze_intent_failures,
    analyze_memory_failures,
    analyze_output_failures,
    analyze_reasoning_failures,
    analyze_retrieval_failures,
    analyze_tool_failures,
    analyze_validation_failures,
    generate_failure_json_report,
    generate_failure_markdown_report,
    rank_root_causes,
    score_findings,
)
from hallucination_replay.analysis.taxonomy import FailureFinding
from hallucination_replay.api.traces import get_trace_repository
from hallucination_replay.models import RunTrace

router = APIRouter(prefix="/analysis", tags=["analysis"])


class FailureAnalysisRequest(BaseModel):
    """Request for deterministic failure analysis."""

    run_id: str
    step_index: int = Field(ge=0)
    report_id: str | None = None


class FailureAnalysisResponse(BaseModel):
    """Structured failure analysis response."""

    report_id: str
    run_id: str
    step_index: int
    findings: list[dict[str, object]]
    root_causes: list[dict[str, object]]
    confidence: list[dict[str, object]]
    markdown_report: str
    json_report: dict[str, object]


@router.post("/run", response_model=FailureAnalysisResponse)
def run_failure_analysis(
    request_body: FailureAnalysisRequest, request: Request
) -> FailureAnalysisResponse:
    """Run all deterministic failure analyzers for a stored trace."""
    trace = _load_trace(request_body.run_id, request)
    findings = _analyze(trace, request_body.step_index)
    report_id = request_body.report_id or str(uuid4())
    response = _response(report_id, trace.run_id, request_body.step_index, findings)
    _reports(request)[report_id] = response
    return response


@router.get("/report", response_model=FailureAnalysisResponse)
def get_failure_analysis_report(
    request: Request, report_id: str = Query(min_length=1)
) -> FailureAnalysisResponse:
    """Return a previously generated failure analysis report."""
    report = _reports(request).get(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{report_id}' was not found",
        )
    return report


def _analyze(trace: RunTrace, step_index: int) -> list[FailureFinding]:
    return [
        *analyze_intent_failures(trace, step_index),
        *analyze_retrieval_failures(trace, step_index),
        *analyze_memory_failures(trace, step_index),
        *analyze_tool_failures(trace, step_index),
        *analyze_validation_failures(trace, step_index),
        *analyze_reasoning_failures(trace, step_index),
        *analyze_output_failures(trace, step_index),
    ]


def _response(
    report_id: str, run_id: str, step_index: int, findings: list[FailureFinding]
) -> FailureAnalysisResponse:
    return FailureAnalysisResponse(
        report_id=report_id,
        run_id=run_id,
        step_index=step_index,
        findings=[finding.to_dict() for finding in findings],
        root_causes=[item.to_dict() for item in rank_root_causes(findings)],
        confidence=[item.to_dict() for item in score_findings(findings)],
        markdown_report=generate_failure_markdown_report(findings),
        json_report=cast(
            dict[str, object], json.loads(generate_failure_json_report(findings))
        ),
    )


def _reports(request: Request) -> dict[str, FailureAnalysisResponse]:
    reports = getattr(request.app.state, "failure_analysis_reports", None)
    if reports is None:
        reports = {}
        request.app.state.failure_analysis_reports = reports
    return cast(dict[str, FailureAnalysisResponse], reports)


def _load_trace(run_id: str, request: Request) -> RunTrace:
    repository = get_trace_repository(request)
    if not repository.exists(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{run_id}' was not found",
        )
    return repository.load_trace(run_id)
