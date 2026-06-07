# Changelog

All notable changes to `hallucination-replay-system` will be documented in this file.

The project follows a release-candidate style changelog while the public v1.0.0 tag has not yet been created.

## Unreleased

- Release hardening and presentation polish for the v1.0.0 release candidate.
- Coverage reporting and a realistic coverage quality gate.
- Benchmark, API, CLI, production readiness, demo, and contributor documentation.
- Architecture diagram assets and repository validation tooling.
- Release workflow for build, test, lint, type check, and artifact upload.

## v1.0.0 planned

The planned v1.0.0 release represents a complete deterministic debugging platform for AI agent traces.

### Foundation

- Typed Pydantic trace models for runs, metadata, steps, memory, retrieval, reasoning, validation, tool calls, and tool results.
- Strict project configuration for Ruff, MyPy, Pytest, packaging, and CI.
- Structured exceptions, logging helpers, and development documentation.

### Storage

- Filesystem trace repository and JSON trace store.
- Trace index, metadata queries, filters, search, lifecycle management, retention policies, compression, import, and export helpers.
- Storage benchmarks and integration coverage.

### Replay

- Deterministic replay trace loader, controller, session state, navigation, snapshots, checkpoints, timeline export, and CLI.
- Forward/backward navigation and jump-by-step support.

### Reconstruction

- Context, conversation, prompt, memory, retrieval, tool, validation, reasoning, and full state reconstruction.
- Reconstruction reports and examples.
- Reasoning reconstruction exposes summaries, confidence, and event types only.

### Failure analysis

- Failure taxonomy and analyzers for intent, retrieval, memory, tool, validation, reasoning, and output failures.
- Confidence scoring, root-cause ranking, contributing factor analysis, summaries, and Markdown/JSON reports.

### Hallucination detection

- Deterministic claim extraction, evidence extraction, normalization, evidence matching, unsupported-claim detection, contradiction detection, coverage scoring, hallucination scoring, severity ranking, reports, benchmark traces, and evaluation suite.
- No LLM calls are used for detection logic.

### Execution comparison

- Deterministic trace, state, context, retrieval, memory, tool, reasoning, and timeline diffing.
- Aggregated execution comparison and Markdown/JSON comparison reports.
- Comparison examples and benchmarks.

### Platform

- FastAPI application with health, version, trace, replay, reconstruction, failure analysis, hallucination analysis, and comparison endpoints.
- OpenAPI documentation and endpoint examples.
- Lightweight deterministic dashboard helpers for timelines, replay state, failure analysis, and hallucination analysis.
- End-to-end API integration tests.

### Release quality

- Coverage reporting and quality gate.
- Benchmark documentation.
- API and CLI reference documentation.
- Production readiness guidance.
- Demo guide, contributor guide, changelog, release workflow, README polish, and repository validation script.

## Notes

- No v1.0.0 tag or GitHub release has been created yet.
- Publishing to PyPI is intentionally not automated in the release workflow.
- Hosted multi-tenant observability, authentication, database-backed report storage, and rich browser UI remain future work.
