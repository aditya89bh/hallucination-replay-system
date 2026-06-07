"""Comparison report generation."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from hallucination_replay.diffing.comparison import ExecutionComparison


def generate_comparison_markdown_report(comparison: ExecutionComparison) -> str:
    """Generate a deterministic markdown comparison report."""
    data = comparison.to_dict()
    trace = comparison.trace_diff
    lines = [
        "# Execution Comparison Report",
        "",
        "## Summary",
        f"- Run A: {trace.run_a_id} ({trace.status_a})",
        f"- Run B: {trace.run_b_id} ({trace.status_b})",
        f"- Status changed: {trace.status_changed}",
        f"- Step count delta: {trace.step_count_delta}",
        f"- Total changes: {_count_changes(data)}",
        "",
        "## Change Counts",
    ]
    lines.extend(
        f"- {section}: {_count_changes(data[section])}" for section in sorted(data)
    )
    lines.extend(["", "## Detailed Diff"])
    for section in sorted(data):
        lines.extend(["", f"### {section}"])
        section_lines = _render_value(data[section], indent=0)
        lines.extend(section_lines or ["- No changes"])
    return "\n".join(lines) + "\n"


def _count_changes(value: object) -> int:
    if isinstance(value, Mapping):
        total = 0
        for item in value.values():
            total += _count_changes(item)
        return total
    if isinstance(value, list):
        return len(value)
    if isinstance(value, tuple):
        return len(value)
    if isinstance(value, bool):
        return int(value)
    if value is None:
        return 0
    return 1


def _render_value(value: object, indent: int) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, Mapping):
        lines: list[str] = []
        for key in sorted(value):
            item = value[key]
            if isinstance(item, Mapping | Sequence) and not isinstance(item, str):
                lines.append(f"{prefix}- {key}:")
                lines.extend(_render_value(item, indent + 1))
            else:
                lines.append(f"{prefix}- {key}: {item}")
        return lines
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [f"{prefix}- {item}" for item in value]
    return [f"{prefix}- {value}"]


def generate_comparison_json_report(comparison: ExecutionComparison) -> str:
    """Generate a deterministic structured JSON comparison report."""
    data = comparison.to_dict()
    payload = {
        "report_type": "execution_comparison",
        "run_a_id": comparison.trace_diff.run_a_id,
        "run_b_id": comparison.trace_diff.run_b_id,
        "status_changed": comparison.trace_diff.status_changed,
        "change_counts": {
            section: _count_changes(data[section]) for section in sorted(data)
        },
        "comparison": data,
    }
    return json.dumps(payload, sort_keys=True)
