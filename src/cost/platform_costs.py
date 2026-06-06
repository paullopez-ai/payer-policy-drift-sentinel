from __future__ import annotations

from src.contracts.cost import CostEstimate
from src.cost.token_meter import TokenMeter

# Configurable pricing - Paul must verify current pricing before live demo
PROMPT_TOKEN_PRICE_PER_1K = 0.005
COMPLETION_TOKEN_PRICE_PER_1K = 0.015
SNOWFLAKE_QUERY_COST_PROXY_USD = 0.02
DATABRICKS_JOB_COST_PROXY_USD = 0.10


def estimate_costs(
    meter: TokenMeter,
    snowflake_queries: int = 0,
    databricks_jobs: int = 0,
    admin_cost_avoided: float = 0.0,
) -> CostEstimate:
    """Build a cost estimate from token usage and platform queries."""
    cost = CostEstimate(
        prompt_tokens=meter.prompt_tokens,
        completion_tokens=meter.completion_tokens,
        estimated_llm_cost_usd=round(
            (meter.prompt_tokens / 1000) * PROMPT_TOKEN_PRICE_PER_1K
            + (meter.completion_tokens / 1000) * COMPLETION_TOKEN_PRICE_PER_1K,
            6,
        ),
        estimated_snowflake_cost_usd=round(
            snowflake_queries * SNOWFLAKE_QUERY_COST_PROXY_USD, 6
        ),
        estimated_databricks_cost_usd=round(
            databricks_jobs * DATABRICKS_JOB_COST_PROXY_USD, 6
        ),
        estimated_admin_cost_avoided_usd=round(admin_cost_avoided, 2),
    )
    cost.compute_total()
    return cost
