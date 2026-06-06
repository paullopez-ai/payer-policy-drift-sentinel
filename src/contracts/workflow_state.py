from __future__ import annotations

from typing import Any, TypedDict

from src.contracts.cost import CostEstimate
from src.contracts.evidence_packet import EvidencePacket
from src.contracts.findings import DriftFinding
from src.contracts.review import ReviewStatus, TrustBoundary


class PolicyPassage(TypedDict, total=False):
    citation_id: str
    policy_version_id: str
    passage: str
    relevance_score: float


class FinancialImpact(TypedDict, total=False):
    denied_dollars: float
    appeal_reversal_dollars: float
    admin_cost_estimate: float
    claim_volume: int
    exposure_estimate: float


class WorkflowState(TypedDict, total=False):
    # Input
    scenario_id: str
    run_id: str

    # DataReadinessNode output
    data_ready: bool
    readiness_details: dict[str, Any]

    # DriftDetectionNode output
    findings: list[DriftFinding]

    # PolicyRetrievalNode output
    policy_passages: list[PolicyPassage]

    # FinancialImpactNode output
    financial_impact: FinancialImpact

    # EvidencePackNode output
    evidence_packet: EvidencePacket

    # QualityGateNode output
    quality_passed: bool
    quality_issues: list[str]

    # Trust and review
    trust_boundary: TrustBoundary
    review_status: ReviewStatus

    # Cost
    cost: CostEstimate

    # Errors
    error: str | None
