"""Tests for default configuration values."""

from packages.common import AppConfig


def test_config_loads_defaults() -> None:
    cfg = AppConfig()

    assert cfg.app_name == "agentic-ai-dashboard"
    assert cfg.environment == "development"
    assert cfg.log_level == "INFO"
