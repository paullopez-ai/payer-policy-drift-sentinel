from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from src.audit.hashing import compute_input_hash
from src.clients.azure_openai_client import AzureOpenAIClientBase
from src.context.context_builder import ContextBuilder
from src.contracts.evidence_packet import Citation, EvidencePacket
from src.contracts.workflow_state import WorkflowState
from src.cost.platform_costs import estimate_costs
from src.cost.token_meter import TokenMeter
from src.prompts.evidence_packet_prompt import build_evidence_prompt

logger = logging.getLogger(__name__)


async def evidence_packet_node(
    state: WorkflowState,
    openai_client: AzureOpenAIClientBase,
) -> WorkflowState:
    """Generates cited evidence packet using Azure OpenAI."""
    findings = state.get("findings", [])
    if not findings:
        state["error"] = "No findings available for evidence generation"
        return state

    primary_finding = findings[0]
    policy_passages = state.get("policy_passages", [])
    financial_impact = state.get("financial_impact", {})

    context_builder = ContextBuilder()
    context = context_builder.build(primary_finding, policy_passages, financial_impact)

    input_hash = compute_input_hash(context)
    prompt = build_evidence_prompt(context)

    response = await openai_client.generate_evidence(prompt)

    content_str = response["content"]
    try:
        parsed = json.loads(content_str)
    except json.JSONDecodeError:
        state["error"] = "Failed to parse evidence packet JSON from model response"
        return state

    meter = TokenMeter()
    meter.record(response.get("prompt_tokens", 0), response.get("completion_tokens", 0))

    # Build citations from passages that were referenced
    citations_used = set(parsed.get("citations_used", []))
    citations = []
    for passage in policy_passages:
        cit_id = passage.get("citation_id", "")
        pv_id = passage.get("policy_version_id", "")
        # Match by exact citation ID or by policy version prefix in any referenced citation
        matched = cit_id in citations_used or any(
            pv_id in ref_cit for ref_cit in citations_used
        )
        if matched:
            citations.append(
                Citation(
                    citation_id=cit_id,
                    policy_version_id=pv_id,
                    passage=passage.get("passage", ""),
                    relevance_score=passage.get("relevance_score", 0.0),
                )
            )

    cost = estimate_costs(
        meter=meter,
        snowflake_queries=3,
        databricks_jobs=1,
        admin_cost_avoided=financial_impact.get("admin_cost_estimate", 0.0),
    )

    packet = EvidencePacket(
        packet_id=str(uuid.uuid4()),
        finding_id=primary_finding.finding_id,
        scenario_id=state["scenario_id"],
        summary=parsed.get("summary", ""),
        root_cause_hypothesis=parsed.get("root_cause_hypothesis", ""),
        recommended_review_path=parsed.get("recommended_review_path", ""),
        citations=citations,
        confidence=float(parsed.get("confidence", 0.0)),
        limitations=parsed.get("limitations", []),
        input_hash=input_hash,
        model_provider=response.get("model_deployment", "MOCK"),
        model_deployment=response.get("model_deployment", ""),
        cost=cost,
        created_at=datetime.now(timezone.utc),
    )

    state["evidence_packet"] = packet
    state["cost"] = cost

    logger.info(
        "Evidence packet created: packet_id=%s, confidence=%.2f, citations=%d",
        packet.packet_id,
        packet.confidence,
        packet.citation_count,
    )

    return state
