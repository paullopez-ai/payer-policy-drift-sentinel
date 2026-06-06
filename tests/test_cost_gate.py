"""Cost cap and token cap tests."""

from __future__ import annotations

import pytest

from src.contracts.cost import CostEstimate
from src.contracts.evidence_packet import Citation, EvidencePacket
from src.workflow.nodes.quality_gate import quality_gate_node


def _make_state(
    prompt_tokens: int = 1000,
    completion_tokens: int = 300,
    total_cost: float = 0.05,
) -> dict:
    packet = EvidencePacket(
        packet_id="test",
        finding_id="test",
        scenario_id="test",
        summary="Test",
        root_cause_hypothesis="Test",
        recommended_review_path="Test",
        citations=[
            Citation(
                citation_id="CIT-1",
                policy_version_id="PV-001",
                passage="Test",
                relevance_score=0.9,
            )
        ],
        confidence=0.85,
        cost=CostEstimate(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_llm_cost_usd=total_cost * 0.5,
            total_estimated_cost_usd=total_cost,
        ),
    )
    cost = CostEstimate(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_estimated_cost_usd=total_cost,
    )
    return {"evidence_packet": packet, "cost": cost}


@pytest.mark.asyncio
async def test_cost_within_budget():
    state = _make_state(total_cost=1.0)
    result = await quality_gate_node(state)
    assert result["quality_passed"] is True


@pytest.mark.asyncio
async def test_cost_exceeds_budget():
    state = _make_state(total_cost=100.0)
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
    assert any("cost" in issue.lower() for issue in result["quality_issues"])


@pytest.mark.asyncio
async def test_prompt_tokens_exceed_max():
    state = _make_state(prompt_tokens=50000)
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
    assert any("Prompt tokens" in issue for issue in result["quality_issues"])


@pytest.mark.asyncio
async def test_completion_tokens_exceed_max():
    state = _make_state(completion_tokens=50000)
    result = await quality_gate_node(state)
    assert result["quality_passed"] is False
    assert any("Completion tokens" in issue for issue in result["quality_issues"])
