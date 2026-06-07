"""Validation reconstruction for replay traces."""

from __future__ import annotations

from pydantic import Field

from hallucination_replay.exceptions import ReplayError
from hallucination_replay.models import RunTrace, ValidationEvent
from hallucination_replay.models.base import TraceModel
from hallucination_replay.reconstruction.context import reconstruct_context


class ValidationRecord(TraceModel):
    """Validation activity associated with a replay step."""

    step_index: int = Field(ge=0)
    event: ValidationEvent


class ReconstructedValidation(TraceModel):
    """Validation activity and results available at a replay step."""

    trace_id: str
    step_index: int = Field(ge=0)
    records: list[ValidationRecord] = Field(default_factory=list)
    passed: list[ValidationRecord] = Field(default_factory=list)
    failed: list[ValidationRecord] = Field(default_factory=list)


def reconstruct_validation(trace: RunTrace, step_index: int) -> ReconstructedValidation:
    """Reconstruct validation activity and validation results at a step."""
    reconstruct_context(trace, step_index)
    records = _validation_records(trace, step_index)
    return ReconstructedValidation(
        trace_id=trace.run_id,
        step_index=step_index,
        records=records,
        passed=[record for record in records if record.event.passed],
        failed=[record for record in records if not record.event.passed],
    )


def _validation_records(trace: RunTrace, step_index: int) -> list[ValidationRecord]:
    raw_records = trace.metadata.get("validations", [])
    if not isinstance(raw_records, list):
        message = "RunTrace metadata field 'validations' must be a list"
        raise ReplayError(message)
    records = [ValidationRecord.model_validate(record) for record in raw_records]
    available_records = [
        record for record in records if record.step_index <= step_index
    ]
    return sorted(
        available_records,
        key=lambda record: (record.step_index, record.event.timestamp),
    )
