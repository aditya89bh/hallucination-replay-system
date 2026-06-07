"""Execution comparison API endpoints."""

from __future__ import annotations

import json
from typing import cast
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel

from hallucination_replay.api.traces import get_trace_repository
from hallucination_replay.diffing import (
    compare_executions,
    generate_comparison_json_report,
    generate_comparison_markdown_report,
)
from hallucination_replay.models import RunTrace

router = APIRouter(prefix="/compare", tags=["comparison"])


class ComparisonRequest(BaseModel):
    """Request for deterministic execution comparison."""

    run_a_id: str
    run_b_id: str
    report_id: str | None = None


class ComparisonResponse(BaseModel):
    """Structured execution comparison response."""

    report_id: str
    run_a_id: str
    run_b_id: str
    comparison: dict[str, object]
    markdown_report: str
    json_report: dict[str, object]


@router.post("", response_model=ComparisonResponse)
def compare_traces(
    request_body: ComparisonRequest, request: Request
) -> ComparisonResponse:
    """Compare two stored traces across deterministic diff dimensions."""
    run_a = _load_trace(request_body.run_a_id, request)
    run_b = _load_trace(request_body.run_b_id, request)
    comparison = compare_executions(run_a, run_b)
    report_id = request_body.report_id or str(uuid4())
    response = ComparisonResponse(
        report_id=report_id,
        run_a_id=run_a.run_id,
        run_b_id=run_b.run_id,
        comparison=comparison.to_dict(),
        markdown_report=generate_comparison_markdown_report(comparison),
        json_report=cast(
            dict[str, object], json.loads(generate_comparison_json_report(comparison))
        ),
    )
    _reports(request)[report_id] = response
    return response


@router.get("/report", response_model=ComparisonResponse)
def get_comparison_report(
    request: Request, report_id: str = Query(min_length=1)
) -> ComparisonResponse:
    """Return a previously generated execution comparison report."""
    report = _reports(request).get(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison report '{report_id}' was not found",
        )
    return report


def _reports(request: Request) -> dict[str, ComparisonResponse]:
    reports = getattr(request.app.state, "comparison_reports", None)
    if reports is None:
        reports = {}
        request.app.state.comparison_reports = reports
    return cast(dict[str, ComparisonResponse], reports)


def _load_trace(run_id: str, request: Request) -> RunTrace:
    repository = get_trace_repository(request)
    if not repository.exists(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{run_id}' was not found",
        )
    return repository.load_trace(run_id)
