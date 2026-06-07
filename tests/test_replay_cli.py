from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from _pytest.capture import CaptureFixture

from hallucination_replay.models import AgentStep, RunTrace
from hallucination_replay.replay import steps_to_metadata
from hallucination_replay.replay.cli import main


def make_step(step_id: str, index: int) -> AgentStep:
    return AgentStep(
        step_id=step_id,
        step_index=index,
        step_type="model",
        timestamp=datetime(2026, 1, 1, 0, index, tzinfo=UTC),
        description=step_id,
    )


def write_trace(tmp_path: Path) -> Path:
    trace = RunTrace(
        run_id="run-1",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        status="completed",
        metadata=steps_to_metadata(
            [make_step("step-1", 0), make_step("step-2", 1)]
        ),
    )
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(trace.to_json(), encoding="utf-8")
    return trace_path


def test_cli_load_trace(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    trace_path = write_trace(tmp_path)

    exit_code = main(["load", str(trace_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {"run_id": "run-1", "status": "completed"}


def test_cli_timeline(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    trace_path = write_trace(tmp_path)

    exit_code = main(["timeline", str(trace_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["steps"][0]["step_id"] == "step-1"


def test_cli_jump_by_index(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    trace_path = write_trace(tmp_path)

    exit_code = main(["jump", str(trace_path), "--index", "1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["step_id"] == "step-2"
