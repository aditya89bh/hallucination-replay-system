from __future__ import annotations

import importlib.util
import tarfile
import zipfile
from pathlib import Path
from types import ModuleType


def load_artifact_script() -> ModuleType:
    """Load the release artifact verification script from its file path."""
    script_path = Path.cwd() / "scripts" / "verify_release_artifacts.py"
    spec = importlib.util.spec_from_file_location(
        "verify_release_artifacts", script_path
    )
    if spec is None or spec.loader is None:
        message = "Could not load verify_release_artifacts.py"
        raise AssertionError(message)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_wheel(path: Path, version: str, required_members: list[str]) -> None:
    metadata = (
        "Metadata-Version: 2.4\n"
        "Name: hallucination-replay-system\n"
        f"Version: {version}\n"
        "Summary: Replay AI agent execution traces.\n"
    )
    with zipfile.ZipFile(path, "w") as archive:
        for member in required_members:
            archive.writestr(member, "")
        archive.writestr(
            f"hallucination_replay_system-{version}.dist-info/METADATA", metadata
        )


def write_sdist(path: Path, required_members: list[str]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for member in required_members:
            file_path = path.parent / member.replace("/", "_")
            file_path.write_text("content", encoding="utf-8")
            archive.add(file_path, arcname=f"pkg-1.0.0rc1/{member}")


def test_missing_required_members_reports_absent_items() -> None:
    script = load_artifact_script()

    missing = script.missing_required_members(
        {"present.py"}, ["present.py", "missing.py"]
    )

    assert missing == ["missing.py"]


def test_wheel_metadata_reads_name_version_and_summary(tmp_path: Path) -> None:
    script = load_artifact_script()
    wheel_path = tmp_path / "hallucination_replay_system-1.0.0rc1-py3-none-any.whl"
    write_wheel(wheel_path, "1.0.0rc1", script.REQUIRED_WHEEL_MEMBERS)

    assert script.wheel_metadata(wheel_path) == {
        "Name": "hallucination-replay-system",
        "Version": "1.0.0rc1",
        "Summary": "Replay AI agent execution traces.",
    }


def test_verify_artifacts_passes_for_expected_files(tmp_path: Path) -> None:
    script = load_artifact_script()
    write_wheel(
        tmp_path / "hallucination_replay_system-1.0.0rc1-py3-none-any.whl",
        "1.0.0rc1",
        script.REQUIRED_WHEEL_MEMBERS,
    )
    write_sdist(
        tmp_path / "hallucination_replay_system-1.0.0rc1.tar.gz",
        script.REQUIRED_SDIST_MEMBERS,
    )

    assert script.verify_artifacts(tmp_path, "1.0.0rc1") == []
