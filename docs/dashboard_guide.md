# Dashboard Walkthrough Guide

The dashboard package provides lightweight, deterministic HTML renderers for local debugging and demos. It is intentionally server-side and minimal: the dashboard helpers format replay and analysis data without adding a large JavaScript frontend or external service dependency.

## When to use the dashboard

Use the dashboard helpers when you want to:

- inspect a replay timeline visually;
- show the current replay position and step details;
- review failure analysis findings in a compact page;
- review hallucination findings, evidence matches, and severity output;
- embed deterministic HTML in internal tools or notebooks.

For API-first workflows, use the FastAPI endpoints documented in [API usage examples](api_examples.md). For CLI workflows, see [CLI reference](cli_reference.md).

## Dashboard service

The `DashboardService` coordinates trace loading and renderer calls.

```python
from hallucination_replay.dashboard import DashboardService
from hallucination_replay.storage import FilesystemTraceRepository

repository = FilesystemTraceRepository(".traces")
dashboard = DashboardService(repository)

html = dashboard.render_timeline("example-run")
```

The service is designed for trusted local or internal environments. It does not add authentication, authorization, or multi-tenant isolation.

## Timeline viewer

The timeline viewer summarizes ordered replay steps and helps identify where a failure happened.

Typical use:

```python
html = dashboard.render_timeline("example-run")
```

Use it to inspect:

- step indexes and identifiers;
- step types;
- deterministic ordering;
- high-level timeline structure;
- the position of retrieval, memory, tool, reasoning, validation, and output events.

Recommended workflow:

1. Load a trace into the repository.
2. Render the timeline.
3. Identify suspicious step indexes.
4. Use replay or reconstruction views for the relevant step.

## Replay viewer

The replay viewer presents current replay state, navigation position, and step details.

Typical use:

```python
html = dashboard.render_replay("example-run", step_index=3)
```

Use it to inspect:

- current step information;
- prior and next step context;
- replay navigation state;
- snapshot-friendly state for debugging discussions.

Recommended workflow:

1. Start from the timeline viewer.
2. Choose a step index near the failure.
3. Render replay state for that step.
4. Compare with reconstruction output if the failure depends on agent-visible state.

## Failure viewer

The failure viewer formats deterministic failure analysis results into a readable debugging page.

Typical use:

```python
html = dashboard.render_failure_analysis("example-run", step_index=3)
```

Use it to inspect:

- failure findings;
- failure taxonomy categories;
- confidence scores;
- contributing factors;
- root-cause ranking;
- short and detailed summaries.

Recommended workflow:

1. Reconstruct state at the failure step.
2. Run failure analysis.
3. Review top-ranked causes first.
4. Use lower-ranked findings as supporting context, not final proof.

## Hallucination viewer

The hallucination viewer formats claim, evidence, contradiction, unsupported-claim, severity, and scoring output.

Typical use:

```python
html = dashboard.render_hallucination("example-run", step_index=3)
```

Use it to inspect:

- extracted claims;
- available evidence;
- claim/evidence matches;
- unsupported claims;
- contradiction findings;
- coverage and severity scores.

Recommended workflow:

1. Identify the model output step.
2. Review extracted claims.
3. Check whether each claim has supporting evidence.
4. Review contradictions separately from unsupported claims.
5. Treat the output as deterministic debugging evidence, not an LLM judgment.

## Operational notes

- Dashboard renderers do not call external LLMs.
- Inputs should be sanitized before rendering if traces contain private data.
- The dashboard is not a hosted multi-user observability UI.
- For deployed environments, put any dashboard route behind your own authentication and access controls.
- For incident reports, export Markdown or JSON reports alongside dashboard HTML so findings remain reproducible.
