# Limitations and Non-Goals

This project is a deterministic replay and debugging toolkit for AI agent traces. It is production-quality for local, CI, and trusted internal debugging workflows, but it is not a complete hosted observability product.

## Current limitations

### Trace quality determines analysis quality

The system can only replay, reconstruct, analyze, and compare what was captured in the trace. Missing prompts, retrieval results, tool outputs, memory events, validation decisions, or metadata can lead to incomplete findings.

### Deterministic analysis is intentionally conservative

Hallucination detection uses deterministic claim/evidence matching and contradiction rules. It does not ask an LLM to judge whether an answer is correct. This keeps results reproducible, but nuanced semantic equivalence may require human review.

### Reasoning analysis avoids chain-of-thought inference

Reasoning reconstruction and diffing work with summaries, confidence, and event types. The project does not reconstruct hidden chain-of-thought and does not infer private reasoning text.

### Local filesystem storage is the primary backend

The current storage layer is suitable for local, CI, and internal trusted workflows. It is not a horizontally scalable trace lake or distributed ingestion service.

### Dashboard is intentionally lightweight

The dashboard helpers render deterministic HTML views. They are not a full collaborative browser application with users, comments, saved investigations, or real-time updates.

### API authentication is out of scope for core package

The FastAPI app is designed to be embedded behind your own deployment controls. Built-in authentication, authorization, tenant isolation, and rate limiting are not included in the core package.

### Benchmark traces are synthetic fixtures

Included benchmark traces are deterministic and useful for regression checks, but they are not a substitute for evaluating the tool on sanitized traces from your own agent stack.

## Unsupported scenarios

- Hosted multi-tenant SaaS operation without external access controls.
- Direct ingestion of unredacted sensitive production traces.
- Reconstructing data that was never captured.
- Proving factual correctness beyond the available evidence.
- Inferring hidden chain-of-thought.
- Replacing human incident review for high-impact failures.
- Running non-deterministic LLM-based detection inside the release quality gate.

## Non-goals

The v1.0.0 release does not aim to provide:

- a hosted observability platform;
- a large JavaScript dashboard;
- built-in user management;
- database-backed report storage;
- distributed ingestion workers;
- vendor-specific agent SDK integrations;
- automatic remediation or self-healing;
- LLM-as-judge hallucination detection;
- private reasoning or chain-of-thought extraction.

## Future work

Future releases may add:

- additional storage backends;
- richer dashboard workflows;
- more trace import adapters;
- deployment templates with authentication guidance;
- larger benchmark suites;
- sanitized real-world example traces;
- expanded comparison and regression reporting;
- optional hosted-service integration points.

## Recommended release use

Use v1.0.0 for:

- local trace debugging;
- CI regression checks over deterministic fixtures;
- internal incident review with sanitized traces;
- reproducing and explaining agent failures;
- comparing successful and failed executions;
- documenting failure analysis in Markdown or JSON reports.

Do not expose the API or dashboard to untrusted users without wrapping it in your own security layer.
