"""Application configuration models."""

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration with sensible defaults for local development."""

    app_name: str = "agentic-ai-dashboard"
    environment: str = "development"
    log_level: str = "INFO"
