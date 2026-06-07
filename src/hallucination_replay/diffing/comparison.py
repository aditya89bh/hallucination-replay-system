"""Aggregate execution comparison results."""

from __future__ import annotations

from hallucination_replay.diffing.context import (
    ContextDiff,
    ContextSnapshot,
    diff_context_state,
)
from hallucination_replay.diffing.memory import MemoryDiff, diff_memory_state
from hallucination_replay.diffing.reasoning import ReasoningDiff, diff_reasoning_state
from hallucination_replay.diffing.retrieval import RetrievalDiff, diff_retrieval_state
from hallucination_replay.diffing.states import StateDiff, diff_reconstructed_states
from hallucination_replay.diffing.timeline import TimelineDiff, diff_timelines
from hallucination_replay.diffing.tools import ToolDiff, diff_tool_state
from hallucination_replay.diffing.traces import TraceDiff, diff_traces
from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import (
    reconstruct_context,
    reconstruct_conversation,
    reconstruct_memory,
    reconstruct_prompt,
    reconstruct_reasoning,
    reconstruct_retrieval,
    reconstruct_state,
    reconstruct_tools,
)
from hallucination_replay.replay import ReplayTraceLoader


class ExecutionComparison(TraceModel):
    """Single aggregate comparison result for two executions."""

    trace_diff: TraceDiff
    state_diff: StateDiff
    context_diff: ContextDiff
    retrieval_diff: RetrievalDiff
    memory_diff: MemoryDiff
    tool_diff: ToolDiff
    reasoning_diff: ReasoningDiff
    timeline_diff: TimelineDiff


def compare_executions(run_a: RunTrace, run_b: RunTrace) -> ExecutionComparison:
    """Compare two executions across all deterministic diff dimensions."""
    step_a = _last_step_index(run_a)
    step_b = _last_step_index(run_b)
    state_a = reconstruct_state(run_a, step_a)
    state_b = reconstruct_state(run_b, step_b)
    return ExecutionComparison(
        trace_diff=diff_traces(run_a, run_b),
        state_diff=diff_reconstructed_states(state_a, state_b),
        context_diff=diff_context_state(
            ContextSnapshot(
                context=reconstruct_context(run_a, step_a),
                prompt=reconstruct_prompt(run_a, step_a),
                conversation=reconstruct_conversation(run_a, step_a),
            ),
            ContextSnapshot(
                context=reconstruct_context(run_b, step_b),
                prompt=reconstruct_prompt(run_b, step_b),
                conversation=reconstruct_conversation(run_b, step_b),
            ),
        ),
        retrieval_diff=diff_retrieval_state(
            reconstruct_retrieval(run_a, step_a), reconstruct_retrieval(run_b, step_b)
        ),
        memory_diff=diff_memory_state(
            reconstruct_memory(run_a, step_a), reconstruct_memory(run_b, step_b)
        ),
        tool_diff=diff_tool_state(
            reconstruct_tools(run_a, step_a), reconstruct_tools(run_b, step_b)
        ),
        reasoning_diff=diff_reasoning_state(
            reconstruct_reasoning(run_a, step_a), reconstruct_reasoning(run_b, step_b)
        ),
        timeline_diff=diff_timelines(run_a, run_b),
    )


def _last_step_index(trace: RunTrace) -> int:
    steps = ReplayTraceLoader().get_steps(trace)
    if not steps:
        return 0
    return max(step.step_index for step in steps)
