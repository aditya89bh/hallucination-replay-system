from __future__ import annotations

import hallucination_replay


def test_package_imports() -> None:
    assert hallucination_replay.__doc__


def test_version_is_exported() -> None:
    assert hallucination_replay.__version__ == "0.1.0"
