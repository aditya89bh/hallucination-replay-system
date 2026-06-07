"""State diffing for reconstructed execution states."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import ReconstructedState


class StateValueChange(TraceModel):
    """A deterministic value change at a state path."""

    path: str
    run_a: object | None = None
    run_b: object | None = None


class StateDiff(TraceModel):
    """Additions, removals, and modifications between reconstructed states."""

    run_a_id: str
    run_b_id: str
    additions: list[StateValueChange] = Field(default_factory=list)
    removals: list[StateValueChange] = Field(default_factory=list)
    modifications: list[StateValueChange] = Field(default_factory=list)


def diff_reconstructed_states(
    state_a: ReconstructedState, state_b: ReconstructedState
) -> StateDiff:
    """Compare reconstructed states with deterministic path ordering."""
    flat_a = _flatten(state_a.to_dict())
    flat_b = _flatten(state_b.to_dict())
    additions: list[StateValueChange] = []
    removals: list[StateValueChange] = []
    modifications: list[StateValueChange] = []
    for path in sorted(set(flat_a) | set(flat_b)):
        in_a = path in flat_a
        in_b = path in flat_b
        if not in_a and in_b:
            additions.append(StateValueChange(path=path, run_b=flat_b[path]))
        elif in_a and not in_b:
            removals.append(StateValueChange(path=path, run_a=flat_a[path]))
        elif flat_a[path] != flat_b[path]:
            modifications.append(
                StateValueChange(path=path, run_a=flat_a[path], run_b=flat_b[path])
            )
    return StateDiff(
        run_a_id=state_a.trace_id,
        run_b_id=state_b.trace_id,
        additions=additions,
        removals=removals,
        modifications=modifications,
    )


def _flatten(value: object, prefix: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        flattened: dict[str, object] = {}
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(_flatten(value[key], path))
        return flattened
    if isinstance(value, list):
        flattened = {}
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]"
            flattened.update(_flatten(item, path))
        return flattened
    return {prefix: value}
