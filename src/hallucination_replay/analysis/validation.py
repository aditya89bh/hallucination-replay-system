"""Validation failure analysis."""

from __future__ import annotations

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_validation


def analyze_validation_failures(
    trace: RunTrace, step_index: int
) -> list[FailureFinding]:
    """Detect missing validation, ignored failures, and coverage gaps."""
    validation = reconstruct_validation(trace, step_index)
    findings: list[FailureFinding] = []

    if not validation.records:
        findings.append(
            FailureFinding(
                failure_type=FailureType.VALIDATION_FAILURE,
                message="Validation never executed",
                severity=4,
                confidence=0.9,
                evidence=["No validation records were available at this step"],
                step_index=step_index,
                metadata={"reason": "validation_never_executed"},
            )
        )
        return findings

    ignored = _strings_by_step(
        trace.metadata.get("ignored_validations", []), step_index
    )
    failed_names = {record.event.validator_name for record in validation.failed}
    ignored_failures = sorted(name for name in ignored if name in failed_names)
    if ignored_failures:
        findings.append(
            FailureFinding(
                failure_type=FailureType.VALIDATION_FAILURE,
                message="Failed validations ignored",
                severity=5,
                confidence=0.85,
                evidence=[
                    f"Failed validation ignored: {name}" for name in ignored_failures
                ],
                step_index=step_index,
                metadata={"reason": "failed_validations_ignored"},
            )
        )

    required = _strings_by_step(
        trace.metadata.get("validation_requirements", []), step_index
    )
    executed = {record.event.validator_name for record in validation.records}
    missing = sorted(name for name in required if name not in executed)
    if missing:
        findings.append(
            FailureFinding(
                failure_type=FailureType.VALIDATION_FAILURE,
                message="Validation coverage gaps",
                severity=3,
                confidence=0.8,
                evidence=[
                    f"Required validation not executed: {name}" for name in missing
                ],
                step_index=step_index,
                metadata={"reason": "validation_coverage_gaps"},
            )
        )

    return findings


def _strings_by_step(raw_items: object, step_index: int) -> list[str]:
    if not isinstance(raw_items, list):
        return []
    values: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            item_step = item.get("step_index", 0)
            value = item.get("validator_name", item.get("value", ""))
            if (
                isinstance(item_step, int)
                and item_step <= step_index
                and isinstance(value, str)
            ):
                values.append(value)
        elif isinstance(item, str):
            values.append(item)
    return sorted(value for value in values if value.strip())
