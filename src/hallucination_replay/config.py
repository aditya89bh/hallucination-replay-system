"""Environment-based application configuration."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["development", "test", "staging", "production"]


class ReplaySettings(BaseSettings):
    """Runtime settings for the hallucination replay system."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="HRS_",
        extra="ignore",
    )

    app_name: str = Field(default="hallucination-replay-system")
    environment: EnvironmentName = Field(default="development")
    log_level: str = Field(default="INFO")
    json_logs: bool = Field(default=False)


@lru_cache(maxsize=1)
def get_settings() -> ReplaySettings:
    """Return cached settings loaded from the process environment."""
    return ReplaySettings()
