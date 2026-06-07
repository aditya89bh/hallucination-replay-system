"""Command-line interface for deterministic replay."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from hallucination_replay.models import RunTrace
from hallucination_replay.replay.controller import ReplayController
from hallucination_replay.replay.timeline import ReplayTimeline


def load_trace(path: Path) -> RunTrace:
    """Load a run trace from a JSON file."""
    return RunTrace.from_json(path.read_text(encoding="utf-8"))


def create_controller(trace_path: Path, session_id: str) -> ReplayController:
    """Create a replay controller for a trace path."""
    return ReplayController.create(load_trace(trace_path), session_id)


def build_parser() -> argparse.ArgumentParser:
    """Build the replay CLI parser."""
    parser = argparse.ArgumentParser(description="Deterministic trace replay CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser("load", help="Load a trace and show metadata")
    add_trace_arguments(load_parser)

    timeline_parser = subparsers.add_parser("timeline", help="Show trace timeline")
    add_trace_arguments(timeline_parser)

    next_parser = subparsers.add_parser("next", help="Show the next replay step")
    add_trace_arguments(next_parser)

    previous_parser = subparsers.add_parser(
        "previous", help="Show the previous replay step from a position"
    )
    add_trace_arguments(previous_parser)
    previous_parser.add_argument("--position", type=int, default=0)

    jump_parser = subparsers.add_parser("jump", help="Jump to a replay step")
    add_trace_arguments(jump_parser)
    jump_group = jump_parser.add_mutually_exclusive_group(required=True)
    jump_group.add_argument("--step-id")
    jump_group.add_argument("--index", type=int)

    return parser


def add_trace_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common trace arguments to a subparser."""
    parser.add_argument("trace_path", type=Path)
    parser.add_argument("--session-id", default="cli-session")


def write_output(payload: str) -> None:
    """Write CLI output to stdout."""
    sys.stdout.write(f"{payload}\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the replay CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    command = str(args.command)
    trace_path = Path(args.trace_path)

    if command == "load":
        trace = load_trace(trace_path)
        payload = {"run_id": trace.run_id, "status": trace.status}
        write_output(json.dumps(payload, sort_keys=True))
        return 0

    if command == "timeline":
        timeline = ReplayTimeline(load_trace(trace_path)).export()
        write_output(timeline.to_json())
        return 0

    controller = create_controller(trace_path, str(args.session_id))

    if command == "next":
        step = controller.next_step()
        write_output(
            json.dumps(step.to_dict() if step is not None else None, sort_keys=True)
        )
        return 0

    if command == "previous":
        controller.jump_to_index(int(args.position))
        step = controller.previous_step()
        write_output(
            json.dumps(step.to_dict() if step is not None else None, sort_keys=True)
        )
        return 0

    if command == "jump":
        step_id = getattr(args, "step_id", None)
        if step_id is not None:
            step = controller.jump_to_step(str(step_id))
        else:
            step = controller.jump_to_index(int(args.index))
        write_output(json.dumps(step.to_dict(), sort_keys=True))
        return 0

    message = f"Unknown replay command: {command}"
    raise ValueError(message)


if __name__ == "__main__":
    raise SystemExit(main())
