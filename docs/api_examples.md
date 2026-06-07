# API Usage Examples

These examples assume the FastAPI application is running locally:

```bash
uvicorn hallucination_replay.api:create_app --factory --reload
```

The examples use `benchmarks/hallucination/contradiction.json` as a deterministic trace fixture. Replace run IDs, step indexes, and file paths with your own trace data when debugging real runs.

## Health and version

```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
```

## Trace upload and lookup

Upload a trace:

```bash
curl -X POST http://localhost:8000/traces \
  -H 'content-type: application/json' \
  --data @benchmarks/hallucination/contradiction.json
```

List traces:

```bash
curl http://localhost:8000/traces
```

Fetch a trace by run ID:

```bash
curl http://localhost:8000/traces/hallucination-contradiction
```

## Replay calls

Create a replay session for a trace:

```bash
curl -X POST http://localhost:8000/replay/sessions \
  -H 'content-type: application/json' \
  -d '{"run_id":"hallucination-contradiction"}'
```

Inspect the replay state:

```bash
curl http://localhost:8000/replay/sessions/<session_id>
```

Move forward one replay step:

```bash
curl -X POST http://localhost:8000/replay/sessions/<session_id>/next
```

Move backward one replay step:

```bash
curl -X POST http://localhost:8000/replay/sessions/<session_id>/previous
```

Jump to a deterministic step index:

```bash
curl -X POST http://localhost:8000/replay/sessions/<session_id>/jump \
  -H 'content-type: application/json' \
  -d '{"step_index":3}'
```

## Reconstruction calls

Reconstruct agent-visible state for a run and step:

```bash
curl 'http://localhost:8000/reconstruction/state/hallucination-contradiction?step_index=3'
```

Reconstruct context only:

```bash
curl 'http://localhost:8000/reconstruction/context/hallucination-contradiction?step_index=3'
```

Reconstruct memory only:

```bash
curl 'http://localhost:8000/reconstruction/memory/hallucination-contradiction?step_index=3'
```

## Failure analysis calls

Run full failure analysis for a trace step:

```bash
curl -X POST http://localhost:8000/analysis/run \
  -H 'content-type: application/json' \
  -d '{"run_id":"hallucination-contradiction","step_index":3,"report_id":"demo-analysis"}'
```

Fetch a generated analysis report:

```bash
curl http://localhost:8000/analysis/reports/demo-analysis
```

## Hallucination calls

Run deterministic hallucination analysis:

```bash
curl -X POST http://localhost:8000/hallucination/run \
  -H 'content-type: application/json' \
  -d '{"run_id":"hallucination-contradiction","step_index":3,"report_id":"demo-hallucination"}'
```

Fetch a hallucination report:

```bash
curl http://localhost:8000/hallucination/reports/demo-hallucination
```

## Comparison calls

Compare two traces:

```bash
curl -X POST http://localhost:8000/comparison/run \
  -H 'content-type: application/json' \
  -d '{
    "baseline_run_id":"baseline-run",
    "candidate_run_id":"candidate-run",
    "report_id":"demo-comparison"
  }'
```

Fetch the comparison report:

```bash
curl http://localhost:8000/comparison/reports/demo-comparison
```

## Error handling

Missing traces return `404` responses with the missing run ID in the response detail. Replay jump requests must include either `step_id` or `step_index`; requests with neither field return `422`.
