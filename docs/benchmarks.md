# Benchmark Guide

The repository keeps benchmarks lightweight, deterministic where practical, and easy to run locally. They are intended to show relative behavior during development rather than publish hardware-independent throughput claims.

## Setup

Install the package in editable development mode before running benchmarks:

```bash
python -m pip install -e ".[dev]"
```

Run commands from the repository root so benchmark modules can find package code and fixture files.

## Storage benchmarks

Storage benchmarks exercise the filesystem trace repository and metadata index.

```bash
python benchmarks/storage_benchmark.py
```

The JSON output includes:

- `trace_count` — number of synthetic traces written and read.
- `save_seconds` — wall-clock time to persist all traces.
- `load_seconds` — wall-clock time to reload all traces by run ID.
- `list_seconds` — wall-clock time to list stored run IDs.
- `search_seconds` — wall-clock time to search indexed tags.
- `listed_count` / `search_result_count` — correctness checks for benchmark scope.

Interpret storage timings as local smoke signals. Disk, filesystem cache, and machine load will affect absolute values.

## Replay benchmarks

Replay benchmarks exercise trace loading, bidirectional navigation, snapshot creation, and timeline export.

```bash
python benchmarks/replay_benchmark.py
```

The JSON output includes:

- `step_count` — number of generated replay steps.
- `load_seconds` — time to create a replay controller.
- `navigation_seconds` — time to move forward through all steps and back to the beginning.
- `snapshot_seconds` — time to create a replay snapshot.
- `timeline_seconds` — time to export replay timeline metadata.
- `snapshot_position` and `timeline_step_count` — correctness checks for the replay workflow.

Replay timing is most useful for comparing changes in navigation or snapshot internals over time.

## Hallucination benchmarks

Hallucination benchmark traces live in `benchmarks/hallucination/` and cover deterministic detection cases:

- `unsupported_claim.json`
- `contradiction.json`
- `partially_supported_claim.json`
- `fully_supported_claim.json`

These fixtures are used by the hallucination evaluation suite and API integration tests. To run the benchmark-style evaluation, use pytest:

```bash
pytest tests/test_hallucination_evaluation.py tests/test_hallucination_integration.py
```

Interpret the results as detector behavior checks:

- Unsupported claims should be found when evidence is absent or too weak.
- Contradictions should be found when claims conflict with tool or memory evidence.
- Fully supported claims should keep severity low.
- Coverage scores summarize how well extracted claims map to available evidence.
- Each fixture declares `expected_support_coverage_min` and `expected_support_coverage_max` metadata so coverage thresholds are explicit and deterministic.

Current support-coverage thresholds:

| Fixture | Expected coverage | Purpose |
| --- | --- | --- |
| `unsupported_claim.json` | `0.0` | No captured evidence supports the claim. |
| `contradiction.json` | `1.0` | The claim maps to evidence but conflicts with it. |
| `partially_supported_claim.json` | `0.5` | One claim is supported and one timing claim is unsupported. |
| `fully_supported_claim.json` | `1.0` | All extracted claims are supported by evidence. |

The evaluation suite reports a threshold pass rate in addition to detection, contradiction, and aggregate coverage metrics.

## Comparison benchmarks

Comparison benchmarks measure deterministic work units for Phase 8 diffing and reporting.

```bash
python benchmarks/comparison/comparison_benchmark.py
```

The command refreshes `benchmarks/comparison/summary.json` with deterministic metrics for:

- `memory_regression`
- `retrieval_regression`
- `successful_vs_failed`

Each case reports:

- `diff_sections` — number of comparison sections emitted.
- `total_change_count` — aggregate count of detected changes.
- `markdown_report_lines` — rendered Markdown report size.
- `json_report_bytes` — JSON report size.

Because these metrics avoid wall-clock timing, they are stable enough to track in version control.

## Recommended release benchmark pass

Before a release candidate, run:

```bash
python benchmarks/storage_benchmark.py
python benchmarks/replay_benchmark.py
python benchmarks/comparison/comparison_benchmark.py
pytest tests/test_hallucination_evaluation.py tests/test_hallucination_integration.py
```

Review output for large unexpected changes. Update checked-in deterministic summaries only when behavior changes are intentional.
