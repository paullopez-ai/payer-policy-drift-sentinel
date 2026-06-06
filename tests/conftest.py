from __future__ import annotations

import os

import pytest

# Enforce mock mode for all tests
os.environ["MOCK_LLM"] = "true"
os.environ["EXTERNAL_CLIENT_MODE"] = "mock"
os.environ["APP_ENV"] = "test"

from src.clients.mock_clients import (
    MockAzureOpenAIClient,
    MockDatabricksClient,
    MockSnowflakeClient,
)
from src.config.modes import require_mock_for_tests

require_mock_for_tests()


@pytest.fixture
def mock_snowflake():
    return MockSnowflakeClient()


@pytest.fixture
def mock_databricks():
    return MockDatabricksClient()


@pytest.fixture
def mock_openai():
    return MockAzureOpenAIClient(scenario_id="denial-spike-imaging")


@pytest.fixture
def mock_openai_appeal():
    return MockAzureOpenAIClient(scenario_id="appeal-reversal-leakage")


@pytest.fixture
def mock_openai_provider():
    return MockAzureOpenAIClient(scenario_id="provider-outlier-friction")


@pytest.fixture
def mock_openai_policy():
    return MockAzureOpenAIClient(scenario_id="policy-version-regression")
