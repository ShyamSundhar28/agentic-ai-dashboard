"""Tests for logging configuration helpers."""

import logging

from packages.common import configure_logging, get_logger


def test_logger_initializes_without_error() -> None:
    configure_logging("debug")
    logger = get_logger("tests.logger")

    assert isinstance(logger, logging.Logger)
    logger.info("logger initialized")
