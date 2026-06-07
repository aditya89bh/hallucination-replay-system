"""Replay API endpoints."""

from __future__ import annotations

from typing import cast
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from hallucination_replay.api.traces import get_trace_repository
from hallucination_replay.replay import ReplayController

router = APIRouter(prefix="/replay", tags=["replay"])


class ReplayLoadRequest(BaseModel):
    """Request to load a trace into a replay session."""

    run_id: str
    session_id: str | None = None


class ReplaySessionRequest(BaseModel):
    """Request targeting an existing replay session."""

    session_id: str


class ReplayJumpRequest(ReplaySessionRequest):
    """Request to jump to a replay step by index or identifier."""

    step_id: str | None = None
    step_index: int | None = Field(default=None, ge=0)


class ReplayStateResponse(BaseModel):
    """Replay session state response."""

    session_id: str
    run_id: str
    current_position: int
    step_count: int
    current_step: dict[str, object] | None = None


@router.post("/load", response_model=ReplayStateResponse)
def load_replay(
    request_body: ReplayLoadRequest, request: Request
) -> ReplayStateResponse:
    """Load a stored trace into a replay controller."""
    repository = get_trace_repository(request)
    if not repository.exists(request_body.run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{request_body.run_id}' was not found",
        )
    session_id = request_body.session_id or str(uuid4())
    controller = ReplayController.create(
        repository.load_trace(request_body.run_id), session_id
    )
    _controllers(request)[session_id] = controller
    return _response(controller)


@router.post("/next", response_model=ReplayStateResponse)
def replay_next(
    request_body: ReplaySessionRequest, request: Request
) -> ReplayStateResponse:
    """Move replay forward one step."""
    controller = _controller(request, request_body.session_id)
    controller.move_forward()
    return _response(controller)


@router.post("/previous", response_model=ReplayStateResponse)
def replay_previous(
    request_body: ReplaySessionRequest, request: Request
) -> ReplayStateResponse:
    """Move replay backward one step."""
    controller = _controller(request, request_body.session_id)
    controller.move_backward()
    return _response(controller)


@router.post("/jump", response_model=ReplayStateResponse)
def replay_jump(
    request_body: ReplayJumpRequest, request: Request
) -> ReplayStateResponse:
    """Jump replay to a step index or step identifier."""
    controller = _controller(request, request_body.session_id)
    if request_body.step_id is not None:
        controller.jump_to_step(request_body.step_id)
    elif request_body.step_index is not None:
        controller.jump_to_index(request_body.step_index)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either step_id or step_index is required",
        )
    return _response(controller)


def _controllers(request: Request) -> dict[str, ReplayController]:
    controllers = getattr(request.app.state, "replay_controllers", None)
    if controllers is None:
        controllers = {}
        request.app.state.replay_controllers = controllers
    return cast(dict[str, ReplayController], controllers)


def _controller(request: Request, session_id: str) -> ReplayController:
    controller = _controllers(request).get(session_id)
    if controller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Replay session '{session_id}' was not found",
        )
    return controller


def _response(controller: ReplayController) -> ReplayStateResponse:
    current_step = controller.current_step()
    return ReplayStateResponse(
        session_id=controller.session.session_id,
        run_id=controller.trace.run_id,
        current_position=controller.session.current_position,
        step_count=controller.step_count,
        current_step=current_step.to_dict() if current_step is not None else None,
    )
