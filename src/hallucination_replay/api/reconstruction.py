"""Reconstruction API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from hallucination_replay.api.traces import get_trace_repository
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import (
    reconstruct_context,
    reconstruct_memory,
    reconstruct_state,
)

router = APIRouter(prefix="/reconstruction", tags=["reconstruction"])


class ReconstructionRequest(BaseModel):
    """Request for reconstructing trace state at a step."""

    run_id: str
    step_index: int = Field(ge=0)


@router.post("/context")
def reconstruct_context_endpoint(
    request_body: ReconstructionRequest, request: Request
) -> dict[str, object]:
    """Reconstruct context state for a stored trace."""
    trace = _load_trace(request_body.run_id, request)
    return reconstruct_context(trace, request_body.step_index).to_dict()


@router.post("/memory")
def reconstruct_memory_endpoint(
    request_body: ReconstructionRequest, request: Request
) -> dict[str, object]:
    """Reconstruct memory state for a stored trace."""
    trace = _load_trace(request_body.run_id, request)
    return reconstruct_memory(trace, request_body.step_index).to_dict()


@router.post("/state")
def reconstruct_state_endpoint(
    request_body: ReconstructionRequest, request: Request
) -> dict[str, object]:
    """Reconstruct full state for a stored trace."""
    trace = _load_trace(request_body.run_id, request)
    return reconstruct_state(trace, request_body.step_index).to_dict()


def _load_trace(run_id: str, request: Request) -> RunTrace:
    repository = get_trace_repository(request)
    if not repository.exists(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{run_id}' was not found",
        )
    return repository.load_trace(run_id)
