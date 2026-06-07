# Hallucination Replay System

A production-oriented Python package for replaying AI agent execution traces and performing root-cause analysis of failures. Phase 1 establishes the professional repository foundation before replay functionality is implemented.

## Project Vision

AI agents need debuggers, not just logs. The Hallucination Replay System aims to make agent failures reproducible, inspectable, and explainable by replaying execution traces and reconstructing the state that shaped each model, retrieval, memory, tool, reasoning, and validation decision.

## Problem Statement

When an agent hallucinates or fails, teams often have scattered evidence: prompts in one place, retrieval logs in another, tool calls elsewhere, and validation results hidden in application code. This makes root-cause analysis slow and unreliable.

This project is intended to answer questions such as:

- Did the model invent information not supported by retrieved context?
- Did retrieval miss, rank, or truncate the right evidence?
- Was memory stale, missing, corrupted, or contradictory?
- Did a tool fail, timeout, return malformed data, or get misread?
- Did reasoning drift from the available evidence?
- Did validation fail to detect or block the issue?

## Architecture

```text
+----------------+      +---------------+      +---------------+
| Agent Runtime  | ---> | Trace Recorder| ---> | Trace Storage |
+----------------+      +---------------+      +---------------+
                                                     |
                                                     v
+----------------+      +----------------------+     +---------------+
| Report Output  | <--- | Failure Analysis     | <-- | Replay Engine |
+----------------+      +----------------------+     +---------------+
                              ^                         |
                              |                         v
                      +----------------------+   +----------------------+
                      | Validation Evidence  |   | State Reconstruction |
                      +----------------------+   +----------------------+
```

Planned architectural layers:

- **Trace recording**: capture prompts, responses, retrievals, memories, tools, validation events, and runtime metadata.
- **Replay engine**: play back trace timelines deterministically and support controlled inspection.
- **State reconstruction**: rebuild agent-visible state at each decision point.
- **Failure analysis**: classify hallucination, retrieval, memory, tool, reasoning, and validation failures with evidence.
- **Reporting**: produce reproducible Markdown, JSON, HTML, notebook, or CI-ready artifacts.

See [docs/architecture.md](docs/architecture.md) for more detail.

## Roadmap

### Phase 1: Repository foundation

- Source-layout Python package
- Packaging metadata and build system
- Ruff, MyPy, Pytest, pre-commit, and CI
- Versioning, logging, settings, and exception foundations
- Architecture, development, and README documentation

### Future phases

- Trace schema and storage adapters
- Replay timeline model
- State reconstruction engine
- Failure analyzers for retrieval, memory, tools, reasoning, and validation
- Report generation
- CLI and integration examples

## Installation

Python 3.11 or newer is required.

```bash
python -m pip install hallucination-replay-system
```

For local development from source:

```bash
git clone https://github.com/aditya89bh/hallucination-replay-system.git
cd hallucination-replay-system
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Development

Run the standard quality gate before pushing changes:

```bash
pytest
ruff check .
mypy .
python -m build
```

Optional pre-commit setup:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

See [docs/development.md](docs/development.md) for the complete development workflow and release checklist.

## Current Status

This repository is intentionally limited to Phase 1 foundations. Replay functionality has not been implemented yet.
