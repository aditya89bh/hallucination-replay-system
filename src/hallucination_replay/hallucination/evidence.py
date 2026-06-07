"""Deterministic evidence extraction from execution artifacts."""

from __future__ import annotations

from typing import Any

from hallucination_replay.models import RunTrace
from hallucination_replay.models.base import TraceModel


class Evidence(TraceModel):
    """Evidence available to the agent at a specific step."""

    evidence_id: str
    text: str
    source: str
    source_step: int


def extract_evidence(trace: RunTrace, step_index: int | None = None) -> list[Evidence]:
    """Extract evidence from retrievals, tool results, and memory events."""
    evidence: list[Evidence] = []
    evidence.extend(
        _retrieval_evidence(trace.metadata.get("retrievals", []), step_index)
    )
    evidence.extend(_tool_evidence(trace.metadata.get("tools", []), step_index))
    evidence.extend(_memory_evidence(trace.metadata.get("memory", []), step_index))
    return evidence


def _retrieval_evidence(records: object, max_step: int | None) -> list[Evidence]:
    evidence: list[Evidence] = []
    if not isinstance(records, list):
        return evidence
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        step = _record_step(record)
        if not _within_step(step, max_step):
            continue
        results = record.get("results", record.get("documents", []))
        for result_index, result in enumerate(_as_list(results)):
            text = _text_from_payload(result)
            if text:
                evidence.append(
                    Evidence(
                        evidence_id=f"retrieval-{index}-{result_index}",
                        text=text,
                        source="retrieval",
                        source_step=step,
                    )
                )
    return evidence


def _tool_evidence(records: object, max_step: int | None) -> list[Evidence]:
    evidence: list[Evidence] = []
    if not isinstance(records, list):
        return evidence
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        step = _record_step(record)
        if not _within_step(step, max_step):
            continue
        result = record.get("result", record.get("output", record))
        text = _text_from_payload(result)
        if text:
            evidence.append(
                Evidence(
                    evidence_id=f"tool-{index}",
                    text=text,
                    source="tool",
                    source_step=step,
                )
            )
    return evidence


def _memory_evidence(records: object, max_step: int | None) -> list[Evidence]:
    evidence: list[Evidence] = []
    if not isinstance(records, list):
        return evidence
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        step = _record_step(record)
        if not _within_step(step, max_step):
            continue
        text = _text_from_payload(record.get("value", record.get("content", record)))
        if text:
            evidence.append(
                Evidence(
                    evidence_id=f"memory-{index}",
                    text=text,
                    source="memory",
                    source_step=step,
                )
            )
    return evidence


def _record_step(record: dict[str, Any]) -> int:
    value = record.get("step_index", record.get("source_step", 0))
    return value if isinstance(value, int) else 0


def _within_step(step: int, max_step: int | None) -> bool:
    return max_step is None or step <= max_step


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else [value]


def _text_from_payload(payload: object) -> str:
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        for key in ("text", "content", "output", "value"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return " ".join(
            f"{key}: {value}"
            for key, value in sorted(payload.items())
            if isinstance(value, str)
        ).strip()
    return ""
