"""Replay trace loading and validation."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.storage import TraceRepository


class ReplayTraceLoader:
    """Load and validate traces for deterministic replay."""

    def __init__(self, repository: TraceRepository | None = None) -> None:
        """Create a loader with an optional trace repository."""
        self._repository = repository

    def load_from_repository(self, run_id: str) -> RunTrace:
        """Load a trace by run identifier from the configured repository."""
        if self._repository is None:
            message = "ReplayTraceLoader requires a repository for repository loads"
            raise ReplayError(message)
        trace = self._repository.load_trace(run_id)
        self.validate_trace(trace)
        return trace

    def load_from_object(self, trace: RunTrace) -> RunTrace:
        """Load a trace directly from an existing RunTrace object."""
        self.validate_trace(trace)
        return trace

    def get_steps(self, trace: RunTrace) -> list[AgentStep]:
        """Return replayable steps stored in trace metadata."""
        raw_steps = trace.metadata.get("steps", [])
        if not isinstance(raw_steps, list):
            message = "RunTrace metadata field 'steps' must be a list"
            raise ReplayError(message)
        try:
            steps = [AgentStep.model_validate(step) for step in raw_steps]
        except ValidationError as exc:
            message = "RunTrace contains invalid replay steps"
            raise ReplayError(message) from exc
        return sorted(steps, key=lambda step: step.step_index)

    def validate_trace(self, trace: RunTrace) -> None:
        """Validate that a trace can be used for replay."""
        if not trace.run_id:
            message = "RunTrace must include a run_id"
            raise ReplayError(message)
        self._validate_step_order(self.get_steps(trace))

    @staticmethod
    def _validate_step_order(steps: list[AgentStep]) -> None:
        seen_step_ids: set[str] = set()
        seen_indexes: set[int] = set()
        for step in steps:
            if step.step_id in seen_step_ids:
                message = f"Duplicate replay step_id: {step.step_id}"
                raise ReplayError(message)
            if step.step_index in seen_indexes:
                message = f"Duplicate replay step_index: {step.step_index}"
                raise ReplayError(message)
            seen_step_ids.add(step.step_id)
            seen_indexes.add(step.step_index)


def steps_to_metadata(steps: list[AgentStep]) -> dict[str, Any]:
    """Serialize steps into RunTrace metadata format for tests and fixtures."""
    return {"steps": [step.to_dict() for step in steps]}
