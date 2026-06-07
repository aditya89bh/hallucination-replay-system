"""Prompt reconstruction for replay traces."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context


class PromptState(TraceModel):
    """Prompt state available at a replay step."""

    step_index: int = Field(ge=0)
    system_prompt: str | None = None
    user_prompt: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)


class ReconstructedPrompt(TraceModel):
    """Historical prompt reconstruction at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    current_prompt: PromptState | None = None
    prompt_history: list[PromptState] = Field(default_factory=list)
    context_keys: list[str] = Field(default_factory=list)


def reconstruct_prompt(trace: RunTrace, step_index: int) -> ReconstructedPrompt:
    """Reconstruct prompt state and prompt inputs at a replay step."""
    context = reconstruct_context(trace, step_index)
    prompt_history = _prompt_history(trace, step_index)
    current_prompt = prompt_history[-1] if prompt_history else None
    return ReconstructedPrompt(
        trace_id=trace.run_id,
        step_index=step_index,
        current_prompt=current_prompt,
        prompt_history=prompt_history,
        context_keys=[entry.key for entry in context.entries],
    )


def _prompt_history(trace: RunTrace, step_index: int) -> list[PromptState]:
    raw_prompts = trace.metadata.get("prompts", [])
    if not isinstance(raw_prompts, list):
        message = "RunTrace metadata field 'prompts' must be a list"
        raise ReplayError(message)
    prompts = [PromptState.model_validate(prompt) for prompt in raw_prompts]
    available_prompts = [
        prompt for prompt in prompts if prompt.step_index <= step_index
    ]
    return sorted(available_prompts, key=lambda prompt: prompt.step_index)
