from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_validation_script() -> ModuleType:
    """Load the repository validation script from its file path."""
    script_path = Path.cwd() / "scripts" / "validate_repo.py"
    spec = importlib.util.spec_from_file_location("validate_repo", script_path)
    if spec is None or spec.loader is None:
        message = "Could not load validate_repo.py"
        raise AssertionError(message)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_paths_reports_missing_files(tmp_path: Path) -> None:
    script = load_validation_script()
    (tmp_path / "present.md").write_text("ok", encoding="utf-8")

    assert script.validate_paths(tmp_path, ["present.md", "missing.md"]) == [
        "missing.md"
    ]


def test_validate_readme_sections_reports_missing_sections(tmp_path: Path) -> None:
    script = load_validation_script()
    (tmp_path / "README.md").write_text(
        "# Hallucination Replay System\n", encoding="utf-8"
    )

    missing = script.validate_readme_sections(tmp_path, script.REQUIRED_README_SECTIONS)

    assert "## Capability matrix" in missing


def test_collect_validation_errors_passes_for_repository() -> None:
    script = load_validation_script()

    assert script.collect_validation_errors(Path.cwd()) == []
