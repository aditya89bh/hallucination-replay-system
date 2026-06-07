# Production Readiness Guide

`hallucination-replay-system` is approaching a v1.0.0 release candidate as a deterministic debugging and analysis toolkit for AI agent traces. This guide explains what is ready, where the boundaries are, and how to operate the project safely.

## Current maturity

The project is suitable for:

- Local and CI-based replay of captured agent traces.
- Deterministic reconstruction of execution state from trace metadata.
- Root-cause style failure analysis over trace events.
- Rule-based hallucination analysis against available evidence.
- Execution comparison and regression review.
- Lightweight FastAPI debugging workflows.
- Open-source evaluation, demos, and integration prototypes.

The project is not yet a hosted multi-tenant observability service. It does not provide authentication, authorization, long-term managed storage, distributed ingestion, or a fully styled production dashboard.

## Safe use cases

Recommended production-adjacent uses:

- Run as an internal developer tool on trusted traces.
- Use in CI to replay fixture traces and detect deterministic regressions.
- Analyze sanitized traces from staging or production incidents.
- Generate failure, hallucination, and comparison reports for engineering review.
- Build custom internal dashboards on top of the FastAPI app or Python modules.

Use extra caution when traces contain customer data, secrets, private prompts, or sensitive tool outputs.

## Limitations

Known limitations:

- Detection logic is deterministic and heuristic. It can miss subtle hallucinations or flag benign wording differences.
- The system does not call LLMs for detection, grading, or interpretation.
- Reconstruction depends on trace completeness and metadata quality.
- Reasoning reconstruction intentionally exposes summaries, confidence, and event types only; it does not inspect or infer chain-of-thought.
- The default filesystem repository is simple and best suited to local or single-process workflows.
- FastAPI report storage is in application state by default, so generated reports are process-local unless callers persist responses externally.
- The dashboard layer renders lightweight deterministic HTML helpers rather than a full web application.

## Scaling notes

For larger deployments:

- Store traces on durable storage with backup and retention policies.
- Partition trace directories or implement a repository backend suited to your storage layer.
- Keep benchmark traces small and representative for CI.
- Run expensive batch analysis out of request paths when trace volume grows.
- Treat comparison and reconstruction APIs as CPU-bound operations on trace payloads.
- Cache generated reports externally if they need to survive process restarts.
- Prefer immutable trace IDs for reproducible analysis and auditability.

## Security considerations

Trace files may include sensitive data. Before using the project with real incidents:

- Redact secrets, credentials, tokens, and personal data from trace metadata.
- Restrict filesystem permissions on trace storage directories.
- Run the FastAPI application behind trusted network controls.
- Add authentication and authorization before exposing APIs outside a trusted environment.
- Validate uploaded trace sizes and retention policies in any hosted integration.
- Avoid storing raw chain-of-thought or hidden reasoning in traces.
- Review generated reports before sharing them externally.

The repository intentionally avoids external LLM calls in detection logic, which helps keep analysis deterministic and prevents trace data from leaving the process unexpectedly.

## Operational checklist

Before running in an internal production-like environment:

1. Install from a pinned release candidate or commit SHA.
2. Run the release validation gate:

   ```bash
   pytest --cov
   ruff check .
   mypy .
   python -m build
   ```

3. Confirm trace retention and redaction policies.
4. Configure the trace repository path on durable storage.
5. Put the FastAPI app behind internal authentication if exposed over a network.
6. Capture logs from the hosting process.
7. Document expected trace schemas for agent teams.
8. Keep benchmark fixtures representative of known failure modes.

## Known gaps

The following are intentionally outside the current release scope:

- Managed user accounts and permissions.
- Hosted ingestion service.
- Database-backed report storage.
- Rich browser dashboard with live collaboration.
- Automatic remediation or autonomous production actions.
- LLM-based hallucination judging.
- v1.0.0 release tagging and publishing.

These gaps should be addressed explicitly in future phases or downstream integrations rather than assumed to be present in the core package.
