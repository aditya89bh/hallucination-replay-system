# OpenAPI Usage Guide

The FastAPI application exposes deterministic debugging workflows for trace replay,
state reconstruction, failure analysis, hallucination analysis, and execution comparison.

## Endpoint documentation

- `GET /health` — API health check.
- `GET /version` — package and API version.
- `GET /traces` — list stored traces.
- `GET /traces/{run_id}` — load a stored trace by run ID.
- `POST /traces` — create or replace a stored trace.
- `POST /replay/load` — create a replay session for a stored trace.
- `POST /replay/next` — advance a replay session.
- `POST /replay/previous` — move a replay session backward.
- `POST /replay/jump` — jump to a replay step index or step ID.
- `POST /reconstruction/context` — reconstruct context at a step.
- `POST /reconstruction/memory` — reconstruct memory at a step.
- `POST /reconstruction/state` — reconstruct full execution state at a step.
- `POST /analysis/run` — run deterministic failure analysis.
- `GET /analysis/report` — retrieve a failure analysis report by report ID.
- `POST /hallucination/run` — run deterministic hallucination analysis.
- `GET /hallucination/report` — retrieve a hallucination report by report ID.
- `POST /compare` — compare two stored executions.
- `GET /compare/report` — retrieve a comparison report by report ID.

## Schema examples

```json
{
  "run_id": "example-run",
  "started_at": "2026-01-01T00:00:00Z",
  "status": "completed",
  "metadata": {
    "steps": [
      {
        "step_id": "s1",
        "step_index": 1,
        "step_type": "model",
        "timestamp": "2026-01-01T00:00:01Z",
        "description": "Generated answer"
      }
    ],
    "outputs": [{"step_index": 1, "content": "The account is active."}]
  }
}
```

```json
{"run_id": "example-run", "session_id": "debug-session"}
```

```json
{"run_a_id": "baseline-run", "run_b_id": "candidate-run", "report_id": "comparison-1"}
```

## Usage examples

```bash
curl -X POST http://localhost:8000/traces \
  -H 'content-type: application/json' \
  --data @trace.json

curl -X POST http://localhost:8000/replay/load \
  -H 'content-type: application/json' \
  -d '{"run_id":"example-run","session_id":"debug-session"}'

curl -X POST http://localhost:8000/reconstruction/state \
  -H 'content-type: application/json' \
  -d '{"run_id":"example-run","step_index":1}'

curl -X POST http://localhost:8000/analysis/run \
  -H 'content-type: application/json' \
  -d '{"run_id":"example-run","step_index":1,"report_id":"analysis-1"}'
```
