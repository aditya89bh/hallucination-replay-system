from __future__ import annotations

from hallucination_replay.models import (
    AgentStep,
    MemoryEvent,
    ReasoningEvent,
    RetrievalEvent,
    RunTrace,
    ToolCall,
    ToolResult,
    TraceMetadata,
    ValidationEvent,
)


def test_models_are_exported_from_package() -> None:
    assert AgentStep.__name__ == "AgentStep"
    assert MemoryEvent.__name__ == "MemoryEvent"
    assert ReasoningEvent.__name__ == "ReasoningEvent"
    assert RetrievalEvent.__name__ == "RetrievalEvent"
    assert RunTrace.__name__ == "RunTrace"
    assert ToolCall.__name__ == "ToolCall"
    assert ToolResult.__name__ == "ToolResult"
    assert TraceMetadata.__name__ == "TraceMetadata"
    assert ValidationEvent.__name__ == "ValidationEvent"
