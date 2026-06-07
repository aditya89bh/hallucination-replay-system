"""Output failure analysis."""

from __future__ import annotations

from typing import Any

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_context


def analyze_output_failures(trace: RunTrace, step_index: int) -> list[FailureFinding]:
    """Detect empty, incomplete, and missing final response outputs."""
    reconstruct_context(trace, step_index)
    outputs = _outputs_at_step(trace.metadata.get("outputs", []), step_index)
    findings: list[FailureFinding] = []

    empty_outputs = [
        output for output in outputs if not _output_content(output).strip()
    ]
    if empty_outputs:
        findings.append(
            FailureFinding(
                failure_type=FailureType.OUTPUT_FAILURE,
                message="Empty outputs",
                severity=4,
                confidence=0.9,
                evidence=["Output artifact had empty content" for _ in empty_outputs],
                step_index=step_index,
                metadata={"reason": "empty_outputs"},
            )
        )

    incomplete = _strings_by_step(
        trace.metadata.get("incomplete_outputs", []), step_index
    )
    if incomplete:
        findings.append(
            FailureFinding(
                failure_type=FailureType.OUTPUT_FAILURE,
                message="Incomplete outputs",
                severity=4,
                confidence=0.85,
                evidence=incomplete,
                step_index=step_index,
                metadata={"reason": "incomplete_outputs"},
            )
        )

    if not any(_is_final_response(output) for output in outputs):
        findings.append(
            FailureFinding(
                failure_type=FailureType.OUTPUT_FAILURE,
                message="Missing final response artifacts",
                severity=5,
                confidence=0.9,
                evidence=["No final response artifact was available at this step"],
                step_index=step_index,
                metadata={"reason": "missing_final_response_artifacts"},
            )
        )

    return findings


def _outputs_at_step(raw_outputs: object, step_index: int) -> list[dict[str, Any]]:
    if not isinstance(raw_outputs, list):
        return []
    outputs: list[dict[str, Any]] = []
    for output in raw_outputs:
        if not isinstance(output, dict):
            continue
        raw_step = output.get("step_index", 0)
        if isinstance(raw_step, int) and raw_step <= step_index:
            outputs.append(output)
    return outputs


def _output_content(output: dict[str, Any]) -> str:
    content = output.get("content", output.get("text", ""))
    return content if isinstance(content, str) else str(content)


def _is_final_response(output: dict[str, Any]) -> bool:
    artifact_type = output.get("artifact_type", output.get("type", ""))
    is_final = output.get("final", False)
    return artifact_type == "final_response" or is_final is True


def _strings_by_step(raw_items: object, step_index: int) -> list[str]:
    if not isinstance(raw_items, list):
        return []
    values: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            item_step = item.get("step_index", 0)
            value = item.get("reason", item.get("value", ""))
            if (
                isinstance(item_step, int)
                and item_step <= step_index
                and isinstance(value, str)
            ):
                values.append(value)
        elif isinstance(item, str):
            values.append(item)
    return sorted(value for value in values if value.strip())
