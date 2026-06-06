from __future__ import annotations

import logging
from datetime import date

from src.clients.databricks_client import DatabricksClientBase
from src.contracts.findings import DriftFinding, FindingStatus, FindingType, Severity
from src.contracts.workflow_state import WorkflowState

logger = logging.getLogger(__name__)


def _parse_finding(raw: dict) -> DriftFinding:
    return DriftFinding(
        finding_id=raw["finding_id"],
        scenario_id=raw["scenario_id"],
        finding_type=FindingType(raw["finding_type"]),
        detection_date=date.fromisoformat(raw["detection_date"])
        if isinstance(raw["detection_date"], str)
        else raw["detection_date"],
        procedure_group=raw["procedure_group"],
        provider_id=raw.get("provider_id"),
        baseline_rate=float(raw["baseline_rate"]),
        observed_rate=float(raw["observed_rate"]),
        delta=float(raw["delta"]),
        severity=Severity(raw["severity"]),
        confidence=float(raw["confidence"]),
        policy_version_id=raw["policy_version_id"],
        status=FindingStatus(raw.get("status", "NEW")),
    )


async def drift_detection_node(
    state: WorkflowState,
    databricks_client: DatabricksClientBase,
) -> WorkflowState:
    """Detects drift by reading Databricks output or triggering a job."""
    scenario_id = state["scenario_id"]

    raw_findings = await databricks_client.get_drift_findings(scenario_id)

    if not raw_findings:
        logger.warning("No drift findings for scenario %s", scenario_id)
        state["findings"] = []
        return state

    findings = [_parse_finding(f) for f in raw_findings]
    logger.info("Detected %d drift findings for scenario %s", len(findings), scenario_id)

    state["findings"] = findings
    return state
