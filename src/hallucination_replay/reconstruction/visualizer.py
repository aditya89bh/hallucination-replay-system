"""Human-readable reconstruction visualizer."""

from __future__ import annotations

from hallucination_replay.reconstruction.state import ReconstructedState


def visualize_state(state: ReconstructedState) -> str:
    """Render a deterministic human-readable state summary."""
    lines = [
        f"Reconstructed State: {state.trace_id} @ step {state.step_index}",
        f"Current step: {state.context.current_step.step_id}",
        f"Context entries: {len(state.context.entries)}",
        f"Prompt history: {len(state.prompt.prompt_history)}",
        f"Memory keys: {', '.join(sorted(state.memory.state)) or 'none'}",
        f"Retrieval documents: {len(state.retrieval.retrieved_documents)}",
        f"Tool calls: {len(state.tools.calls)}",
        f"Validation checks: {len(state.validation.records)}",
        f"Reasoning summaries: {len(state.reasoning.summaries)}",
    ]
    return "\n".join(lines)
