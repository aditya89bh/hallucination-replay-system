# Development Guide

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

Install pre-commit hooks if you want local checks before commits and pushes:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

## Linting and Formatting

Ruff is used for linting and formatting policy.

```bash
ruff check .
ruff format .
```

CI runs `ruff check .`. The pre-commit configuration checks both linting and formatting.

## Type Checking

MyPy runs in strict mode against `src` and `tests`.

```bash
mypy .
```

Keep public functions typed and prefer explicit domain models over unstructured dictionaries.

## Testing

Pytest is used for the test suite.

```bash
pytest
```

Generate a local coverage report with pytest-cov:

```bash
pytest --cov
pytest --cov --cov-report=html
```

The terminal report shows line and branch coverage by package. Coverage is
configured with a 90% minimum quality gate; CI runs `pytest --cov` and fails if
coverage drops below that threshold. The optional HTML report is written to
`htmlcov/` for local inspection and is not committed.

Tests live in `tests/` and should be added with every behavior change.

## Build Verification

Before release or packaging changes, build the source distribution and wheel:

```bash
python -m build
```

The generated artifacts are written to `dist/` and are not committed.

## Release Process

1. Confirm the changelog or release notes describe user-visible changes.
2. Update package version metadata in `pyproject.toml` and `src/hallucination_replay/_version.py`.
3. Run the full quality gate:

   ```bash
   pytest
   ruff check .
   mypy .
   python -m build
   ```

4. Tag the release from a clean main branch.
5. Publish artifacts only after CI passes for the release commit.

## Commit Discipline

Keep commits focused and reviewable. Each task should map to exactly one commit, and unrelated changes should be split into separate commits.
