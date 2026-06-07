"""Verify built release artifacts before publishing."""

from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path

PACKAGE_NAME = "hallucination-replay-system"
IMPORT_ROOT = "hallucination_replay"
REQUIRED_WHEEL_MEMBERS = [
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
]
REQUIRED_SDIST_MEMBERS = [
    "README.md",
    "pyproject.toml",
    "src/hallucination_replay/__init__.py",
    "tests/test_package_import_smoke.py",
]


def wheel_members(wheel_path: Path) -> set[str]:
    """Return normalized member names from a wheel file."""
    with zipfile.ZipFile(wheel_path) as archive:
        return set(archive.namelist())


def sdist_members(sdist_path: Path) -> set[str]:
    """Return source distribution members without the top-level directory."""
    with tarfile.open(sdist_path, "r:gz") as archive:
        members: set[str] = set()
        for member in archive.getnames():
            parts = Path(member).parts
            if len(parts) > 1:
                members.add(str(Path(*parts[1:])))
        return members


def wheel_metadata(wheel_path: Path) -> dict[str, str]:
    """Read package metadata from a wheel file."""
    with zipfile.ZipFile(wheel_path) as archive:
        metadata_names = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            return {}
        content = archive.read(metadata_names[0]).decode("utf-8")
    parsed = Parser().parsestr(content)
    return {key: parsed.get(key, "") for key in ["Name", "Version", "Summary"]}


def missing_required_members(members: set[str], required: list[str]) -> list[str]:
    """Return required artifact members absent from a member listing."""
    return [member for member in required if member not in members]


def verify_artifacts(dist_dir: Path, expected_version: str) -> list[str]:
    """Return release artifact verification errors."""
    wheel_path = (
        dist_dir / f"hallucination_replay_system-{expected_version}-py3-none-any.whl"
    )
    sdist_path = dist_dir / f"hallucination_replay_system-{expected_version}.tar.gz"
    errors: list[str] = []

    if not wheel_path.exists():
        errors.append(f"missing wheel: {wheel_path.name}")
    if not sdist_path.exists():
        errors.append(f"missing sdist: {sdist_path.name}")
    if errors:
        return errors

    metadata = wheel_metadata(wheel_path)
    if metadata.get("Name") != PACKAGE_NAME:
        errors.append(f"unexpected package name: {metadata.get('Name', '<missing>')}")
    if metadata.get("Version") != expected_version:
        errors.append(
            f"unexpected package version: {metadata.get('Version', '<missing>')}"
        )
    if not metadata.get("Summary"):
        errors.append("missing package summary")

    missing_wheel = missing_required_members(
        wheel_members(wheel_path), REQUIRED_WHEEL_MEMBERS
    )
    missing_sdist = missing_required_members(
        sdist_members(sdist_path), REQUIRED_SDIST_MEMBERS
    )
    errors.extend(f"wheel missing member: {member}" for member in missing_wheel)
    errors.extend(f"sdist missing member: {member}" for member in missing_sdist)
    return errors


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Verify release artifacts in dist/.")
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--version", required=True)
    return parser.parse_args()


def main() -> int:
    """Run release artifact verification."""
    args = parse_args()
    errors = verify_artifacts(args.dist_dir, args.version)
    if errors:
        for error in errors:
            sys.stderr.write(f"ERROR: {error}\n")
        return 1
    sys.stdout.write("Release artifact verification passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
