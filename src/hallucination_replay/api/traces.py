"""Trace storage API endpoints."""

from __future__ import annotations

from pathlib import Path
from tempfile import gettempdir
from typing import cast

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from hallucination_replay.models import RunTrace
from hallucination_replay.storage import FilesystemTraceRepository, TraceRepository

router = APIRouter(prefix="/traces", tags=["traces"])


class TraceListResponse(BaseModel):
    """Stored trace identifiers."""

    run_ids: list[str] = Field(default_factory=list)


class TraceCreateResponse(BaseModel):
    """Trace creation response."""

    run_id: str


def default_trace_repository() -> TraceRepository:
    """Create the default filesystem trace repository."""
    return FilesystemTraceRepository(Path(gettempdir()) / "hallucination-replay-traces")


@router.get("", response_model=TraceListResponse)
def list_traces(request: Request) -> TraceListResponse:
    """List stored trace identifiers."""
    repository = get_trace_repository(request)
    return TraceListResponse(run_ids=repository.list_traces())


@router.get("/{run_id}", response_model=RunTrace)
def get_trace(run_id: str, request: Request) -> RunTrace:
    """Return a stored trace by run identifier."""
    repository = get_trace_repository(request)
    if not repository.exists(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{run_id}' was not found",
        )
    return repository.load_trace(run_id)


@router.post(
    "", response_model=TraceCreateResponse, status_code=status.HTTP_201_CREATED
)
def create_trace(trace: RunTrace, request: Request) -> TraceCreateResponse:
    """Persist a run trace."""
    repository = get_trace_repository(request)
    repository.save_trace(trace)
    return TraceCreateResponse(run_id=trace.run_id)


def get_trace_repository(request: Request) -> TraceRepository:
    """Read the configured trace repository from app state."""
    repository = getattr(request.app.state, "trace_repository", None)
    if repository is None:
        repository = default_trace_repository()
        request.app.state.trace_repository = repository
    return cast(TraceRepository, repository)
