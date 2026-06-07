from __future__ import annotations

from pathlib import Path

import pytest

from hallucination_replay.exceptions import StorageError
from hallucination_replay.storage import compress_trace_file, decompress_trace_file


def test_compress_and_decompress_trace_file(tmp_path: Path) -> None:
    trace_path = tmp_path / "run-1.json"
    trace_path.write_text('{"run_id":"run-1"}\n', encoding="utf-8")

    compressed_path = compress_trace_file(trace_path)
    restored_path = decompress_trace_file(compressed_path, tmp_path / "restored.json")

    assert compressed_path == tmp_path / "run-1.json.gz"
    assert compressed_path.exists()
    assert restored_path.read_text(encoding="utf-8") == trace_path.read_text(
        encoding="utf-8"
    )


def test_compress_trace_file_accepts_target_path(tmp_path: Path) -> None:
    trace_path = tmp_path / "run-1.json"
    target_path = tmp_path / "archive" / "run-1.gz"
    trace_path.write_text("{}\n", encoding="utf-8")

    result_path = compress_trace_file(trace_path, target_path)

    assert result_path == target_path
    assert target_path.exists()


def test_compression_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(StorageError, match="not found"):
        compress_trace_file(tmp_path / "missing.json")
