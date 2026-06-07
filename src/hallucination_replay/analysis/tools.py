"""Tool failure analysis."""

from __future__ import annotations

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_tools


def analyze_tool_failures(trace: RunTrace, step_index: int) -> list[FailureFinding]:
    """Detect failed executions, missing results, and mismatches."""
    tools = reconstruct_tools(trace, step_index)
    findings: list[FailureFinding] = []

    failed_results = [result for result in tools.results if not result.success]
    if failed_results:
        findings.append(
            FailureFinding(
                failure_type=FailureType.TOOL_FAILURE,
                message="Failed tool executions",
                severity=4,
                confidence=0.9,
                evidence=[
                    f"Tool {result.tool_name} failed at step {result.step_id}"
                    for result in failed_results
                ],
                step_index=step_index,
                metadata={"reason": "failed_tool_executions"},
            )
        )

    result_step_ids = {result.step_id for result in tools.results}
    missing_results = [
        call for call in tools.calls if call.step_id not in result_step_ids
    ]
    if missing_results:
        findings.append(
            FailureFinding(
                failure_type=FailureType.TOOL_FAILURE,
                message="Missing tool results",
                severity=4,
                confidence=0.85,
                evidence=[
                    f"Tool call {call.tool_name} at step {call.step_id} has no result"
                    for call in missing_results
                ],
                step_index=step_index,
                metadata={"reason": "missing_tool_results"},
            )
        )

    call_names = {call.step_id: call.tool_name for call in tools.calls}
    mismatches = [
        result
        for result in tools.results
        if result.step_id in call_names
        and result.tool_name != call_names[result.step_id]
    ]
    if mismatches:
        findings.append(
            FailureFinding(
                failure_type=FailureType.TOOL_FAILURE,
                message="Tool call/result mismatches",
                severity=3,
                confidence=0.8,
                evidence=[
                    f"Result {result.tool_name} mismatches call "
                    f"{call_names[result.step_id]} at step {result.step_id}"
                    for result in mismatches
                ],
                step_index=step_index,
                metadata={"reason": "tool_call_result_mismatches"},
            )
        )

    return findings
