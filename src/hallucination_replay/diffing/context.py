"""Context, prompt, and conversation diffing."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction import (
    ReconstructedContext,
    ReconstructedConversation,
    ReconstructedPrompt,
)


class ContextSnapshot(TraceModel):
    """Reconstructed context surfaces for one run."""

    context: ReconstructedContext
    prompt: ReconstructedPrompt
    conversation: ReconstructedConversation


class ContextDiff(TraceModel):
    """Diff for reconstructed context, prompt, and conversation state."""

    context_added: list[str] = Field(default_factory=list)
    context_removed: list[str] = Field(default_factory=list)
    context_modified: list[str] = Field(default_factory=list)
    prompt_changed: bool
    conversation_added: list[str] = Field(default_factory=list)
    conversation_removed: list[str] = Field(default_factory=list)


def diff_context_state(
    snapshot_a: ContextSnapshot, snapshot_b: ContextSnapshot
) -> ContextDiff:
    """Compare context values, prompt state, and conversation state."""
    values_a = {entry.key: entry.value for entry in snapshot_a.context.entries}
    values_b = {entry.key: entry.value for entry in snapshot_b.context.entries}
    messages_a = {
        _message_key(message.to_dict()) for message in snapshot_a.conversation.messages
    }
    messages_b = {
        _message_key(message.to_dict()) for message in snapshot_b.conversation.messages
    }
    return ContextDiff(
        context_added=sorted(set(values_b) - set(values_a)),
        context_removed=sorted(set(values_a) - set(values_b)),
        context_modified=sorted(
            key
            for key in set(values_a) & set(values_b)
            if values_a[key] != values_b[key]
        ),
        prompt_changed=snapshot_a.prompt.current_prompt
        != snapshot_b.prompt.current_prompt,
        conversation_added=sorted(messages_b - messages_a),
        conversation_removed=sorted(messages_a - messages_b),
    )


def _message_key(message: dict[str, object]) -> str:
    return "|".join(
        str(message.get(key, "")) for key in ("step_index", "role", "content")
    )
