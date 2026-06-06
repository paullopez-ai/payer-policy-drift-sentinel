from __future__ import annotations

from pydantic import BaseModel


class CostEstimate(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_llm_cost_usd: float = 0.0
    estimated_snowflake_cost_usd: float = 0.0
    estimated_databricks_cost_usd: float = 0.0
    estimated_platform_cost_usd: float = 0.0
    estimated_admin_cost_avoided_usd: float = 0.0
    total_estimated_cost_usd: float = 0.0

    def compute_total(self) -> None:
        self.estimated_platform_cost_usd = (
            self.estimated_snowflake_cost_usd + self.estimated_databricks_cost_usd
        )
        self.total_estimated_cost_usd = (
            self.estimated_llm_cost_usd + self.estimated_platform_cost_usd
        )
