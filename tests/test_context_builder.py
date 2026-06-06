"""Scoped context tests."""

from __future__ import annotations

from datetime import date

from src.context.context_builder import ContextBuilder
from src.contracts.findings import DriftFinding, FindingType, Severity
from src.contracts.workflow_state import FinancialImpact, PolicyPassage


def test_context_builder_scopes_to_finding():
    builder = ContextBuilder()

    finding = DriftFinding(
        finding_id="test-finding",
        scenario_id="test-scenario",
        finding_type=FindingType.DENIAL_SPIKE,
        detection_date=date(2024, 9, 15),
        procedure_group="advanced_imaging",
        baseline_rate=0.08,
        observed_rate=0.23,
        delta=0.15,
        severity=Severity.HIGH,
        confidence=0.87,
        policy_version_id="PV-001",
    )

    passages: list[PolicyPassage] = [
        {
            "citation_id": "CIT-001",
            "policy_version_id": "PV-001",
            "passage": "Test policy passage",
            "relevance_score": 0.9,
        }
    ]

    impact: FinancialImpact = {
        "denied_dollars": 50000.0,
        "appeal_reversal_dollars": 12000.0,
        "admin_cost_estimate": 5000.0,
        "claim_volume": 200,
        "exposure_estimate": 55000.0,
    }

    context = builder.build(finding, passages, impact)

    assert context["finding"]["finding_id"] == "test-finding"
    assert context["finding"]["finding_type"] == "DENIAL_SPIKE"
    assert len(context["policy_passages"]) == 1
    assert context["policy_passages"][0]["citation_id"] == "CIT-001"
    assert context["financial_impact"]["denied_dollars"] == 50000.0


def test_context_builder_empty_passages():
    builder = ContextBuilder()

    finding = DriftFinding(
        finding_id="test",
        scenario_id="test",
        finding_type=FindingType.DENIAL_SPIKE,
        detection_date=date(2024, 9, 15),
        procedure_group="advanced_imaging",
        baseline_rate=0.08,
        observed_rate=0.23,
        delta=0.15,
        severity=Severity.HIGH,
        confidence=0.87,
        policy_version_id="PV-001",
    )

    context = builder.build(finding, [], {})
    assert context["policy_passages"] == []
