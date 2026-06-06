"""Ensures tests never call cloud services."""

from __future__ import annotations

import os


def test_mock_llm_is_true():
    assert os.environ.get("MOCK_LLM") == "true", "Tests must run with MOCK_LLM=true"


def test_external_client_mode_is_mock():
    assert os.environ.get("EXTERNAL_CLIENT_MODE") == "mock", (
        "Tests must run with EXTERNAL_CLIENT_MODE=mock"
    )


def test_settings_report_mock():
    from src.config.settings import settings
    assert settings.is_mock, "Settings must report mock mode during tests"
    assert not settings.is_live, "Settings must not report live mode during tests"
