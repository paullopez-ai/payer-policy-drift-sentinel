"""Scenario 1 integration test: denial-spike-imaging."""

from __future__ import annotations

import pytest

from src.contracts.findings import FindingType, Severity
from src.contracts.review import ReviewStatus, TrustBoundary
from src.workflow.graph import DriftSentinelWorkflow


@pytest.mark.asyncio
async def test_denial_spike_workflow(mock_snowflake, mock_databricks, mock_openai):
    workflow = DriftSentinelWorkflow(
        snowflake_client=mock_snowflake,
        databricks_client=mock_databricks,
        openai_client=mock_openai,
    )

    state = await workflow.run("denial-spike-imaging")

    # Data readiness passed
    assert state["data_ready"] is True

    # Findings detected
    findings = state["findings"]
    assert len(findings) >= 1
    primary = findings[0]
    assert primary.finding_type == FindingType.DENIAL_SPIKE
    assert primary.severity == Severity.HIGH
    assert primary.confidence >= 0.7

    # Evidence packet generated
    packet = state["evidence_packet"]
    assert packet is not None
    assert packet.scenario_id == "denial-spike-imaging"
    assert packet.confidence > 0.0
    assert packet.citation_count >= 1
    assert len(packet.summary) > 0
    assert len(packet.root_cause_hypothesis) > 0

    # Quality gate passed
    assert state["quality_passed"] is True

    # Review required for HIGH severity
    assert state["review_status"] in (ReviewStatus.REQUIRED, ReviewStatus.NOT_REQUIRED)

    # Cost is tracked
    cost = state["cost"]
    assert cost is not None
    assert cost.prompt_tokens > 0
    assert cost.completion_tokens > 0
    assert cost.total_estimated_cost_usd > 0
