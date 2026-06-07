"""Opt-in gzip compression utilities for trace JSON files."""

from __future__ import annotations

import gzip
import shutil
from pathlib import Path

from hallucination_replay.exceptions import StorageError

GZIP_SUFFIX = ".gz"


def compress_trace_file(source_path: Path, target_path: Path | None = None) -> Path:
    """Compress a trace JSON file with gzip and return the output path."""
    if not source_path.exists():
        message = f"Trace file not found for compression: {source_path}"
        raise StorageError(message)
    output_path = target_path or source_path.with_suffix(
        source_path.suffix + GZIP_SUFFIX
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        source_path.open("rb") as source_file,
        gzip.open(output_path, "wb") as target_file,
    ):
        shutil.copyfileobj(source_file, target_file)
    return output_path


def decompress_trace_file(source_path: Path, target_path: Path | None = None) -> Path:
    """Decompress a gzip-compressed trace JSON file and return the output path."""
    if not source_path.exists():
        message = f"Trace file not found for decompression: {source_path}"
        raise StorageError(message)
    output_path = target_path or _default_decompressed_path(source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        gzip.open(source_path, "rb") as source_file,
        output_path.open("wb") as target_file,
    ):
        shutil.copyfileobj(source_file, target_file)
    return output_path


def _default_decompressed_path(source_path: Path) -> Path:
    """Return the default path for a decompressed gzip file."""
    if source_path.suffix == GZIP_SUFFIX:
        return source_path.with_suffix("")
    return source_path.with_name(f"{source_path.name}.decompressed")
