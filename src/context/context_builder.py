from __future__ import annotations

from typing import Any

from src.contracts.findings import DriftFinding
from src.contracts.workflow_state import FinancialImpact, PolicyPassage


class ContextBuilder:
    """Builds scoped prompt context for evidence packet generation."""

    def build(
        self,
        finding: DriftFinding,
        policy_passages: list[PolicyPassage],
        financial_impact: FinancialImpact,
    ) -> dict[str, Any]:
        return {
            "finding": {
                "finding_id": finding.finding_id,
                "finding_type": finding.finding_type.value,
                "procedure_group": finding.procedure_group,
                "provider_id": finding.provider_id,
                "baseline_rate": finding.baseline_rate,
                "observed_rate": finding.observed_rate,
                "delta": finding.delta,
                "severity": finding.severity.value,
                "confidence": finding.confidence,
                "policy_version_id": finding.policy_version_id,
            },
            "policy_passages": [
                {
                    "citation_id": p.get("citation_id", ""),
                    "policy_version_id": p.get("policy_version_id", ""),
                    "passage": p.get("passage", ""),
                    "relevance_score": p.get("relevance_score", 0.0),
                }
                for p in policy_passages
            ],
            "financial_impact": dict(financial_impact),
        }
