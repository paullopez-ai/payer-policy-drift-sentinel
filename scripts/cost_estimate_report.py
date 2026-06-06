"""Prints run-level cost estimates.

Usage:
    uv run python scripts/cost_estimate_report.py
"""

from __future__ import annotations

from src.cost.platform_costs import (
    COMPLETION_TOKEN_PRICE_PER_1K,
    DATABRICKS_JOB_COST_PROXY_USD,
    PROMPT_TOKEN_PRICE_PER_1K,
    SNOWFLAKE_QUERY_COST_PROXY_USD,
    estimate_costs,
)
from src.cost.token_meter import TokenMeter


def main() -> None:
    print("=== Payer Policy Drift Sentinel - Cost Estimate Report ===\n")

    print("Pricing assumptions (verify before live demo):")
    print(f"  Prompt token price per 1K:     ${PROMPT_TOKEN_PRICE_PER_1K:.4f}")
    print(f"  Completion token price per 1K: ${COMPLETION_TOKEN_PRICE_PER_1K:.4f}")
    print(f"  Snowflake query proxy:         ${SNOWFLAKE_QUERY_COST_PROXY_USD:.4f}")
    print(f"  Databricks job proxy:          ${DATABRICKS_JOB_COST_PROXY_USD:.4f}")
    print()

    # Typical scenario run
    meter = TokenMeter()
    meter.record(prompt_tokens=2400, completion_tokens=380)

    cost = estimate_costs(
        meter=meter,
        snowflake_queries=3,
        databricks_jobs=1,
        admin_cost_avoided=5000.0,
    )

    print("Typical scenario run (denial-spike-imaging):")
    print(f"  Prompt tokens:              {cost.prompt_tokens}")
    print(f"  Completion tokens:          {cost.completion_tokens}")
    print(f"  Estimated LLM cost:         ${cost.estimated_llm_cost_usd:.4f}")
    print(f"  Estimated Snowflake cost:   ${cost.estimated_snowflake_cost_usd:.4f}")
    print(f"  Estimated Databricks cost:  ${cost.estimated_databricks_cost_usd:.4f}")
    print(f"  Estimated platform cost:    ${cost.estimated_platform_cost_usd:.4f}")
    print(f"  Total estimated cost:       ${cost.total_estimated_cost_usd:.4f}")
    print(f"  Admin cost avoided:         ${cost.estimated_admin_cost_avoided_usd:,.2f}")
    print()

    # 4-scenario demo session
    total_cost = cost.total_estimated_cost_usd * 4
    print(f"Full demo session (4 scenarios): ~${total_cost:.2f}")
    print()
    print("NOTE: These are synthetic cost proxies. Verify current pricing")
    print("for Azure OpenAI, Snowflake, and Databricks before live demo.")


if __name__ == "__main__":
    main()
