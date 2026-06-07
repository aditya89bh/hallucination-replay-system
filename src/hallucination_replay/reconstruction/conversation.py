"""Conversation reconstruction for replay traces."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context

MessageRole = Literal["system", "user", "assistant", "tool"]


class ConversationMessage(TraceModel):
    """Conversation message associated with a replay step."""

    step_index: int = Field(ge=0)
    role: MessageRole
    content: str
    timestamp: datetime


class ReconstructedConversation(TraceModel):
    """Conversation state and ordered interaction history."""

    trace_id: str
    step_index: int = Field(ge=0)
    messages: list[ConversationMessage] = Field(default_factory=list)


def reconstruct_conversation(
    trace: RunTrace, step_index: int
) -> ReconstructedConversation:
    """Reconstruct conversation state and history at a replay step."""
    reconstruct_context(trace, step_index)
    return ReconstructedConversation(
        trace_id=trace.run_id,
        step_index=step_index,
        messages=_conversation_messages(trace, step_index),
    )


def _conversation_messages(
    trace: RunTrace, step_index: int
) -> list[ConversationMessage]:
    raw_messages = trace.metadata.get("conversation", [])
    if not isinstance(raw_messages, list):
        message = "RunTrace metadata field 'conversation' must be a list"
        raise ReplayError(message)
    messages = [ConversationMessage.model_validate(message) for message in raw_messages]
    available_messages = [
        message for message in messages if message.step_index <= step_index
    ]
    return sorted(
        available_messages,
        key=lambda message: (message.step_index, message.timestamp, message.role),
    )
