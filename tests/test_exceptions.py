from __future__ import annotations

from hallucination_replay.exceptions import (
    AnalysisError,
    HallucinationReplayError,
    ReplayError,
    StorageError,
)


def test_domain_exceptions_share_base_type() -> None:
    assert issubclass(StorageError, HallucinationReplayError)
    assert issubclass(ReplayError, HallucinationReplayError)
    assert issubclass(AnalysisError, HallucinationReplayError)
