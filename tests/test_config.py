from __future__ import annotations

from pytest import MonkeyPatch

from hallucination_replay.config import ReplaySettings, get_settings


def test_settings_defaults() -> None:
    settings = ReplaySettings()

    assert settings.app_name == "hallucination-replay-system"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.json_logs is False


def test_settings_load_from_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("HRS_ENVIRONMENT", "production")
    monkeypatch.setenv("HRS_LOG_LEVEL", "debug")
    monkeypatch.setenv("HRS_JSON_LOGS", "true")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.environment == "production"
    assert settings.log_level == "debug"
    assert settings.json_logs is True

    get_settings.cache_clear()
