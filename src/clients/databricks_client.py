from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class DatabricksClientBase(ABC):
    """Abstract base for Databricks interactions."""

    @abstractmethod
    async def run_job(self, job_id: str, wait: bool = True) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_sql(self, sql: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_drift_findings(self, scenario_id: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_policy_retrieval(self, procedure_group: str) -> list[dict[str, Any]]:
        ...
