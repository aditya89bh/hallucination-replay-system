"""Dashboard service layer for aggregating debugging platform state."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from hallucination_replay.storage import TraceRepository


class DashboardService:
    """Aggregate traces, replay sessions, and analysis reports for dashboards."""

    def __init__(self, repository: TraceRepository) -> None:
        """Initialize the service with a trace repository."""
        self._repository = repository

    def trace_summary(self) -> dict[str, object]:
        """Return deterministic trace counts and run identifiers."""
        run_ids = sorted(self._repository.list_traces())
        traces = [self._repository.load_trace(run_id) for run_id in run_ids]
        statuses: dict[str, int] = {}
        for trace in traces:
            statuses[trace.status] = statuses.get(trace.status, 0) + 1
        return {
            "total": len(traces),
            "run_ids": run_ids,
            "statuses": dict(sorted(statuses.items())),
        }

    def replay_summary(self, sessions: Mapping[str, object]) -> dict[str, object]:
        """Return lightweight replay session metadata."""
        return {
            "total": len(sessions),
            "sessions": [
                self._replay_session_summary(session_id, controller)
                for session_id, controller in sorted(sessions.items())
            ],
        }

    def analysis_summary(self, reports: Mapping[str, object]) -> dict[str, object]:
        """Return failure-analysis report metadata."""
        return {
            "total": len(reports),
            "reports": [
                {
                    "report_id": report_id,
                    "run_id": self._field(report, "run_id"),
                    "finding_count": len(self._list_field(report, "findings")),
                }
                for report_id, report in sorted(reports.items())
            ],
        }

    def hallucination_summary(self, reports: Mapping[str, object]) -> dict[str, object]:
        """Return hallucination report metadata."""
        return {
            "total": len(reports),
            "reports": [
                {
                    "report_id": report_id,
                    "run_id": self._field(report, "run_id"),
                    "severity": self._field(report, "severity"),
                    "contradiction_count": len(
                        self._list_field(report, "contradictions")
                    ),
                }
                for report_id, report in sorted(reports.items())
            ],
        }

    def overview(
        self,
        replay_sessions: Mapping[str, object] | None = None,
        analysis_reports: Mapping[str, object] | None = None,
        hallucination_reports: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Return a combined dashboard overview."""
        return {
            "traces": self.trace_summary(),
            "replay": self.replay_summary(replay_sessions or {}),
            "analysis": self.analysis_summary(analysis_reports or {}),
            "hallucinations": self.hallucination_summary(hallucination_reports or {}),
        }

    def _replay_session_summary(
        self, session_id: str, controller: object
    ) -> dict[str, object]:
        session = getattr(controller, "session", None)
        trace = getattr(controller, "trace", None)
        return {
            "session_id": session_id,
            "run_id": getattr(trace, "run_id", None),
            "current_position": getattr(session, "current_position", None),
            "step_count": getattr(controller, "step_count", None),
        }

    def _field(
        self, value: object, name: str, default: object | None = None
    ) -> object | None:
        if isinstance(value, Mapping):
            mapped = cast(Mapping[str, object], value)
            return mapped.get(name, default)
        return getattr(value, name, default)

    def _list_field(self, value: object, name: str) -> list[object]:
        field = self._field(value, name, [])
        return field if isinstance(field, list) else []
