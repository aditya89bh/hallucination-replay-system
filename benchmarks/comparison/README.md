# Comparison Benchmarks

`comparison_benchmark.py` measures deterministic Phase 8 work units for:

- diff generation (`diff_sections`, `total_change_count`)
- markdown report generation (`markdown_report_lines`)
- JSON report generation (`json_report_bytes`)

The benchmark intentionally avoids wall-clock timing so output remains deterministic in CI.
