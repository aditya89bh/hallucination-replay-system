from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_repo = load_script_module("validate_repo", ROOT / "scripts" / "validate_repo.py")
verify_release_artifacts = load_script_module(
    "verify_release_artifacts",
    ROOT / "scripts" / "verify_release_artifacts.py",
)


def test_release_validation_import_roots_are_complete() -> None:
    expected_imports = {
        "hallucination_replay",
        "hallucination_replay.models",
        "hallucination_replay.storage",
        "hallucination_replay.replay",
        "hallucination_replay.reconstruction",
        "hallucination_replay.analysis",
        "hallucination_replay.hallucination",
        "hallucination_replay.diffing",
        "hallucination_replay.api",
        "hallucination_replay.dashboard",
    }

    assert expected_imports.issubset(set(validate_repo.REQUIRED_IMPORTS))
    assert validate_repo.validate_imports(validate_repo.REQUIRED_IMPORTS) == []


def test_release_validation_required_docs_exist() -> None:
    missing = validate_repo.validate_paths(ROOT, validate_repo.REQUIRED_DOCS)

    assert missing == []


def test_release_artifact_member_expectations_cover_public_packages() -> None:
    required_wheel_roots = {
        "hallucination_replay/__init__.py",
        "hallucination_replay/models/__init__.py",
        "hallucination_replay/storage/__init__.py",
        "hallucination_replay/replay/__init__.py",
        "hallucination_replay/reconstruction/__init__.py",
        "hallucination_replay/analysis/__init__.py",
        "hallucination_replay/hallucination/__init__.py",
        "hallucination_replay/diffing/__init__.py",
        "hallucination_replay/api/__init__.py",
        "hallucination_replay/dashboard/__init__.py",
    }

    assert required_wheel_roots.issubset(
        set(verify_release_artifacts.REQUIRED_WHEEL_MEMBERS)
    )
    assert (
        "tests/test_package_import_smoke.py"
        in verify_release_artifacts.REQUIRED_SDIST_MEMBERS
    )
