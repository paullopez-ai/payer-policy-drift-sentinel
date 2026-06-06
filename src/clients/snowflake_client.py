from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class SnowflakeClientBase(ABC):
    """Abstract base for Snowflake interactions."""

    @abstractmethod
    async def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def write_rows(self, table: str, rows: list[dict[str, Any]]) -> int:
        ...

    @abstractmethod
    async def check_table_exists(self, schema: str, table: str) -> bool:
        ...

    @abstractmethod
    async def get_row_count(self, schema: str, table: str) -> int:
        ...
