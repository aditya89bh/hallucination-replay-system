from __future__ import annotations

import logging

from hallucination_replay.logging import configure_logging, get_logger


def test_configure_logging_sets_root_level() -> None:
    configure_logging(log_level="debug")

    assert logging.getLogger().level == logging.DEBUG


def test_get_logger_returns_bound_logger() -> None:
    logger = get_logger("hallucination_replay.tests")

    assert logger is not None
