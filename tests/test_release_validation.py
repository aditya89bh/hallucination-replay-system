from __future__ import annotations

from scripts.validate_repo import (
    REQUIRED_DOCS,
    REQUIRED_IMPORTS,
    validate_imports,
    validate_paths,
)
from scripts.verify_release_artifacts import (
    REQUIRED_SDIST_MEMBERS,
    REQUIRED_WHEEL_MEMBERS,
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

    assert expected_imports.issubset(set(REQUIRED_IMPORTS))
    assert validate_imports(REQUIRED_IMPORTS) == []


def test_release_validation_required_docs_exist() -> None:
    missing = validate_paths(root=__import__("pathlib").Path.cwd(), paths=REQUIRED_DOCS)

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

    assert required_wheel_roots.issubset(set(REQUIRED_WHEEL_MEMBERS))
    assert "tests/test_package_import_smoke.py" in REQUIRED_SDIST_MEMBERS
