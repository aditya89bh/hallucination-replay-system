# CLI Reference

The project includes a small deterministic replay CLI for inspecting trace files from a terminal. It is intentionally focused on replay navigation and timeline viewing; analysis and platform workflows are exposed through Python APIs and FastAPI endpoints.

## Installation

Install the project in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Run the CLI module from the repository root:

```bash
python -m hallucination_replay.replay.cli --help
```

## Trace loading

Use `load` to verify that a trace can be parsed and to print basic metadata.

```bash
python -m hallucination_replay.replay.cli load path/to/trace.json
```

Output is deterministic JSON:

```json
{"run_id": "example-run", "status": "completed"}
```

The trace must conform to the `RunTrace` schema and include replay steps in `metadata["steps"]` for navigation commands.

## Timeline viewing

Use `timeline` to display ordered replay steps and summary metadata.

```bash
python -m hallucination_replay.replay.cli timeline path/to/trace.json
```

The output includes the ordered step list, step count, first step, and last step. Timeline output is useful before debugging because it confirms the available `step_id` and `step_index` values.

## Navigation commands

All navigation commands accept a trace path and optional session ID:

```bash
python -m hallucination_replay.replay.cli next path/to/trace.json --session-id demo
python -m hallucination_replay.replay.cli previous path/to/trace.json --position 3
python -m hallucination_replay.replay.cli jump path/to/trace.json --index 5
python -m hallucination_replay.replay.cli jump path/to/trace.json --step-id step-005
```

### `next`

`next` creates a replay controller and prints the next step from the initial replay position.

```bash
python -m hallucination_replay.replay.cli next examples/replay/example_trace.json
```

If there is no next step, the command prints JSON `null`.

### `previous`

`previous` first jumps to `--position` and then prints the previous step.

```bash
python -m hallucination_replay.replay.cli previous examples/replay/example_trace.json --position 4
```

Use this to inspect reverse navigation behavior around a known step index.

### `jump`

`jump` moves directly to a step by either step ID or numeric index. Exactly one selector is required.

```bash
python -m hallucination_replay.replay.cli jump examples/replay/example_trace.json --index 2
python -m hallucination_replay.replay.cli jump examples/replay/example_trace.json --step-id tool-call-2
```

The command prints the selected step as JSON.

## Example workflow

1. Load the trace:

   ```bash
   python -m hallucination_replay.replay.cli load trace.json
   ```

2. Inspect timeline metadata:

   ```bash
   python -m hallucination_replay.replay.cli timeline trace.json
   ```

3. Jump to a suspicious step:

   ```bash
   python -m hallucination_replay.replay.cli jump trace.json --index 7
   ```

4. Inspect neighboring steps:

   ```bash
   python -m hallucination_replay.replay.cli previous trace.json --position 7
   python -m hallucination_replay.replay.cli next trace.json
   ```

## Output and errors

- Successful commands write JSON to stdout.
- Invalid trace files raise schema validation errors.
- Invalid step IDs or indexes raise replay errors.
- The CLI does not mutate trace files, call tools, execute agent code, or perform hallucination detection.

For richer workflows, use the FastAPI platform endpoints documented in `docs/openapi.md`.
