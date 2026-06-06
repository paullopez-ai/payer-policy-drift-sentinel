"""Dependency failure tests."""

from __future__ import annotations

from typing import Any

import pytest

from src.clients.azure_openai_client import AzureOpenAIClientBase
from src.clients.databricks_client import DatabricksClientBase
from src.clients.mock_clients import MockAzureOpenAIClient, MockDatabricksClient, MockSnowflakeClient
from src.clients.snowflake_client import SnowflakeClientBase
from src.workflow.graph import DriftSentinelWorkflow


class FailingSnowflakeClient(SnowflakeClientBase):
    async def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        raise TimeoutError("Snowflake query timeout")

    async def write_rows(self, table: str, rows: list[dict[str, Any]]) -> int:
        raise TimeoutError("Snowflake write timeout")

    async def check_table_exists(self, schema: str, table: str) -> bool:
        raise ConnectionError("Snowflake unavailable")

    async def get_row_count(self, schema: str, table: str) -> int:
        raise ConnectionError("Snowflake unavailable")


class FailingDatabricksClient(DatabricksClientBase):
    async def run_job(self, job_id: str, wait: bool = True) -> dict[str, Any]:
        raise TimeoutError("Databricks job timeout")

    async def query_sql(self, sql: str) -> list[dict[str, Any]]:
        raise ConnectionError("Databricks unavailable")

    async def get_drift_findings(self, scenario_id: str) -> list[dict[str, Any]]:
        raise ConnectionError("Databricks unavailable")

    async def get_policy_retrieval(self, procedure_group: str) -> list[dict[str, Any]]:
        raise ConnectionError("Databricks unavailable")


class BadJsonOpenAIClient(AzureOpenAIClientBase):
    async def generate_evidence(self, prompt: str, max_tokens: int = 1800) -> dict[str, Any]:
        return {
            "content": "This is not valid JSON at all!!!",
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "model_deployment": "mock",
        }


@pytest.mark.asyncio
async def test_snowflake_unavailable():
    workflow = DriftSentinelWorkflow(
        snowflake_client=FailingSnowflakeClient(),
        databricks_client=MockDatabricksClient(),
        openai_client=MockAzureOpenAIClient(),
    )
    with pytest.raises(ConnectionError):
        await workflow.run("denial-spike-imaging")


@pytest.mark.asyncio
async def test_databricks_unavailable():
    workflow = DriftSentinelWorkflow(
        snowflake_client=MockSnowflakeClient(),
        databricks_client=FailingDatabricksClient(),
        openai_client=MockAzureOpenAIClient(),
    )
    with pytest.raises(ConnectionError):
        await workflow.run("denial-spike-imaging")


@pytest.mark.asyncio
async def test_openai_bad_json():
    workflow = DriftSentinelWorkflow(
        snowflake_client=MockSnowflakeClient(),
        databricks_client=MockDatabricksClient(),
        openai_client=BadJsonOpenAIClient(),
    )
    state = await workflow.run("denial-spike-imaging")
    assert state.get("error") is not None
    assert "JSON" in state["error"]
