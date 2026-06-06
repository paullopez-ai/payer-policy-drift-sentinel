from __future__ import annotations

import logging

from src.clients.databricks_client import DatabricksClientBase
from src.contracts.workflow_state import PolicyPassage, WorkflowState
from src.retrieval.policy_index import PolicyIndex

logger = logging.getLogger(__name__)


async def policy_retrieval_node(
    state: WorkflowState,
    databricks_client: DatabricksClientBase,
) -> WorkflowState:
    """Retrieves policy passages and citation metadata for detected findings."""
    findings = state.get("findings", [])
    if not findings:
        state["policy_passages"] = []
        return state

    primary_finding = findings[0]
    procedure_group = primary_finding.procedure_group

    raw_passages = await databricks_client.get_policy_retrieval(procedure_group)

    index = PolicyIndex()
    for raw in raw_passages:
        index.add_passage(
            policy_version_id=raw["policy_version_id"],
            passage=raw["passage"],
            relevance_score=float(raw.get("relevance_score", 0.8)),
        )

    top_passages = index.top_k(5)
    logger.info(
        "Retrieved %d policy passages for procedure group %s",
        len(top_passages),
        procedure_group,
    )

    state["policy_passages"] = top_passages
    return state
