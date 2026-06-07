# Contributing Guide

Thanks for considering a contribution to `hallucination-replay-system`. The project values deterministic behavior, strict typing, focused commits, and clear tests.

## Setup

Use Python 3.11 or newer.

```bash
git clone https://github.com/aditya89bh/hallucination-replay-system.git
cd hallucination-replay-system
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Optional pre-commit setup:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

## Code style

- Use Ruff for linting and formatting policy.
- Keep public functions typed.
- Prefer domain models over loose dictionaries at package boundaries.
- Keep deterministic output stable by sorting keys or collections where order matters.
- Do not add LLM calls to hallucination detection or failure analysis logic.
- Do not compare, infer, or expose hidden chain-of-thought; reasoning features should use summaries, confidence, and event types only.

Run style checks:

```bash
ruff check .
ruff format .
```

## Testing

Every behavior change should include tests.

Required local gate:

```bash
pytest
ruff check .
mypy .
```

Coverage gate:

```bash
pytest --cov
```

The configured minimum coverage threshold is intentionally realistic for the current suite. If coverage drops, add focused tests rather than lowering the threshold.

## Commit expectations

Keep commits focused and reviewable:

- One logical task per commit.
- Do not mix formatting-only changes with behavior changes unless required by the task.
- Write imperative commit messages, for example `Add replay API endpoints`.
- Run the quality gate before committing.

## Issue guidelines

When opening an issue, include:

- A clear problem statement.
- Reproduction steps or a minimal trace fixture when possible.
- Expected behavior and actual behavior.
- Python version and operating system.
- Relevant command output, stack trace, or report snippets.

Avoid posting secrets, private prompts, customer data, or raw chain-of-thought in issues.

## Pull request guidelines

A good pull request includes:

- A concise summary of the change.
- Tests that cover the new or changed behavior.
- Documentation updates when user-facing workflows change.
- Notes about deterministic behavior, compatibility, or known limitations.
- Confirmation that `pytest`, `ruff check .`, and `mypy .` pass locally.

For release-quality changes, also run:

```bash
python -m build
```

## Documentation updates

Update docs when changing:

- Trace schemas or model behavior.
- Replay, reconstruction, analysis, hallucination, or diffing APIs.
- FastAPI endpoints or request/response schemas.
- CLI commands.
- Benchmark interpretation.
- Production-readiness boundaries.

## Security and privacy

Trace files can contain sensitive data. Contributions should preserve privacy-conscious defaults:

- Do not commit real secrets or private traces.
- Redact credentials, tokens, and personal data from examples.
- Keep hosted/API security limitations documented.
- Prefer deterministic local analysis over sending trace data to external services.
