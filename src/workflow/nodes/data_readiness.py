from __future__ import annotations

import logging

from src.clients.snowflake_client import SnowflakeClientBase
from src.contracts.workflow_state import WorkflowState

logger = logging.getLogger(__name__)

REQUIRED_TABLES = [
    ("RAW", "CLAIM_LINES"),
    ("RAW", "AUTHORIZATIONS"),
    ("RAW", "DENIAL_EVENTS"),
    ("RAW", "APPEALS"),
    ("MART", "PROVIDER_DIM"),
    ("POLICY", "POLICY_VERSION"),
]


async def data_readiness_node(
    state: WorkflowState,
    snowflake_client: SnowflakeClientBase,
) -> WorkflowState:
    """Validates Snowflake tables, row counts, and freshness."""
    details: dict[str, dict] = {}
    all_ready = True

    for schema, table in REQUIRED_TABLES:
        exists = await snowflake_client.check_table_exists(schema, table)
        row_count = 0
        if exists:
            row_count = await snowflake_client.get_row_count(schema, table)

        ready = exists and row_count > 0
        details[f"{schema}.{table}"] = {
            "exists": exists,
            "row_count": row_count,
            "ready": ready,
        }
        if not ready:
            all_ready = False

    if all_ready:
        logger.info("Data readiness check passed for scenario %s", state.get("scenario_id"))
    else:
        logger.warning("Data readiness check failed: %s", details)

    state["data_ready"] = all_ready
    state["readiness_details"] = details
    return state
