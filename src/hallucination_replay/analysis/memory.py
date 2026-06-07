"""Memory failure analysis."""

from __future__ import annotations

from typing import Any

from hallucination_replay.analysis.taxonomy import FailureFinding, FailureType
from hallucination_replay.models import RunTrace
from hallucination_replay.reconstruction import reconstruct_memory


def analyze_memory_failures(trace: RunTrace, step_index: int) -> list[FailureFinding]:
    """Detect missing reads, stale access, and state inconsistencies."""
    memory = reconstruct_memory(trace, step_index)
    findings: list[FailureFinding] = []

    expected_reads = _string_items(
        trace.metadata.get("memory_expected_reads", []), step_index
    )
    read_keys = {record.event.key for record in memory.reads}
    missing_reads = sorted(key for key in expected_reads if key not in read_keys)
    if missing_reads:
        findings.append(
            FailureFinding(
                failure_type=FailureType.MEMORY_FAILURE,
                message="Missing memory reads",
                severity=4,
                confidence=0.85,
                evidence=[
                    f"Expected memory read not observed: {key}" for key in missing_reads
                ],
                step_index=step_index,
                metadata={"reason": "missing_memory_reads"},
            )
        )

    stale_keys = sorted(
        set(_string_items(trace.metadata.get("stale_memory_keys", []), step_index))
    )
    stale_access = [
        record.event.key for record in memory.reads if record.event.key in stale_keys
    ]
    if stale_access:
        findings.append(
            FailureFinding(
                failure_type=FailureType.MEMORY_FAILURE,
                message="Stale memory access",
                severity=3,
                confidence=0.8,
                evidence=[
                    f"Read stale memory key: {key}" for key in sorted(stale_access)
                ],
                step_index=step_index,
                metadata={"reason": "stale_memory_access"},
            )
        )

    inconsistencies = _memory_inconsistencies(memory.state, trace.metadata, step_index)
    if inconsistencies:
        findings.append(
            FailureFinding(
                failure_type=FailureType.MEMORY_FAILURE,
                message="Memory state inconsistencies",
                severity=4,
                confidence=0.8,
                evidence=inconsistencies,
                step_index=step_index,
                metadata={"reason": "memory_state_inconsistencies"},
            )
        )

    return findings


def _string_items(raw_items: object, step_index: int) -> list[str]:
    if not isinstance(raw_items, list):
        return []
    items: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            item_step = item.get("step_index", 0)
            value = item.get("key", item.get("value", ""))
            if (
                isinstance(item_step, int)
                and item_step <= step_index
                and isinstance(value, str)
            ):
                items.append(value)
        elif isinstance(item, str):
            items.append(item)
    return sorted(item for item in items if item.strip())


def _memory_inconsistencies(
    state: dict[str, Any], metadata: dict[str, Any], step_index: int
) -> list[str]:
    raw_expected = metadata.get("memory_expected_state", {})
    if not isinstance(raw_expected, dict):
        return []
    inconsistencies: list[str] = []
    for key, expected in sorted(raw_expected.items()):
        if not isinstance(key, str):
            continue
        expected_step = 0
        expected_value = expected
        if isinstance(expected, dict) and "value" in expected:
            expected_step_raw = expected.get("step_index", 0)
            if not isinstance(expected_step_raw, int):
                continue
            expected_step = expected_step_raw
            expected_value = expected["value"]
        if expected_step <= step_index and state.get(key) != expected_value:
            inconsistencies.append(
                f"Memory key {key!r} expected {expected_value!r} "
                f"but found {state.get(key)!r}"
            )
    return inconsistencies
