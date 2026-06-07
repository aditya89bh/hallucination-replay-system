# Troubleshooting Guide

This guide covers common setup, build, API, replay, and analysis issues for `hallucination-replay-system`.

## Installation issues

### Python version is too old

The package requires Python 3.11 or newer.

Check your version:

```bash
python --version
```

Create a fresh Python 3.11 environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Development extras are missing

If `pytest`, `ruff`, `mypy`, or `build` is unavailable, reinstall with development extras:

```bash
python -m pip install -e ".[dev]"
```

### Package imports fail from a checkout

Make sure the virtual environment is active and the editable install completed:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -c "import hallucination_replay; print(hallucination_replay.__version__)"
```

## Build issues

### Build artifacts are stale

Remove old build output before building release artifacts:

```bash
rm -rf dist build *.egg-info
python -m build
```

### Artifact verification fails

Build first, then verify with the exact package version:

```bash
python -m build
python scripts/verify_release_artifacts.py --version 1.0.0rc1
```

If verification reports missing files, inspect the wheel and source distribution contents and confirm package paths are included by `pyproject.toml`.

### Coverage gate fails

Run the full coverage command locally:

```bash
pytest --cov
```

The configured threshold is 90%. If coverage drops below the threshold, add focused tests for the changed behavior instead of lowering the gate.

## API issues

### FastAPI app does not start

Install development dependencies and start with an ASGI server:

```bash
python -m pip install -e ".[dev]"
uvicorn hallucination_replay.api:create_app --factory --reload
```

### Trace upload returns a validation error

Confirm the JSON matches the trace schema and includes required run metadata and step data. See [Trace schema](trace_schema.md).

### Trace lookup returns 404

A missing trace returns a `404` response. Confirm the uploaded `run_id` matches the ID used in the lookup, replay, reconstruction, analysis, hallucination, or comparison request.

### Replay jump returns 422

Jump requests must include either `step_id` or `step_index`:

```bash
curl -X POST http://localhost:8000/replay/sessions/<session_id>/jump \
  -H 'content-type: application/json' \
  -d '{"step_index":3}'
```

## Replay issues

### Replay session is missing

Replay sessions are app-state backed. If the API process restarts, create a new replay session before navigating.

### Steps appear out of order

Replay uses serialized `AgentStep` records stored in trace metadata and sorts by `step_index`. Check for duplicated, missing, or malformed `step_index` values in the trace.

### Navigation does not move

Confirm the session has more than one step and that the replay controller is not already at the first or last step.

## Analysis issues

### Failure analysis finds too little

Analysis quality depends on the captured trace. If prompts, retrievals, tool outputs, validation events, or memory records are missing, findings may be incomplete.

### Hallucination detection seems conservative

Detection is deterministic and evidence-based. It does not use an LLM judge. If a claim requires semantic interpretation beyond captured evidence, review the extracted claims and evidence manually.

### Contradictions are not detected

Contradiction detection depends on explicit conflicting evidence in the trace. If the contradictory evidence was not captured, the detector cannot infer it from outside knowledge.

### Reasoning analysis does not show chain-of-thought

This is intentional. Reasoning reconstruction exposes summaries, confidence changes, and reasoning event types only. It does not reconstruct or infer hidden chain-of-thought.

## Repository validation issues

Run the validation script from the repository root:

```bash
python scripts/validate_repo.py
```

If it fails, restore missing required docs, benchmark files, README sections, or public package imports before cutting a release.

## Getting a clean local state

From the repository root:

```bash
git status --short
pytest
ruff check .
mypy .
python scripts/validate_repo.py
```

A clean release-candidate checkout should have an empty `git status --short` output after committed changes are pushed.
