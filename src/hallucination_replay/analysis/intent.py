"""Intent failure analysis."""

from __future__ import annotations

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import (
    reconstruct_conversation,
    reconstruct_prompt,
)


def analyze_intent_failures(trace: RunTrace, step_index: int) -> list[FailureFinding]:
    """Detect missing, conflicting, and incomplete intent capture."""
    prompt = reconstruct_prompt(trace, step_index)
    conversation = reconstruct_conversation(trace, step_index)
    findings: list[FailureFinding] = []

    user_objectives = _user_objectives(trace, step_index)
    if prompt.current_prompt is not None and prompt.current_prompt.user_prompt:
        user_objectives.append(prompt.current_prompt.user_prompt)
    user_objectives.extend(
        message.content for message in conversation.messages if message.role == "user"
    )

    if not [objective for objective in user_objectives if objective.strip()]:
        findings.append(
            FailureFinding(
                failure_type=FailureType.INTENT_FAILURE,
                message="Missing user objective",
                severity=5,
                confidence=0.9,
                evidence=["No user prompt or user conversation message available"],
                step_index=step_index,
                metadata={"reason": "missing_user_objective"},
            )
        )

    conflicts = _intent_list(trace, step_index, "conflicts")
    if conflicts:
        findings.append(
            FailureFinding(
                failure_type=FailureType.INTENT_FAILURE,
                message="Conflicting objectives captured",
                severity=4,
                confidence=0.85,
                evidence=conflicts,
                step_index=step_index,
                metadata={"reason": "conflicting_objectives"},
            )
        )

    incomplete = _intent_list(trace, step_index, "incomplete")
    if incomplete:
        findings.append(
            FailureFinding(
                failure_type=FailureType.INTENT_FAILURE,
                message="Incomplete intent capture",
                severity=3,
                confidence=0.8,
                evidence=incomplete,
                step_index=step_index,
                metadata={"reason": "incomplete_intent_capture"},
            )
        )

    return findings


def _user_objectives(trace: RunTrace, step_index: int) -> list[str]:
    objectives = _intent_list(trace, step_index, "objectives")
    captured = _intent_list(trace, step_index, "captured_objectives")
    return objectives + captured


def _intent_list(trace: RunTrace, step_index: int, key: str) -> list[str]:
    raw_intent = trace.metadata.get("intent", {})
    if not isinstance(raw_intent, dict):
        return []
    raw_items = raw_intent.get(key, [])
    if not isinstance(raw_items, list):
        return []
    items: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            item_step = item.get("step_index", 0)
            value = item.get("value", item.get("description", ""))
            if (
                isinstance(item_step, int)
                and item_step <= step_index
                and isinstance(value, str)
            ):
                items.append(value)
        elif isinstance(item, str):
            items.append(item)
    return sorted(item for item in items if item.strip())
