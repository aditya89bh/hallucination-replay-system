"""Validate release-candidate repository structure and presentation."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

REQUIRED_DOCS = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "docs/architecture.md",
    "docs/api_reference.md",
    "docs/benchmarks.md",
    "docs/cli_reference.md",
    "docs/demo_guide.md",
    "docs/development.md",
    "docs/openapi.md",
    "docs/production_readiness.md",
    "docs/trace_schema.md",
    "docs/assets/architecture.mmd",
]

REQUIRED_IMPORTS = [
    "hallucination_replay",
    "hallucination_replay.analysis",
    "hallucination_replay.api",
    "hallucination_replay.dashboard",
    "hallucination_replay.diffing",
    "hallucination_replay.hallucination",
    "hallucination_replay.models",
    "hallucination_replay.reconstruction",
    "hallucination_replay.replay",
    "hallucination_replay.storage",
]

REQUIRED_BENCHMARKS = [
    "benchmarks/storage_benchmark.py",
    "benchmarks/replay_benchmark.py",
    "benchmarks/hallucination/unsupported_claim.json",
    "benchmarks/hallucination/contradiction.json",
    "benchmarks/hallucination/partially_supported_claim.json",
    "benchmarks/hallucination/fully_supported_claim.json",
    "benchmarks/comparison/comparison_benchmark.py",
    "benchmarks/comparison/summary.json",
]

REQUIRED_README_SECTIONS = [
    "# Hallucination Replay System",
    "## Why this exists",
    "## Capability matrix",
    "## Architecture overview",
    "## Quickstart",
    "## Demo workflow",
    "## Benchmark summary",
    "## Production readiness note",
    "## Roadmap",
]


def validate_paths(root: Path, paths: list[str]) -> list[str]:
    """Return missing required paths under root."""
    return [path for path in paths if not (root / path).exists()]


def validate_imports(import_names: list[str]) -> list[str]:
    """Return import names that fail to import."""
    failures: list[str] = []
    for import_name in import_names:
        try:
            importlib.import_module(import_name)
        except ImportError:
            failures.append(import_name)
    return failures


def validate_readme_sections(root: Path, sections: list[str]) -> list[str]:
    """Return README sections that are absent."""
    readme = (root / "README.md").read_text(encoding="utf-8")
    return [section for section in sections if section not in readme]


def collect_validation_errors(root: Path) -> list[str]:
    """Collect release-candidate repository validation errors."""
    errors: list[str] = []
    missing_docs = validate_paths(root, REQUIRED_DOCS)
    missing_benchmarks = validate_paths(root, REQUIRED_BENCHMARKS)
    failed_imports = validate_imports(REQUIRED_IMPORTS)
    missing_sections = validate_readme_sections(root, REQUIRED_README_SECTIONS)

    errors.extend(f"missing required document: {path}" for path in missing_docs)
    errors.extend(f"missing required benchmark: {path}" for path in missing_benchmarks)
    errors.extend(f"failed package import: {name}" for name in failed_imports)
    errors.extend(f"missing README section: {section}" for section in missing_sections)
    return errors


def main() -> int:
    """Run repository validation and print a concise report."""
    root = Path(__file__).resolve().parents[1]
    errors = collect_validation_errors(root)
    if errors:
        for error in errors:
            sys.stderr.write(f"ERROR: {error}\n")
        return 1
    sys.stdout.write("Repository validation passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
