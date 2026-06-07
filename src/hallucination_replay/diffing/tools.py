"""Tool diffing for execution comparisons."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import ReconstructedTools


class ToolDiff(TraceModel):
    """Diff between reconstructed tool execution states."""

    calls_added: list[str] = Field(default_factory=list)
    calls_removed: list[str] = Field(default_factory=list)
    results_added: list[str] = Field(default_factory=list)
    results_removed: list[str] = Field(default_factory=list)
    failures_added: list[str] = Field(default_factory=list)
    outcome_changes: list[str] = Field(default_factory=list)


def diff_tool_state(
    tools_a: ReconstructedTools, tools_b: ReconstructedTools
) -> ToolDiff:
    """Compare tool calls, results, failures, and execution outcomes."""
    calls_a = {call.step_id: call.tool_name for call in tools_a.calls}
    calls_b = {call.step_id: call.tool_name for call in tools_b.calls}
    results_a = {result.step_id: result for result in tools_a.results}
    results_b = {result.step_id: result for result in tools_b.results}
    return ToolDiff(
        calls_added=sorted(
            _format_step(step_id, calls_b) for step_id in set(calls_b) - set(calls_a)
        ),
        calls_removed=sorted(
            _format_step(step_id, calls_a) for step_id in set(calls_a) - set(calls_b)
        ),
        results_added=sorted(set(results_b) - set(results_a)),
        results_removed=sorted(set(results_a) - set(results_b)),
        failures_added=sorted(
            result.step_id for result in tools_b.results if not result.success
        ),
        outcome_changes=sorted(
            step_id
            for step_id in set(results_a) & set(results_b)
            if results_a[step_id].success != results_b[step_id].success
        ),
    )


def _format_step(step_id: str, calls: dict[str, str]) -> str:
    return f"{step_id}:{calls[step_id]}"
