"""Full-state reconstruction for replay traces."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import (
    ReconstructedContext,
    reconstruct_context,
)
from hallucination_replay.reconstruction.memory import (
    ReconstructedMemory,
    reconstruct_memory,
)
from hallucination_replay.reconstruction.prompt import (
    ReconstructedPrompt,
    reconstruct_prompt,
)
from hallucination_replay.reconstruction.reasoning import (
    ReconstructedReasoning,
    reconstruct_reasoning,
)
from hallucination_replay.reconstruction.retrieval import (
    ReconstructedRetrieval,
    reconstruct_retrieval,
)
from hallucination_replay.reconstruction.tools import (
    ReconstructedTools,
    reconstruct_tools,
)
from hallucination_replay.reconstruction.validation import (
    ReconstructedValidation,
    reconstruct_validation,
)


class ReconstructedState(TraceModel):
    """Complete reconstructed state available at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    context: ReconstructedContext
    prompt: ReconstructedPrompt
    memory: ReconstructedMemory
    retrieval: ReconstructedRetrieval
    tools: ReconstructedTools
    validation: ReconstructedValidation
    reasoning: ReconstructedReasoning


def reconstruct_state(trace: RunTrace, step_index: int) -> ReconstructedState:
    """Reconstruct complete agent state at a replay step."""
    return ReconstructedState(
        trace_id=trace.run_id,
        step_index=step_index,
        context=reconstruct_context(trace, step_index),
        prompt=reconstruct_prompt(trace, step_index),
        memory=reconstruct_memory(trace, step_index),
        retrieval=reconstruct_retrieval(trace, step_index),
        tools=reconstruct_tools(trace, step_index),
        validation=reconstruct_validation(trace, step_index),
        reasoning=reconstruct_reasoning(trace, step_index),
    )
