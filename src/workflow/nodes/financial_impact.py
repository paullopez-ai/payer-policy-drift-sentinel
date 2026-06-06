from __future__ import annotations

import logging

from src.clients.snowflake_client import SnowflakeClientBase
from src.contracts.workflow_state import FinancialImpact, WorkflowState

logger = logging.getLogger(__name__)


async def financial_impact_node(
    state: WorkflowState,
    snowflake_client: SnowflakeClientBase,
) -> WorkflowState:
    """Queries Snowflake for claim volume, denied dollars, appeal reversals, admin cost."""
    findings = state.get("findings", [])
    if not findings:
        state["financial_impact"] = FinancialImpact()
        return state

    primary_finding = findings[0]
    scenario_id = state["scenario_id"]

    # Query denial amounts
    denial_rows = await snowflake_client.query(
        "SELECT SUM(denied_amount) as total_denied, COUNT(*) as denial_count "
        "FROM RAW.DENIAL_EVENTS WHERE procedure_group = :procedure_group",
        params={"procedure_group": primary_finding.procedure_group, "scenario_id": scenario_id},
    )

    # Query appeal reversals
    appeal_rows = await snowflake_client.query(
        "SELECT SUM(admin_cost_estimate) as total_admin_cost, "
        "COUNT(*) as reversal_count FROM RAW.APPEALS "
        "WHERE appeal_outcome = 'OVERTURNED'",
        params={"scenario_id": scenario_id},
    )

    # Query claim volume
    claim_rows = await snowflake_client.query(
        "SELECT COUNT(*) as claim_volume FROM RAW.CLAIM_LINES "
        "WHERE procedure_group = :procedure_group",
        params={"procedure_group": primary_finding.procedure_group, "scenario_id": scenario_id},
    )

    denied_dollars = 0.0
    claim_volume = 0
    admin_cost = 0.0
    reversal_dollars = 0.0

    if denial_rows:
        denied_dollars = float(denial_rows[0].get("total_denied", 0) or 0)
    if claim_rows:
        claim_volume = int(claim_rows[0].get("claim_volume", 0) or 0)
    if appeal_rows:
        admin_cost = float(appeal_rows[0].get("total_admin_cost", 0) or 0)
        reversal_dollars = admin_cost * 0.6  # proxy

    exposure = denied_dollars + admin_cost

    impact = FinancialImpact(
        denied_dollars=denied_dollars,
        appeal_reversal_dollars=reversal_dollars,
        admin_cost_estimate=admin_cost,
        claim_volume=claim_volume,
        exposure_estimate=exposure,
    )

    logger.info(
        "Financial impact for %s: denied=$%.2f, claims=%d, exposure=$%.2f",
        scenario_id,
        denied_dollars,
        claim_volume,
        exposure,
    )

    state["financial_impact"] = impact
    return state
