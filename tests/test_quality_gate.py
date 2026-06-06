"""Quality gate tests."""

from __future__ import annotations

import pytest

from src.contracts.cost import CostEstimate
from src.contracts.evidence_packet import Citation, EvidencePacket
from src.contracts.review import ReviewStatus, TrustBoundary
from src.workflow.nodes.quality_gate import quality_gate_node


def _make_packet(confidence: float = 0.8, citation_count: int = 2) -> EvidencePacket:
    citations = [
        Citation(
            citation_id=f"CIT-{i}",
            policy_version_id="PV-001",
            passage=f"Test passage {i}",
            relevance_score=0.9,
        )
        for i in range(citation_count)
    ]
    return EvidencePacket(
        packet_id="test-packet",
        finding_id="test-finding",
        scenario_id="test-scenario",
        summary="Test summary",
        root_cause_hypothesis="Test hypothesis",
        recommended_review_path="Test path",
        citations=citations,
        confidence=confidence,
        cost=CostEstimate(
            prompt_tokens=1000,
            completion_tokens=300,
            estimated_llm_cost_usd=0.01,
            total_estimated_cost_usd=0.05,
        ),
    )


@pytest.mark.asyncio
async def test_quality_gate_passes():
    state = {
        "evidence_packet": _make_packet(confidence=0.85, citation_count=2),
        "cost": CostEstimate(total_estimated_cost_usd=0.05),
    }
    result = await quality_gate_node(state)
    assert result["quality_passed"] is True
    assert result["quality_issues"] == []


@pytest.mark.asyncio
async def test_quality_gate_blocks_low_confidence():
    state = {
        "evidence_packet": _make_packet(confidence=0.3, citation_count=2),
        "cost": CostEstimate(total_estimated_cost_usd=0.05),
    }
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
    assert any("Confidence" in issue for issue in result["quality_issues"])


@pytest.mark.asyncio
async def test_quality_gate_blocks_no_citations():
    state = {
        "evidence_packet": _make_packet(confidence=0.8, citation_count=0),
        "cost": CostEstimate(total_estimated_cost_usd=0.05),
    }
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
    assert any("Citation" in issue for issue in result["quality_issues"])


@pytest.mark.asyncio
async def test_quality_gate_blocks_excessive_cost():
    state = {
        "evidence_packet": _make_packet(confidence=0.8, citation_count=2),
        "cost": CostEstimate(total_estimated_cost_usd=100.0),
    }
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
    assert any("cost" in issue.lower() for issue in result["quality_issues"])


@pytest.mark.asyncio
async def test_quality_gate_no_packet():
    state = {"evidence_packet": None, "cost": None}
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
