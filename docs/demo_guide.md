# Demo Guide

This guide walks through a practical demo of the replay, analysis, hallucination, comparison, API, and dashboard capabilities. Commands assume you are in the repository root with development dependencies installed.

## 1. Prepare the environment

```bash
python -m pip install -e ".[dev]"
```

Run the core quality gate if you want to verify the checkout first:

```bash
pytest
ruff check .
mypy .
```

## 2. Use example and benchmark traces

Useful demo inputs live in:

- `benchmarks/hallucination/*.json` — compact hallucination scenarios.
- `examples/diffing/*.json` — execution comparison scenarios.
- `examples/reconstruction/*.md` — documented reconstruction examples.

The hallucination benchmark traces are valid `RunTrace` JSON files and are the easiest starting point for API demos.

## 3. Replay a trace

Replay commands require traces with `metadata["steps"]`. To inspect replay behavior from tests or custom traces, run:

```bash
python -m hallucination_replay.replay.cli load trace.json
python -m hallucination_replay.replay.cli timeline trace.json
python -m hallucination_replay.replay.cli jump trace.json --index 1
```

The CLI prints deterministic JSON. Use the timeline output to identify step IDs and indexes before jumping.

## 4. Run failure analysis

Failure analysis can be invoked from Python or through the FastAPI app.

Python sketch:

```python
from hallucination_replay.analysis import (
    analyze_output_failures,
    generate_failure_markdown_report,
)
from hallucination_replay.models import RunTrace

trace = RunTrace.from_json(open("trace.json", encoding="utf-8").read())
findings = analyze_output_failures(trace, step_index=1)
print(generate_failure_markdown_report(findings))
```

The analysis package also includes analyzers for intent, retrieval, memory, tools, validation, and reasoning.

## 5. Run hallucination detection

Use the benchmark fixtures for a deterministic demo:

```bash
pytest tests/test_hallucination_evaluation.py tests/test_hallucination_integration.py
```

Python sketch:

```python
from hallucination_replay.hallucination import (
    detect_contradictions,
    detect_unsupported_claims,
    extract_claims_from_outputs,
    extract_evidence,
    match_claims_to_evidence,
)
from hallucination_replay.models import RunTrace

trace = RunTrace.from_json(open("benchmarks/hallucination/contradiction.json", encoding="utf-8").read())
claims = extract_claims_from_outputs(trace.metadata["outputs"])
evidence = extract_evidence(trace, step_index=3)
matches = match_claims_to_evidence(claims, evidence)
print(detect_unsupported_claims(matches))
print(detect_contradictions(claims, evidence))
```

Detection is deterministic and does not call an LLM.

## 6. Compare executions

Run the deterministic comparison benchmark:

```bash
python benchmarks/comparison/comparison_benchmark.py
cat benchmarks/comparison/summary.json
```

Or use the Python API:

```python
from hallucination_replay.diffing import compare_executions
from hallucination_replay.diffing.examples import successful_vs_failed_runs

run_a, run_b = successful_vs_failed_runs()
comparison = compare_executions(run_a, run_b)
print(comparison.to_json())
```

## 7. Use the FastAPI platform

Start the API app with any ASGI server. For example, if `uvicorn` is installed locally:

```bash
uvicorn hallucination_replay.api:create_app --factory --reload
```

Core endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/traces
```

Upload a trace:

```bash
curl -X POST http://localhost:8000/traces \
  -H 'content-type: application/json' \
  --data @benchmarks/hallucination/contradiction.json
```

Run hallucination analysis:

```bash
curl -X POST http://localhost:8000/hallucination/run \
  -H 'content-type: application/json' \
  -d '{"run_id":"hallucination-contradiction","step_index":3,"report_id":"demo-hallucination"}'
```

Fetch the report:

```bash
curl 'http://localhost:8000/hallucination/report?report_id=demo-hallucination'
```

See `docs/openapi.md` for the full endpoint list and payload examples.

## 8. Use dashboard helpers

The dashboard package renders deterministic HTML snippets that can be embedded in an internal UI or printed during demos.

```python
from hallucination_replay.dashboard import render_hallucination_viewer
from hallucination_replay.hallucination import HallucinationSeverity

html = render_hallucination_viewer([], [], HallucinationSeverity.LOW)
print(html)
```

Available helpers render timelines, replay state, failure findings, and hallucination findings.

## 9. Generate reports

Report helpers are available for:

- Failure analysis: Markdown and JSON.
- Hallucination analysis: Markdown and JSON.
- Execution comparison: Markdown and JSON.

Reports are deterministic and suitable for CI artifacts, pull request comments, notebooks, or internal incident reviews.

## 10. Suggested live demo script

1. Show the README capability matrix and architecture diagram.
2. Run `pytest --cov` to show release quality.
3. Upload `benchmarks/hallucination/contradiction.json` to the API.
4. Run `/hallucination/run` and inspect unsupported/contradiction output.
5. Run the comparison benchmark and show `summary.json`.
6. Render a dashboard helper in a Python shell.
7. Close by showing `docs/production_readiness.md` and current known gaps.
