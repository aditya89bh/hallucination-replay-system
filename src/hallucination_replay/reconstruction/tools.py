"""Tool reconstruction for replay traces."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import RunTrace, ToolCall, ToolResult
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context


class ToolRecord(TraceModel):
    """A tool call and optional result associated with a replay step."""

    step_index: int = Field(ge=0)
    call: ToolCall
    result: ToolResult | None = None


class ToolTimelineItem(TraceModel):
    """Compact tool state timeline item."""

    step_index: int = Field(ge=0)
    tool_name: str
    step_id: str
    status: str


class ReconstructedTools(TraceModel):
    """Tool calls, results, and tool state timeline at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    calls: list[ToolCall] = Field(default_factory=list)
    results: list[ToolResult] = Field(default_factory=list)
    timeline: list[ToolTimelineItem] = Field(default_factory=list)


def reconstruct_tools(trace: RunTrace, step_index: int) -> ReconstructedTools:
    """Reconstruct tool calls, results, and state timeline at a step."""
    reconstruct_context(trace, step_index)
    records = _tool_records(trace, step_index)
    return ReconstructedTools(
        trace_id=trace.run_id,
        step_index=step_index,
        calls=[record.call for record in records],
        results=[record.result for record in records if record.result is not None],
        timeline=[_timeline_item(record) for record in records],
    )


def _tool_records(trace: RunTrace, step_index: int) -> list[ToolRecord]:
    raw_records = trace.metadata.get("tools", [])
    if not isinstance(raw_records, list):
        message = "RunTrace metadata field 'tools' must be a list"
        raise ReplayError(message)
    records = [ToolRecord.model_validate(record) for record in raw_records]
    available_records = [
        record for record in records if record.step_index <= step_index
    ]
    return sorted(
        available_records,
        key=lambda record: (record.step_index, record.call.invocation_time),
    )


def _timeline_item(record: ToolRecord) -> ToolTimelineItem:
    status = "pending"
    if record.result is not None:
        status = "success" if record.result.success else "failed"
    return ToolTimelineItem(
        step_index=record.step_index,
        tool_name=record.call.tool_name,
        step_id=record.call.step_id,
        status=status,
    )
