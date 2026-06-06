from __future__ import annotations

import logging

from src.clients.azure_openai_client import AzureOpenAIClientBase
from src.clients.databricks_client import DatabricksClientBase
from src.clients.snowflake_client import SnowflakeClientBase
from src.contracts.workflow_state import WorkflowState
from src.workflow.nodes.data_readiness import data_readiness_node
from src.workflow.nodes.drift_detection import drift_detection_node
from src.workflow.nodes.evidence_packet import evidence_packet_node
from src.workflow.nodes.financial_impact import financial_impact_node
from src.workflow.nodes.human_review import human_review_node
from src.workflow.nodes.policy_retrieval import policy_retrieval_node
from src.workflow.nodes.quality_gate import quality_gate_node
from src.workflow.state import create_initial_state

logger = logging.getLogger(__name__)


class DriftSentinelWorkflow:
    """Orchestrates the drift detection workflow through sequential nodes."""

    def __init__(
        self,
        snowflake_client: SnowflakeClientBase,
        databricks_client: DatabricksClientBase,
        openai_client: AzureOpenAIClientBase,
    ) -> None:
        self.snowflake_client = snowflake_client
        self.databricks_client = databricks_client
        self.openai_client = openai_client

    async def run(self, scenario_id: str) -> WorkflowState:
        """Execute the full drift sentinel workflow for a scenario."""
        state = create_initial_state(scenario_id)

        logger.info("Starting workflow for scenario %s, run %s", scenario_id, state["run_id"])

        # Node 1: Data Readiness
        state = await data_readiness_node(state, self.snowflake_client)
        if not state.get("data_ready"):
            state["error"] = "Data readiness check failed"
            return state

        # Node 2: Drift Detection
        state = await drift_detection_node(state, self.databricks_client)
        if not state.get("findings"):
            state["error"] = "No drift findings detected"
            return state

        # Node 3: Policy Retrieval
        state = await policy_retrieval_node(state, self.databricks_client)

        # Node 4: Financial Impact
        state = await financial_impact_node(state, self.snowflake_client)

        # Node 5: Evidence Packet
        state = await evidence_packet_node(state, self.openai_client)
        if state.get("error"):
            return state

        # Node 6: Quality Gate
        state = await quality_gate_node(state)

        # Node 7: Human Review
        state = await human_review_node(state)

        logger.info(
            "Workflow complete for scenario %s: quality=%s, review=%s",
            scenario_id,
            state.get("quality_passed"),
            state.get("review_status", "UNKNOWN"),
        )

        return state
