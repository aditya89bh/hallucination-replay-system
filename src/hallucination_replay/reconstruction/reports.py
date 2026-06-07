"""Reconstruction report generation."""

from __future__ import annotations

import json

from hallucination_replay.reconstruction.state import ReconstructedState
from hallucination_replay.reconstruction.visualizer import visualize_state


def generate_markdown_report(state: ReconstructedState) -> str:
    """Generate a deterministic markdown reconstruction report."""
    return "\n".join(
        [
            f"# Reconstruction Report: {state.trace_id}",
            "",
            f"- Step index: {state.step_index}",
            f"- Current step: {state.context.current_step.step_id}",
            f"- Context entries: {len(state.context.entries)}",
            f"- Memory keys: {', '.join(sorted(state.memory.state)) or 'none'}",
            f"- Tool calls: {len(state.tools.calls)}",
            "",
            "## Summary",
            visualize_state(state),
        ]
    )


def generate_json_report(state: ReconstructedState) -> str:
    """Generate a deterministic JSON reconstruction report."""
    return json.dumps(state.to_dict(), sort_keys=True)


def generate_state_summary_report(state: ReconstructedState) -> dict[str, object]:
    """Generate a compact state summary report."""
    return {
        "trace_id": state.trace_id,
        "step_index": state.step_index,
        "current_step_id": state.context.current_step.step_id,
        "context_entry_count": len(state.context.entries),
        "memory_key_count": len(state.memory.state),
        "retrieval_document_count": len(state.retrieval.retrieved_documents),
        "tool_call_count": len(state.tools.calls),
        "validation_count": len(state.validation.records),
        "reasoning_summary_count": len(state.reasoning.summaries),
    }
