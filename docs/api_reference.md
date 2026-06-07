# API Reference

This reference summarizes the public Python APIs and FastAPI platform endpoints used to replay traces, reconstruct execution state, analyze failures, detect hallucinations, and compare executions.

## Trace models

Core models live under `hallucination_replay.models`.

- `RunTrace` — top-level execution trace with `run_id`, timestamps, `status`, and flexible `metadata`.
- `TraceMetadata` — structured run metadata for agent, model, environment, tags, and extra fields.
- `AgentStep` — ordered replay step with `step_id`, `step_index`, `step_type`, timestamp, and description.
- `MemoryEvent`, `RetrievalEvent`, `ReasoningEvent`, `ValidationEvent`, `ToolCall`, and `ToolResult` — event models used by reconstruction, replay, and analysis modules.

All models inherit common Pydantic serialization helpers such as `to_dict()` and `to_json()`.

## Storage layer

Storage APIs live under `hallucination_replay.storage`.

- `TraceRepository` defines the repository interface.
- `FilesystemTraceRepository` persists traces and maintains a filesystem-backed index.
- `JsonTraceStore` reads and writes individual JSON trace files.
- `TraceIndex` maintains searchable trace metadata.
- `TraceSearch` provides search helpers for status, tags, agents, and metadata values.
- Filters, retention policies, lifecycle management, compression, import, and export helpers support repository maintenance workflows.

Typical usage:

```python
from pathlib import Path
from hallucination_replay.storage import FilesystemTraceRepository

repository = FilesystemTraceRepository(Path("./traces"))
run_ids = repository.list_traces()
trace = repository.load_trace(run_ids[0])
```

## Replay engine

Replay APIs live under `hallucination_replay.replay`.

- `ReplayTraceLoader` validates and loads serialized `AgentStep` objects from `RunTrace.metadata["steps"]`.
- `ReplayController` manages replay position and navigation.
- `ReplaySession` captures replay session identity, current step, and navigation state.
- `ReplayTimeline` exports ordered step metadata and summaries.
- `ReplaySnapshot` and checkpoint helpers persist deterministic replay positions.
- `steps_to_metadata()` serializes step lists back into trace metadata.

Replay operations are deterministic and do not execute agent code or external tools.

## Reconstruction

Reconstruction APIs live under `hallucination_replay.reconstruction`.

- `reconstruct_context()` returns context entries visible at a step.
- `reconstruct_memory()` folds memory events into step-local memory state.
- `reconstruct_prompt()` rebuilds prompt inputs from context and metadata.
- `reconstruct_conversation()` reconstructs visible conversation messages.
- `reconstruct_retrieval()` reconstructs retrieval evidence available by step.
- `reconstruct_tools()` reconstructs tool calls, results, and tool timeline.
- `reconstruct_validation()` reconstructs validation events.
- `reconstruct_reasoning()` exposes reasoning summaries, confidence, and event types only; it does not compare or infer chain-of-thought.
- `reconstruct_state()` aggregates the reconstructed execution state.

## Failure analysis

Failure analysis APIs live under `hallucination_replay.analysis`.

- `FailureFinding`, `FailureCategory`, and `FailureSeverity` define the taxonomy.
- Analyzers include intent, retrieval, memory, tool, validation, reasoning, and output failure detection.
- `score_findings()` assigns confidence scores.
- `rank_root_causes()` orders likely root causes.
- `analyze_contributing_factors()` groups secondary factors.
- `summarize_failures()` creates compact summaries.
- `generate_failure_markdown_report()` and `generate_failure_json_report()` render deterministic reports.

All analyzers are deterministic and operate on trace metadata and reconstructed state.

## Hallucination detection

Hallucination APIs live under `hallucination_replay.hallucination`.

- `extract_claims_from_outputs()` extracts claims from agent outputs.
- `extract_evidence()` collects retrieval, tool, and memory evidence available at a step.
- Normalization helpers produce stable text comparisons.
- `match_claims_to_evidence()` scores claim support.
- `detect_unsupported_claims()` flags missing or weak evidence.
- `detect_contradictions()` flags rule-based evidence conflicts.
- `score_evidence_coverage()` and `score_hallucinations()` compute aggregate scores.
- `rank_hallucination_severity()` maps scores to severity levels.
- Markdown and JSON report helpers render deterministic analysis output.

Detection does not call LLMs.

## Diffing and comparison

Diffing APIs live under `hallucination_replay.diffing`.

- Trace, state, context, retrieval, memory, tool, reasoning, and timeline diff engines compare deterministic execution artifacts.
- `compare_executions()` aggregates all diff dimensions into one comparison object.
- Report helpers generate Markdown and JSON comparison reports.
- Example factories provide deterministic comparison cases for demos and benchmarks.

Reasoning diffing compares summaries, confidence values, and reasoning event types only.

## Platform API

The FastAPI platform lives under `hallucination_replay.api`.

Create an app:

```python
from hallucination_replay.api import create_app

app = create_app()
```

Endpoints:

- `GET /health` — health check.
- `GET /version` — package/API version information.
- `GET /traces` — list stored trace IDs.
- `GET /traces/{run_id}` — load a trace.
- `POST /traces` — upload/persist a trace.
- `POST /replay/load` — create a replay session.
- `POST /replay/next` — advance replay.
- `POST /replay/previous` — rewind replay.
- `POST /replay/jump` — jump by step ID or step index.
- `POST /reconstruction/context` — reconstruct context.
- `POST /reconstruction/memory` — reconstruct memory.
- `POST /reconstruction/state` — reconstruct full state.
- `POST /analysis/run` and `GET /analysis/report` — run and fetch failure analysis.
- `POST /hallucination/run` and `GET /hallucination/report` — run and fetch hallucination analysis.
- `POST /compare` and `GET /compare/report` — compare traces and fetch comparison reports.

OpenAPI metadata and usage examples are documented in `docs/openapi.md`.

## Dashboard helpers

Dashboard helpers live under `hallucination_replay.dashboard`.

- `DashboardService` aggregates trace summaries, replay sessions, and stored reports.
- `render_timeline_viewer()` renders ordered replay steps.
- `render_replay_viewer()` renders current replay position, step, and snapshot metadata.
- `render_failure_analysis_viewer()` renders findings, root causes, and confidence scores.
- `render_hallucination_viewer()` renders unsupported claims, contradictions, and severity.

The dashboard layer intentionally emits simple deterministic HTML strings that can be embedded by a minimal web UI or documentation demo.
